"""
OCR服务模块
提供文档OCR识别功能
"""
from typing import List, Optional, Union, Dict, Any
import os
import uuid
import tempfile
from pathlib import Path
from PIL import Image
import io
import base64
import logging
from paddleocr import PaddleOCR
import traceback
from .exceptions import OCRError, FileProcessingError


class OCRService:
    """OCR识别服务类"""

    def __init__(self, lang: str = 'ch', use_angle_cls: bool = True):
        """
        初始化OCR服务

        Args:
            lang: 识别语言，默认为中文
            use_angle_cls: 是否使用角度分类器
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = True  # 允许向上级 logger 传递到 root logger
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=use_angle_cls,
                lang=lang,
            )
            self.logger.info("PaddleOCR初始化成功")
        except Exception as e:
            self.logger.error(f"PaddleOCR初始化失败: {e}")
            raise OCRError(f"OCR服务初始化失败: {e}")

    def recognize_image(self, image_data: Union[str, bytes, Image.Image]) -> str:
        """
        识别图片中的文字

        Args:
            image_data: 图片数据，可以是文件路径、字节数据或PIL Image对象

        Returns:
            识别出的文本内容

        Raises:
            OCRError: OCR识别失败时抛出
        """
        temp_path: Optional[str] = None

        try:
            # 处理不同类型的输入数据
            if isinstance(image_data, str):
                # 文件路径
                if not os.path.exists(image_data):
                    raise FileProcessingError(f"图片文件不存在: {image_data}")
                temp_path = image_data
                created_temp = False
            else:
                # 字节数据或PIL Image对象
                image = self._prepare_image(image_data)
                temp_path = self._save_temp_image(image)
                created_temp = True

            if not os.path.exists(temp_path):
                self.logger.error(f"file {temp_path} not exists")
                raise FileProcessingError(f"file {temp_path} not exists")

            result = self.ocr.ocr(temp_path)
            extracted_text = self._extract_text_from_result(result)

            self.logger.info(f"OCR识别完成，识别出{len(extracted_text.splitlines())}行文本")
            return extracted_text

        except Exception as e:
            self.logger.error(f"OCR识别失败: {e}\n{traceback.format_exc()}")
            raise OCRError(f"OCR识别失败: {e}")
        finally:
            # 清理临时文件
            if temp_path and created_temp and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    self.logger.warning(f"清理临时文件失败: {e}")

    def recognize_multiple_images(self, images_data: List[Union[str, bytes, Image.Image]]) -> List[str]:
        """
        批量识别多张图片

        Args:
            images_data: 图片数据列表

        Returns:
            识别结果列表
        """
        results = []
        for i, image_data in enumerate(images_data):
            try:
                text = self.recognize_image(image_data)
                results.append(text)
                self.logger.info(f"第{i + 1}张图片识别完成")
            except Exception as e:
                self.logger.error(f"第{i + 1}张图片识别失败: {e}")
                results.append("")  # 识别失败时添加空字符串

        return results

    def _prepare_image(self, image_data: Union[bytes, Image.Image]) -> Image.Image:
        """
        准备图片数据

        Args:
            image_data: 字节数据或PIL Image对象

        Returns:
            PIL Image对象
        """
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise FileProcessingError("不支持的图片数据类型")

        # 转换为RGB格式
        if image.mode != 'RGB':
            image = image.convert('RGB')

        return image

    def _save_temp_image(self, image: Image.Image) -> str:
        """
        保存临时图片文件

        Args:
            image: PIL Image对象

        Returns:
            临时文件路径
        """
        temp_dir = tempfile.gettempdir()
        temp_filename = f"ocr_temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(temp_dir, temp_filename)

        try:
            image.save(temp_path, 'JPEG', quality=95)
            return temp_path
        except Exception as e:
            raise FileProcessingError(f"保存临时图片失败: {e}")

    def _extract_text_from_result(self, result: List[Any]) -> str:
        extracted_text = []
        if not result:
            return ""

        # 如果是 predict 返回的 dict 格式
        if isinstance(result[0], dict) and "rec_texts" in result[0]:
            for res in result:
                extracted_text.extend(res["rec_texts"])
        else:
            # 普通 ocr 返回的 list 格式
            for line in result[0]:
                extracted_text.append(line[1][0])
        return "\n".join(extracted_text)

    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息

        Returns:
            服务信息字典
        """
        return {
            'service': 'OCRService',
            'engine': 'PaddleOCR',
            'status': 'ready',
            'supported_formats': ['jpg', 'jpeg', 'png', 'bmp', 'tiff']
        }


class BatchOCRService(OCRService):
    """批量OCR处理服务"""

    def __init__(self, lang: str = 'ch', use_angle_cls: bool = True, max_workers: int = 4):
        """
        初始化批量OCR服务

        Args:
            lang: 识别语言
            use_angle_cls: 是否使用角度分类器
            max_workers: 最大并发数
        """
        super().__init__(lang, use_angle_cls)
        self.max_workers = max_workers

    def process_batch(self, images_data: List[Union[str, bytes, Image.Image]],
                      progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        批量处理图片OCR

        Args:
            images_data: 图片数据列表
            progress_callback: 进度回调函数

        Returns:
            处理结果列表，包含文本和状态信息
        """
        results = []
        total = len(images_data)

        for i, image_data in enumerate(images_data):
            try:
                text = self.recognize_image(image_data)
                results.append({
                    'index': i,
                    'success': True,
                    'text': text,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'success': False,
                    'text': '',
                    'error': str(e)
                })

            # 执行进度回调
            if progress_callback:
                progress_callback(i + 1, total)

        return results
