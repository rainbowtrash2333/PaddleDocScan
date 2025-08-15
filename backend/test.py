from services import (
    OCRService, PDFProcessor, ImageProcessor, PreviewGenerator,
    FileManager, FileProcessor, OCRError, FileProcessingError,
    UnsupportedFileError, FileSizeError, ValidationError
)

def _test_orc_image():
    Test_OCR_Server = OCRService(lang='ch', use_angle_cls=True)
    image_path = r'./uploads/test.png'
    img_txt = Test_OCR_Server.recognize_image(image_path)
    print(img_txt)
    
    
if __name__ == '__main__':
    _test_orc_image()
    
    
  