"""
Flask API主模块
重构后的API接口，使用服务类进行业务逻辑处理
"""
from typing import Dict, Any, Tuple, Union
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from services import (
    OCRService, PDFProcessor, ImageProcessor, PreviewGenerator,
    FileManager, FileProcessor, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError
)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask应用配置
app = Flask(__name__)
CORS(app)

# 应用配置
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = FileProcessor.MAX_FILE_SIZE

# 初始化服务
try:
    ocr_service = OCRService(lang='ch', use_angle_cls=True)
    pdf_processor = PDFProcessor()
    image_processor = ImageProcessor()
    preview_generator = PreviewGenerator()
    file_manager = FileManager(UPLOAD_FOLDER)
    logger.info("所有服务初始化成功")
except Exception as e:
    logger.error(f"服务初始化失败: {e}")
    raise


class APIResponse:
    """API响应封装类"""
    
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


class FileValidator:
    """文件验证器"""
    
    @staticmethod
    def validate_upload_request() -> Tuple[bool, str]:
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
        
        # 文件大小在Flask配置中已经限制，这里做额外检查
        file.seek(0, 2)  # 移到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        if not FileProcessor.validate_file_size(file_size):
            return False, f"文件大小超过限制 ({FileProcessor.MAX_FILE_SIZE // (1024*1024)}MB)"
        
        return True, ""


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e) -> Tuple[Dict[str, Any], int]:
    """处理文件过大异常"""
    return APIResponse.error("文件大小超过限制", "FILE_TOO_LARGE", 413)


@app.errorhandler(Exception)
def handle_general_exception(e) -> Tuple[Dict[str, Any], int]:
    """处理通用异常"""
    logger.error(f"未处理的异常: {e}")
    return APIResponse.error("服务器内部错误", "INTERNAL_ERROR", 500)


@app.route('/', methods=['GET'])
def index() -> str:
    """主页路由"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/api/health', methods=['GET'])
def health_check() -> Dict[str, Any]:
    """健康检查接口"""
    try:
        ocr_info = ocr_service.get_service_info()
        return APIResponse.success({
            'status': 'healthy',
            'services': {
                'ocr': ocr_info,
                'file_processor': 'ready',
                'preview_generator': 'ready'
            }
        })
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return APIResponse.error("服务不健康", "HEALTH_CHECK_FAILED", 503)


@app.route('/api/upload', methods=['POST'])
def upload_and_process() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """
    文件上传和OCR处理接口
    
    Returns:
        包含处理结果的JSON响应
    """
    try:
        # 验证请求
        is_valid, error_msg = FileValidator.validate_upload_request()
        if not is_valid:
            return APIResponse.error(error_msg, "INVALID_REQUEST")
        
        file = request.files['file']
        
        # 验证文件
        is_valid, error_msg = FileValidator.validate_file(file)
        if not is_valid:
            return APIResponse.error(error_msg, "INVALID_FILE")
        
        # 保存文件
        original_filename = secure_filename(file.filename)
        file_path, unique_filename = file_manager.save_uploaded_file(file, original_filename)
        
        try:
            # 获取文件类型
            file_type = FileProcessor.get_file_extension(original_filename)
            
            # 处理文件并执行OCR
            extracted_text = process_file_ocr(file_path, file_type)
            
            # 生成预览
            preview_data = preview_generator.generate_preview(file_path, file_type)
            
            # 构造响应数据
            response_data = {
                'filename': unique_filename,
                'original_filename': original_filename,
                'text': extracted_text,
                'preview': preview_data,
                'file_type': file_type,
                'text_length': len(extracted_text),
                'has_text': bool(extracted_text.strip())
            }
            
            logger.info(f"文件处理完成: {original_filename}")
            return APIResponse.success(response_data, "文档识别完成")
            
        except Exception as e:
            logger.error(f"文件处理失败: {e}")
            return APIResponse.error(f"文件处理失败: {str(e)}", "PROCESSING_ERROR", 500)
        finally:
            # 清理上传的文件
            file_manager.cleanup_file(file_path)
    
    except Exception as e:
        logger.error(f"上传处理异常: {e}")
        return APIResponse.error("上传处理失败", "UPLOAD_ERROR", 500)


def process_file_ocr(file_path: str, file_type: str) -> str:
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
    try:
        if file_type == 'pdf':
            # 处理PDF文件
            images_data = pdf_processor.convert_to_images(file_path)
            if not images_data:
                raise FileProcessingError("PDF文件转换失败，没有生成图片")
            
            # 批量OCR识别
            texts = ocr_service.recognize_multiple_images(images_data)
            
            # 组合结果
            extracted_text = ""
            for i, text in enumerate(texts):
                if text.strip():
                    extracted_text += f"第{i+1}页:\n{text}\n\n"
            
            return extracted_text.strip()
        else:
            # 处理图片文件
            if not image_processor.validate_image(file_path):
                raise FileProcessingError("图片文件无效或损坏")
            
            return ocr_service.recognize_image(file_path)
    
    except (OCRError, FileProcessingError):
        raise
    except Exception as e:
        raise OCRError(f"OCR处理过程中发生未知错误: {e}")


@app.route('/api/batch-upload', methods=['POST'])
def batch_upload_and_process() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """
    批量文件上传和处理接口
    
    Returns:
        包含批量处理结果的JSON响应
    """
    try:
        if 'files' not in request.files:
            return APIResponse.error("没有选择文件", "NO_FILES")
        
        files = request.files.getlist('files')
        if not files:
            return APIResponse.error("文件列表为空", "EMPTY_FILES")
        
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
                file_path, unique_filename = file_manager.save_uploaded_file(file, original_filename)
                
                try:
                    file_type = FileProcessor.get_file_extension(original_filename)
                    extracted_text = process_file_ocr(file_path, file_type)
                    
                    results.append({
                        'index': i,
                        'filename': original_filename,
                        'success': True,
                        'text': extracted_text,
                        'text_length': len(extracted_text),
                        'has_text': bool(extracted_text.strip())
                    })
                finally:
                    file_manager.cleanup_file(file_path)
                    
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
        
        return APIResponse.success({
            'results': results,
            'summary': {
                'total': total_count,
                'success': success_count,
                'failed': total_count - success_count
            }
        }, f"批量处理完成: {success_count}/{total_count} 成功")
        
    except Exception as e:
        logger.error(f"批量上传处理异常: {e}")
        return APIResponse.error("批量处理失败", "BATCH_ERROR", 500)


@app.route('/static/<path:filename>')
def serve_static(filename: str) -> str:
    """静态文件服务"""
    return send_from_directory('../frontend', filename)


if __name__ == '__main__':
    logger.info("启动Flask应用")
    app.run(debug=True, host='0.0.0.0', port=5000)