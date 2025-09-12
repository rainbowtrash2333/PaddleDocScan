"""
文件处理工具模块
提供PDF和图片文件的处理功能
"""
from typing import List, Optional, Tuple, Union, Dict, Any
import os
import uuid
import base64
import tempfile
from pathlib import Path
import logging
import fitz  # PyMuPDF
from PIL import Image
import io

from .exceptions import FileProcessingError, UnsupportedFileError


class FileProcessor:
    """文件处理基类"""

    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = True  # 允许向上级 logger 传递到 root logger

    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """
        检查文件是否为允许的格式
        
        Args:
            filename: 文件名
            
        Returns:
            是否为允许的格式
        """
        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in cls.ALLOWED_EXTENSIONS)

    @classmethod
    def get_file_extension(cls, filename: str) -> str:
        """
        获取文件扩展名
        
        Args:
            filename: 文件名
            
        Returns:
            文件扩展名（小写）
        """
        if '.' not in filename:
            raise FileProcessingError("文件名没有扩展名")
        return filename.rsplit('.', 1)[1].lower()

    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """
        验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            
        Returns:
            是否在允许范围内
        """
        return file_size <= cls.MAX_FILE_SIZE

    @classmethod
    def generate_unique_filename(cls, original_filename: str) -> str:
        """
        生成唯一文件名
        
        Args:
            original_filename: 原始文件名
            
        Returns:
            唯一文件名
        """
        ext = cls.get_file_extension(original_filename)
        return f"{uuid.uuid4().hex}_{original_filename}"


class PDFProcessor(FileProcessor):
    """PDF文件处理器"""

    def convert_to_images(self, pdf_path: str, dpi: int = 200) -> List[bytes]:
        if not os.path.exists(pdf_path):
            raise FileProcessingError(f"PDF文件不存在: {pdf_path}")

        images = []
        doc = None
        try:
            doc = fitz.open(pdf_path)
            self.logger.info(f"PDF文件包含 {len(doc)} 页")

            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    mat = fitz.Matrix(dpi / 72, dpi / 72)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    images.append(img_data)
                    self.logger.debug(f"第 {page_num + 1} 页转换完成")
                except Exception as e:
                    self.logger.error(f"第 {page_num + 1} 页转换失败: {e}")
                    continue  # 跳过坏页，继续下一页

            return images

        except Exception as e:
            raise FileProcessingError(f"PDF转换失败: {e}")
        finally:
            if doc:
                doc.close()

    def get_first_page_image(self, pdf_path: str, dpi: int = 150) -> bytes:
        """
        获取PDF第一页图片用于预览
        
        Args:
            pdf_path: PDF文件路径
            dpi: 图片分辨率
            
        Returns:
            第一页图片字节数据
        """
        if not os.path.exists(pdf_path):
            raise FileProcessingError(f"PDF文件不存在: {pdf_path}")

        doc = None
        try:
            doc = fitz.open(pdf_path)
            if len(doc) == 0:
                raise FileProcessingError("PDF文件没有页面")

            page = doc.load_page(0)
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)
            return pix.tobytes("png")

        except Exception as e:
            raise FileProcessingError(f"获取PDF预览失败: {e}")
        finally:
            if doc:
                doc.close()

    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        获取PDF文件信息
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            PDF文件信息
        """
        if not os.path.exists(pdf_path):
            raise FileProcessingError(f"PDF文件不存在: {pdf_path}")

        doc = None
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata

            return {
                'page_count': len(doc),
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'created': metadata.get('creationDate', ''),
                'modified': metadata.get('modDate', '')
            }

        except Exception as e:
            raise FileProcessingError(f"获取PDF信息失败: {e}")
        finally:
            if doc:
                doc.close()


class ImageProcessor(FileProcessor):
    """图片文件处理器"""

    def validate_image(self, image_path: str) -> bool:
        """
        验证图片文件是否有效
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            是否为有效图片
        """
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            self.logger.error(f"图片验证失败: {e}")
            return False

    def convert_to_rgb(self, image_path: str) -> Image.Image:
        """
        将图片转换为RGB格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            RGB格式的PIL Image对象
        """
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise FileProcessingError(f"图片格式转换失败: {e}")

    def resize_image(self, image: Image.Image, max_size: Tuple[int, int] = (2048, 2048)) -> Image.Image:
        """
        调整图片大小
        
        Args:
            image: PIL Image对象
            max_size: 最大尺寸 (width, height)
            
        Returns:
            调整后的图片
        """
        try:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            raise FileProcessingError(f"图片尺寸调整失败: {e}")

    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        获取图片信息
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片信息
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height
                }
        except Exception as e:
            raise FileProcessingError(f"获取图片信息失败: {e}")


class PreviewGenerator:
    """预览图生成器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()

    def generate_preview(self, file_path: str, file_type: str) -> str:
        """
        生成文件预览（base64编码）
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            base64编码的预览图片
        """
        try:
            if file_type == 'pdf':
                preview_data = self.pdf_processor.get_first_page_image(file_path)
            else:
                with open(file_path, 'rb') as f:
                    preview_data = f.read()

            return base64.b64encode(preview_data).decode('utf-8')

        except Exception as e:
            self.logger.error(f"生成预览失败: {e}")
            raise FileProcessingError(f"生成预览失败: {e}")

    def generate_thumbnail(self, image_data: bytes, size: Tuple[int, int] = (300, 300)) -> str:
        """
        生成缩略图
        
        Args:
            image_data: 图片字节数据
            size: 缩略图尺寸
            
        Returns:
            base64编码的缩略图
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(size, Image.Resampling.LANCZOS)

            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85)
            thumbnail_data = output.getvalue()

            return base64.b64encode(thumbnail_data).decode('utf-8')

        except Exception as e:
            self.logger.error(f"生成缩略图失败: {e}")
            raise FileProcessingError(f"生成缩略图失败: {e}")


class FileManager:
    """文件管理器"""

    def __init__(self, upload_folder: str):
        """
        初始化文件管理器
        
        Args:
            upload_folder: 上传文件夹路径
        """
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def save_uploaded_file(self, file_obj, original_filename: str) -> Tuple[str, str]:
        """
        保存上传的文件
        
        Args:
            file_obj: 文件对象
            original_filename: 原始文件名
            
        Returns:
            (保存的文件路径, 唯一文件名)
        """
        try:
            unique_filename = FileProcessor.generate_unique_filename(original_filename)
            file_path = self.upload_folder / unique_filename
            file_obj.save(str(file_path))

            self.logger.info(f"文件保存成功: {unique_filename}")
            return str(file_path), unique_filename

        except Exception as e:
            raise FileProcessingError(f"文件保存失败: {e}")

    def cleanup_file(self, file_path: str) -> bool:
        """
        清理文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否清理成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"文件清理成功: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"文件清理失败: {e}")
            return False

    def get_temp_path(self, filename: str) -> str:
        """
        获取临时文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            临时文件路径
        """
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}_{filename}")
