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


# 配置日志

import logging
logging.basicConfig(level=logging.INFO)

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_processor import PDFProcessor
from services.exceptions import FileProcessingError

def save_images(images_data, output_dir="./fixtures/output_images"):
    os.makedirs(output_dir, exist_ok=True)  # 创建输出目录

    for idx, img_bytes in enumerate(images_data, start=1):
        filename = os.path.join(output_dir, f"image_{idx}.png")
        with open(filename, "wb") as f:
            f.write(img_bytes)

    print(f"保存完成，共保存 {len(images_data)} 张图片到 {output_dir}/")




if __name__ == '__main__':
    process = PDFProcessor()
    file_path=r"/media/twikura/交换区/test.pdf"
    images_data = process.convert_to_images(file_path)
    print(f"共转换 {len(images_data)} 张图片")
    save_images(images_data)
    if not images_data:
        raise FileProcessingError("PDF文件转换失败，没有生成图片")
