#!/usr/bin/env python3
"""
OCR服务测试
测试图片和PDF文档的OCR识别功能
"""
import sys
import os

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import (
    OCRService, PDFProcessor, ImageProcessor, PreviewGenerator,
    FileManager, FileProcessor, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError
)

Test_OCR_Server = OCRService(lang='ch', use_angle_cls=True)
pdf_processor = PDFProcessor()

def test_ocr_image():
    """测试图片OCR识别"""
    image_path = './fixtures/sample_image.png'
    try:
        img_txt = Test_OCR_Server.recognize_image(image_path)
        print(f"图片OCR结果: {img_txt}")
        return img_txt
    except Exception as e:
        print(f"图片OCR测试失败: {e}")
        return None

def test_pdf_processing():
    """测试PDF文档处理"""
    pdf_path = './fixtures/sample_document.pdf'
    try:
        # 获取文件类型
        file_type = FileProcessor.get_file_extension(pdf_path)
        if file_type == 'pdf':
            # 处理PDF文件
            images_data = pdf_processor.convert_to_images(pdf_path)
            if not images_data:
                raise FileProcessingError("PDF文件转换失败，没有生成图片")
            
            print(f"PDF转换成功，生成了{len(images_data)}张图片")
            
            # 对第一张图片进行OCR
            if images_data:
                first_image = images_data[0]
                ocr_result = Test_OCR_Server.recognize_from_bytes(first_image['image_data'])
                print(f"PDF第一页OCR结果: {ocr_result}")
                return ocr_result
                
    except Exception as e:
        print(f"PDF处理测试失败: {e}")
        return None

if __name__ == "__main__":
    print("=== OCR服务测试 ===")
    
    # 切换到tests目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("\n1. 测试图片OCR识别...")
    test_ocr_image()
    
    print("\n2. 测试PDF文档处理...")
    test_pdf_processing()
    
    print("\n测试完成！")
