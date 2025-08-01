# PaddleOCR 文档扫描应用

基于Flask后端和前端分离架构的OCR文档扫描Web应用，使用PaddleOCR进行文本识别。

## 功能特性

- ✅ 支持PDF、JPG、PNG、BMP、TIFF格式文件上传
- ✅ 拖拽上传和点击上传两种方式
- ✅ 左侧文件预览，右侧文本显示
- ✅ 使用PaddleOCR进行高精度中英文OCR识别
- ✅ 一键复制识别结果
- ✅ 响应式界面设计
- ✅ 实时处理状态显示

## 项目结构

```
PaddleDocScan/
├── backend/
│   ├── api.py                     # Flask API主模块
│   ├── config.py                  # 应用配置
│   └── services/                  # 业务服务模块
│       ├── __init__.py           # 服务模块导出
│       ├── ocr_service.py        # OCR识别服务
│       ├── file_processor.py     # 文件处理服务
│       └── exceptions.py         # 自定义异常
├── frontend/
│   ├── index.html                # 前端页面
│   └── app.js                   # 前端JavaScript逻辑
├── uploads/                     # 临时上传目录
├── requirements.txt             # Python依赖
└── README.md                   # 项目说明
```

## 安装和运行

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 启动Flask后端：
```bash
cd backend
python api.py
```

3. 启动前端
```bash
cd frontend
python -m http.server
```


4. 打开浏览器访问：
```
http://localhost:8000
```

## 技术栈

### 后端
- **Flask**: Web框架
- **Flask-CORS**: 跨域支持
- **PaddleOCR**: OCR文本识别
- **PyMuPDF**: PDF文件处理
- **Pillow**: 图像处理

### 前端
- **HTML5**: 页面结构
- **Bootstrap 5**: UI框架
- **JavaScript ES6**: 交互逻辑
- **Font Awesome**: 图标库

## 使用说明

1. **上传文件**：
   - 点击上传区域选择文件
   - 或直接拖拽文件到上传区域
   - 支持格式：PDF, JPG, PNG, BMP, TIFF
   - 文件大小限制：16MB

2. **查看结果**：
   - 左侧显示文件预览
   - 右侧显示OCR识别的文本
   - 支持PDF多页面识别

3. **复制文本**：
   - 点击右上角"复制文本"按钮
   - 文本将复制到剪贴板

## API接口

### GET /api/health
健康检查接口

**响应格式：**
```json
{
    "success": true,
    "message": "操作成功",
    "data": {
        "status": "healthy",
        "services": {
            "ocr": {...},
            "file_processor": "ready"
        }
    }
}
```

### POST /api/upload
上传文件并进行OCR识别

**请求参数：**
- `file`: 上传的文件

**响应格式：**
```json
{
    "success": true,
    "message": "文档识别完成",
    "data": {
        "filename": "唯一文件名",
        "original_filename": "原始文件名",
        "text": "识别的文本内容",
        "preview": "base64编码的预览图片",
        "file_type": "文件类型",
        "text_length": 1234,
        "has_text": true
    }
}
```

### POST /api/batch-upload
批量文件上传和处理

**请求参数：**
- `files`: 文件列表

**响应格式：**
```json
{
    "success": true,
    "message": "批量处理完成: 3/5 成功",
    "data": {
        "results": [...],
        "summary": {
            "total": 5,
            "success": 3,
            "failed": 2
        }
    }
}
```

## 注意事项

1. 首次运行会自动下载PaddleOCR模型，请保持网络连接
2. 上传的文件会被临时保存并在处理完成后自动删除
3. 建议使用清晰的文档图像以获得更好的识别效果
4. PDF文件将转换为图像进行OCR识别

## 系统要求

- Python 3.7+
- 2GB+ 可用内存
- 网络连接（首次运行下载模型）