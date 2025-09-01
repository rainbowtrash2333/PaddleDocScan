"""
Flask API主模块
重构后的API接口，使用控制器进行业务逻辑处理
"""
import os
import logging
import gc
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from controllers import OCRController, AIAnalysisController, FileValidator, ResponseHelper
from services import (
    FileProcessor, ValidationError, OCRError, FileProcessingError,
    AIAnalysisError
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

# 初始化控制器
try:
    ocr_controller = OCRController(UPLOAD_FOLDER)
    ai_analysis_controller = AIAnalysisController()
    logger.info("所有控制器初始化成功")
except Exception as e:
    logger.error(f"控制器初始化失败: {e}")
    raise


# =============================================================================
# 错误处理器
# =============================================================================

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    """处理文件过大异常"""
    return ResponseHelper.error("文件大小超过限制", "FILE_TOO_LARGE", 413)


@app.errorhandler(Exception)
def handle_general_exception(e):
    """处理通用异常"""
    logger.error(f"未处理的异常: {e}")
    return ResponseHelper.error("服务器内部错误", "INTERNAL_ERROR", 500)


# =============================================================================
# 静态文件路由
# =============================================================================

@app.route('/', methods=['GET'])
def index():
    """主页路由"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/analysis')
def analysis_page():
    """AI分析页面路由"""
    return send_from_directory('../frontend', 'analysis.html')


@app.route('/static/<path:filename>')
def serve_static(filename: str):
    """静态文件服务"""
    return send_from_directory('../frontend', filename)


# =============================================================================
# API路由
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        health_data = ocr_controller.get_health_info()
        return ResponseHelper.success(health_data)
    except OCRError as e:
        logger.error(f"健康检查失败: {e}")
        return ResponseHelper.error("服务不健康", "HEALTH_CHECK_FAILED", 503)
    except Exception as e:
        logger.error(f"健康检查异常: {e}")
        return ResponseHelper.error("健康检查失败", "HEALTH_CHECK_ERROR", 500)


@app.route('/api/upload', methods=['POST'])
def upload_and_process():
    """
    文件上传和OCR处理接口
    
    Returns:
        包含处理结果的JSON响应
    """
    try:
        # 验证请求
        is_valid, error_msg = FileValidator.validate_upload_request(request)
        if not is_valid:
            return ResponseHelper.error(error_msg, "INVALID_REQUEST")
        
        file = request.files['file']
        
        # 处理文件
        result_data = ocr_controller.process_single_file(file)
        
        return ResponseHelper.success(result_data, "文档识别完成")
        
    except ValidationError as e:
        return ResponseHelper.error(str(e), "VALIDATION_ERROR", 400)
    except (OCRError, FileProcessingError) as e:
        logger.error(f"文件处理失败: {e}")
        return ResponseHelper.error(f"文件处理失败: {str(e)}", "PROCESSING_ERROR", 500)
    except Exception as e:
        logger.error(f"上传处理异常: {e}")
        return ResponseHelper.error("上传处理失败", "UPLOAD_ERROR", 500)


@app.route('/api/batch-upload', methods=['POST'])
def batch_upload_and_process():
    """
    批量文件上传和处理接口
    
    Returns:
        包含批量处理结果的JSON响应
    """
    try:
        if 'files' not in request.files:
            return ResponseHelper.error("没有选择文件", "NO_FILES")
        
        files = request.files.getlist('files')
        if not files:
            return ResponseHelper.error("文件列表为空", "EMPTY_FILES")
        
        # 批量处理文件
        batch_result = ocr_controller.process_batch_files(files)
        
        success_count = batch_result['summary']['success']
        total_count = batch_result['summary']['total']
        
        return ResponseHelper.success(
            batch_result, 
            f"批量处理完成: {success_count}/{total_count} 成功"
        )
        
    except ValidationError as e:
        return ResponseHelper.error(str(e), "VALIDATION_ERROR", 400)
    except Exception as e:
        logger.error(f"批量上传处理异常: {e}")
        return ResponseHelper.error("批量处理失败", "BATCH_ERROR", 500)


@app.route('/api/ai-analysis', methods=['POST'])
def ai_analysis():
    """
    AI内容分析接口
    
    Returns:
        包含AI分析结果的JSON响应
    """
    try:
        # 验证请求数据
        if not request.json:
            return ResponseHelper.error("请求数据格式错误", "INVALID_JSON")
        
        content = request.json.get('content', '').strip()
        analysis_type = request.json.get('analysis_type', 'general')
        
        # 执行AI分析
        analysis_result = ai_analysis_controller.analyze_content(content, analysis_type)
        
        return ResponseHelper.success(analysis_result, "AI分析完成")
        
    except ValidationError as e:
        return ResponseHelper.error(str(e), "VALIDATION_ERROR", 400)
    except AIAnalysisError as e:
        logger.error(f"AI分析失败: {e}")
        return ResponseHelper.error(f"AI分析失败: {str(e)}", "AI_ANALYSIS_ERROR", 500)
    except Exception as e:
        logger.error(f"AI分析接口异常: {e}")
        return ResponseHelper.error("AI分析服务暂时不可用", "AI_SERVICE_ERROR", 500)


# =============================================================================
# 应用启动
# =============================================================================

if __name__ == '__main__':
    logger.info("启动Flask应用")
    app.run(debug=True, host='0.0.0.0', port=20010, threaded=False)