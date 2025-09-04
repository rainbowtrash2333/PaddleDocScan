"""
应用配置模块
"""
import os
from typing import Dict, Any
from pathlib import Path


class Config:
    """基础配置类"""
    
    # 应用基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 服务器配置
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'}
    
    # OCR配置
    OCR_LANGUAGE = os.environ.get('OCR_LANGUAGE', 'ch')
    OCR_USE_ANGLE_CLS = os.environ.get('OCR_USE_ANGLE_CLS', 'true').lower() == 'true'
    OCR_MAX_WORKERS = int(os.environ.get('OCR_MAX_WORKERS', 4))
    
    # 图片处理配置
    IMAGE_MAX_SIZE = (2048, 2048)  # 最大图片尺寸
    THUMBNAIL_SIZE = (300, 300)    # 缩略图尺寸
    PDF_DPI = int(os.environ.get('PDF_DPI', 200))  # PDF转图片DPI
    PREVIEW_DPI = int(os.environ.get('PREVIEW_DPI', 150))  # 预览图DPI
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # CORS配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Dify AI配置
    DIFY_MODELS = {
        'general': {
            'id': 'general',
            'name': '通用分析',
            'description': '对文本内容进行全面的分析和理解',
            'url': os.environ.get('DIFY_GENERAL_URL', 'https://api.dify.ai/v1/workflows/run'),
            'token': os.environ.get('DIFY_GENERAL_TOKEN', 'app-dAUUqBRS185OrvicXgikgb8K')
        },
        'summary': {
            'id': 'summary',
            'name': '内容摘要',
            'description': '提取文本的核心内容和关键信息',
            'url': os.environ.get('DIFY_SUMMARY_URL', 'https://api.dify.ai/v1/workflows/run'),
            'token': os.environ.get('DIFY_SUMMARY_TOKEN', 'app-dAUUqBRS185OrvicXgikgb8K')
        },
        'extract': {
            'id': 'extract',
            'name': '信息提取',
            'description': '从文本中提取特定的数据和实体',
            'url': os.environ.get('DIFY_EXTRACT_URL', 'https://api.dify.ai/v1/workflows/run'),
            'token': os.environ.get('DIFY_EXTRACT_TOKEN', 'app-dAUUqBRS185OrvicXgikgb8K')
        },
        'sentiment': {
            'id': 'sentiment',
            'name': '情感分析',
            'description': '分析文本的情感倾向和态度',
            'url': os.environ.get('DIFY_SENTIMENT_URL', 'https://api.dify.ai/v1/workflows/run'),
            'token': os.environ.get('DIFY_SENTIMENT_TOKEN', 'app-dAUUqBRS185OrvicXgikgb8K')
        }
    }
    
    @classmethod
    def init_app(cls, app) -> None:
        """初始化Flask应用配置"""
        app.config.from_object(cls)
        
        # 确保上传目录存在
        upload_path = Path(cls.UPLOAD_FOLDER)
        upload_path.mkdir(exist_ok=True)
    
    @classmethod
    def get_config_dict(cls) -> Dict[str, Any]:
        """获取配置字典"""
        return {
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT,
            'upload_folder': cls.UPLOAD_FOLDER,
            'max_content_length': cls.MAX_CONTENT_LENGTH,
            'allowed_extensions': list(cls.ALLOWED_EXTENSIONS),
            'ocr_language': cls.OCR_LANGUAGE,
            'ocr_use_angle_cls': cls.OCR_USE_ANGLE_CLS,
            'log_level': cls.LOG_LEVEL
        }


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # 生产环境安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-set-secret-key-in-production'
    
    @classmethod
    def init_app(cls, app) -> None:
        Config.init_app(app)
        
        # 生产环境额外配置
        if not os.environ.get('SECRET_KEY'):
            raise RuntimeError('SECRET_KEY environment variable must be set in production')


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    UPLOAD_FOLDER = 'test_uploads'
    LOG_LEVEL = 'DEBUG'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}