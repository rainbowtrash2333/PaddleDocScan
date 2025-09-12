#!/usr/bin/env python3
"""
PDFProcessor 测试模块
测试 PDFProcessor 类的 convert_to_images 功能
"""
import sys
import os
import unittest
from hashlib import file_digest
from unittest.mock import patch, Mock, MagicMock
import tempfile
from pathlib import Path

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_processor import PDFProcessor
from services.exceptions import FileProcessingError




if __name__ == '__main__':
    process = PDFProcessor()
    file_path=r"/media/twikura/交换区/test.pdf"
    images_data = process.convert_to_images(file_path)
    if not images_data:
        raise FileProcessingError("PDF文件转换失败，没有生成图片")
