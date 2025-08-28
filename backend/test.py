from services import (
    OCRService, PDFProcessor, ImageProcessor, PreviewGenerator,
    FileManager, FileProcessor, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError
)

Test_OCR_Server = OCRService(lang='ch', use_angle_cls=True)
pdf_processor = PDFProcessor()
def _test_orc_image():
    image_path = r'./uploads/test.png'
    pdf_path = r'./uploads/test.pdf'
    img_txt = Test_OCR_Server.recognize_image(image_path)
    print(img_txt)
    # 获取文件类型
    file_type = FileProcessor.get_file_extension(pdf_path)
    if file_type == 'pdf':
        # 处理PDF文件
        images_data = pdf_processor.convert_to_images(pdf_path)
        if not images_data:
            raise FileProcessingError("PDF文件转换失败，没有生成图片")

        # 批量OCR识别
        texts = Test_OCR_Server.recognize_multiple_images(images_data)

        # 组合结果
        extracted_text = ""
        for i, text in enumerate(texts):
            if text.strip():
                extracted_text += f"第{i + 1}页:\n{text}\n\n"

        print(extracted_text.strip())

def _test_orc_pdf():
    pdf_path = r'./uploads/test.pdf'
    # 获取文件类型
    file_type = FileProcessor.get_file_extension(pdf_path)
    if file_type == 'pdf':
        # 处理PDF文件
        images_data = pdf_processor.convert_to_images(pdf_path)
        if not images_data:
            raise FileProcessingError("PDF文件转换失败，没有生成图片")

        # 批量OCR识别
        texts = Test_OCR_Server.recognize_multiple_images(images_data)

        # 组合结果
        extracted_text = ""
        for i, text in enumerate(texts):
            if text.strip():
                extracted_text += f"第{i + 1}页:\n{text}\n\n"

        print(extracted_text.strip())
    
if __name__ == '__main__':
    _test_orc_image()
    _test_orc_pdf()
    _test_orc_pdf()

  