"""
业务逻辑控制器
处理OCR文档扫描相关的业务逻辑
"""
import gc
import logging
import traceback
from typing import Dict, Any, Tuple, List
from werkzeug.utils import secure_filename

from services import (
    OCRService, PDFProcessor, ImageProcessor, PreviewGenerator,
    FileManager, FileProcessor, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError,
    AIAnalysisService, AIAnalysisError
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = True  # 允许向上级 logger 传递到 root logger

class FileValidator:
    """文件验证器"""
    
    @staticmethod
    def validate_upload_request(request) -> Tuple[bool, str]:
        """验证上传请求"""
        if 'file' not in request.files:
            return False, "没有选择文件"
        
        file = request.files['file']
        if file.filename == '':
            return False, "没有选择文件"
        
        return True, ""
    
    @staticmethod
    def validate_file(file) -> Tuple[bool, str]:
        """验证文件"""
        if not file:
            return False, "文件为空"
        
        filename = secure_filename(file.filename)
        if not FileProcessor.is_allowed_file(filename):
            return False, f"不支持的文件格式，支持的格式: {', '.join(FileProcessor.ALLOWED_EXTENSIONS)}"
        
        # 文件大小检查
        file.seek(0, 2)  # 移到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if not FileProcessor.validate_file_size(file_size):
            return False, f"文件大小超过限制 ({FileProcessor.MAX_FILE_SIZE // (1024*1024)}MB)"
        
        return True, ""


class OCRController:
    """OCR业务逻辑控制器"""
    
    def __init__(self, upload_folder: str):
        """
        初始化OCR控制器
        
        Args:
            upload_folder: 上传文件目录
        """
        self.upload_folder = upload_folder
        self.ocr_service = OCRService(lang='ch', use_angle_cls=True)
        self.pdf_processor = PDFProcessor()
        self.image_processor = ImageProcessor()
        self.preview_generator = PreviewGenerator()
        self.file_manager = FileManager(upload_folder)
        logger.info("OCR控制器初始化成功")
    
    def get_health_info(self) -> Dict[str, Any]:
        """
        获取健康检查信息
        
        Returns:
            健康检查数据
        """
        try:
            ocr_info = self.ocr_service.get_service_info()
            return {
                'status': 'healthy',
                'services': {
                    'ocr': ocr_info,
                    'file_processor': 'ready',
                    'preview_generator': 'ready'
                }
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            raise OCRError(f"服务不健康: {e}")
    
    def process_single_file(self, file) -> Dict[str, Any]:
        """
        处理单个文件上传和OCR识别
        
        Args:
            file: 上传的文件对象
            
        Returns:
            处理结果数据
            
        Raises:
            ValidationError: 验证失败
            FileProcessingError: 文件处理失败
            OCRError: OCR识别失败
        """
        # 验证请求和文件
        is_valid, error_msg = FileValidator.validate_file(file)
        if not is_valid:
            raise ValidationError(error_msg)
        
        # 保存文件
        original_filename = secure_filename(file.filename)
        file_path, unique_filename = self.file_manager.save_uploaded_file(file, original_filename)
        
        try:
            # 获取文件类型
            file_type = FileProcessor.get_file_extension(original_filename)
            
            # 处理文件并执行OCR
            extracted_text = self._process_file_ocr(file_path, file_type)
            
            # 生成预览
            preview_data = self.preview_generator.generate_preview(file_path, file_type)
            
            # 构造响应数据
            result_data = {
                'filename': unique_filename,
                'original_filename': original_filename,
                'text': extracted_text,
                'preview': preview_data,
                'file_type': file_type,
                'text_length': len(extracted_text),
                'has_text': bool(extracted_text.strip())
            }
            
            logger.info(f"文件处理完成: {original_filename}")
            return result_data
            
        finally:
            # 清理上传的文件
            self.file_manager.cleanup_file(file_path)
    
    def process_batch_files(self, files) -> Dict[str, Any]:
        """
        批量处理文件上传和OCR识别
        
        Args:
            files: 文件列表
            
        Returns:
            批量处理结果数据
        """
        if not files:
            raise ValidationError("文件列表为空")
        
        results = []
        for i, file in enumerate(files):
            try:
                # 验证文件
                is_valid, error_msg = FileValidator.validate_file(file)
                if not is_valid:
                    results.append({
                        'index': i,
                        'filename': file.filename,
                        'success': False,
                        'error': error_msg
                    })
                    continue
                
                # 处理单个文件
                original_filename = secure_filename(file.filename)
                file_path, unique_filename = self.file_manager.save_uploaded_file(file, original_filename)
                
                try:
                    file_type = FileProcessor.get_file_extension(original_filename)
                    extracted_text = self._process_file_ocr(file_path, file_type)
                    
                    results.append({
                        'index': i,
                        'filename': original_filename,
                        'success': True,
                        'text': extracted_text,
                        'text_length': len(extracted_text),
                        'has_text': bool(extracted_text.strip())
                    })
                finally:
                    self.file_manager.cleanup_file(file_path)
                    
            except Exception as e:
                results.append({
                    'index': i,
                    'filename': file.filename if file else f'file_{i}',
                    'success': False,
                    'error': str(e)
                })
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        return {
            'results': results,
            'summary': {
                'total': total_count,
                'success': success_count,
                'failed': total_count - success_count
            }
        }
    
    def _process_file_ocr(self, file_path: str, file_type: str) -> str:
        """
        处理文件OCR识别
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            识别的文本内容
            
        Raises:
            OCRError: OCR处理失败
            FileProcessingError: 文件处理失败
        """
        logger.info(f"文件执行OCR: {file_path}")
        try:
            if file_type == 'pdf':
                # 处理PDF文件
                images_data = self.pdf_processor.convert_to_images(file_path)
                if not images_data:
                    raise FileProcessingError("PDF文件转换失败，没有生成图片")
                
                # 批量OCR识别
                texts = self.ocr_service.recognize_multiple_images(images_data)
                
                # 清理内存
                gc.collect()
                
                # 组合结果
                extracted_text = ""
                for i, text in enumerate(texts):
                    if text.strip():
                        extracted_text += f"第{i+1}页:\n{text}\n\n"
                
                return extracted_text.strip()
            else:
                # 处理图片文件
                if not self.image_processor.validate_image(file_path):
                    raise FileProcessingError("图片文件无效或损坏")
                
                result = self.ocr_service.recognize_image(file_path)
                
                # 清理内存
                gc.collect()
                
                return result
        
        except (OCRError, FileProcessingError):
            raise
        except Exception as e:
            raise OCRError(f"OCR处理过程中发生未知错误: {e}\n{traceback.format_exc()}")


class AIAnalysisController:
    """AI分析业务逻辑控制器"""
    
    def __init__(self, dify_models_config: Dict[str, Dict[str, str]] = None):
        """
        初始化AI分析控制器
        
        Args:
            dify_models_config: Dify模型配置
        """
        self.ai_analysis_service = AIAnalysisService(dify_models_config)
        logger.info("AI分析控制器初始化成功")
    
    def analyze_content(self, content: str, analysis_type: str = 'general') -> Dict[str, Any]:
        """
        分析内容 - 直接调用Dify
        
        Args:
            content: 要分析的文本内容
            analysis_type: 分析类型 (general, summary, extract, sentiment)
            
        Returns:
            分析结果数据
            
        Raises:
            ValidationError: 验证失败
            AIAnalysisError: AI分析失败
        """
        # 验证输入
        if not content or not content.strip():
            raise ValidationError("分析内容不能为空")
        
        if len(content) > 50000:
            raise ValidationError("内容长度超过限制（最多50000字符）")
        
        try:
            # 执行AI分析
            analysis_result = self.ai_analysis_service.analyze_content(content, analysis_type)
            
            # 清理内存
            gc.collect()
            
            logger.info(f"AI分析完成，内容长度: {len(content)}")
            return analysis_result
            
        except AIAnalysisError:
            raise
        except Exception as e:
            logger.error(f"AI分析过程中发生错误: {e}")
            raise AIAnalysisError(f"AI分析失败: {str(e)}")


class ResponseHelper:
    """API响应辅助类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """成功响应"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response
    
    @staticmethod
    def error(message: str, error_code: str = None, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
        """错误响应"""
        response = {
            'success': False,
            'message': message
        }
        if error_code:
            response['error_code'] = error_code
        return response, status_code