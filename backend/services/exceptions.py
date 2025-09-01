"""
自定义异常类
"""


class BaseAppException(Exception):
    """应用基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class OCRError(BaseAppException):
    """OCR处理异常"""
    pass


class FileProcessingError(BaseAppException):
    """文件处理异常"""
    pass


class UnsupportedFileError(FileProcessingError):
    """不支持的文件格式异常"""
    pass


class FileSizeError(FileProcessingError):
    """文件大小超限异常"""
    pass


class ValidationError(BaseAppException):
    """验证异常"""
    pass


class ConfigurationError(BaseAppException):
    """配置异常"""
    pass


class AIAnalysisError(BaseAppException):
    """AI分析异常"""
    pass