"""
服务模块
"""
from .ocr_service import OCRService, BatchOCRService
from .file_processor import (
    FileProcessor, PDFProcessor, ImageProcessor,
    PreviewGenerator, FileManager
)
from .exceptions import (
    BaseAppException, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError,
    ConfigurationError
)

__all__ = [
    'OCRService',
    'BatchOCRService',
    'FileProcessor',
    'PDFProcessor',
    'ImageProcessor',
    'PreviewGenerator',
    'FileManager',
    'BaseAppException',
    'OCRError',
    'FileProcessingError',
    'UnsupportedFileError',
    'FileSizeError',
    'ValidationError',
    'ConfigurationError'
]