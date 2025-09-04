# PaddleDocScan

基于PaddleOCR和Dify AI的智能文档扫描识别系统。支持OCR文本识别和AI内容分析。

## 功能特性

- 📄 **多格式支持**: PDF、JPG、PNG、BMP、TIFF
- 🔍 **OCR识别**: 基于PaddleOCR的中英文文本识别  
- 🤖 **AI分析**: 集成Dify工作流的智能内容分析
- 📱 **响应式UI**: 现代化的Web界面设计
- 🚀 **拖拽上传**: 支持文件拖拽和点击上传

## 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 快速启动
```bash
# 启动后端服务
cd backend && python3 api.py

# 启动前端
cd frontend && python3 -m http.server
http://localhost:20010
```

### 3. Docker部署
```bash
docker-compose up -d
```

## 项目架构

```
PaddleDocScan/
├── backend/                    # 后端服务
│   ├── api.py                 # Flask API主入口
│   ├── config.py              # 配置管理
│   ├── controllers.py         # 控制器层
│   ├── services/              # 业务服务层
│   └── tests/                 # 测试套件
├── frontend/                  # 前端界面
│   ├── index.html             # 主页面
│   ├── analysis.html          # AI分析页面
│   └── assets/                # 静态资源
├── docker-compose.yaml        # Docker配置
└── nginx.conf                 # Nginx配置
```

## API接口

| 接口 | 方法 | 功能 |
|-----|------|------|
| `/api/upload` | POST | 文件上传和OCR识别 |
| `/api/ai-analysis` | POST | AI内容分析 |
| `/api/analysis-types` | GET | 获取分析类型 |

## 配置说明

### Dify AI配置
在 `backend/config.py` 中配置Dify模型：
```python
DIFY_MODELS = {
    'general': {
        'name': '通用分析',
        'token': 'your-api-token',
        'url': 'https://api.dify.ai/v1/workflows/run'
    }
}
```

### 环境变量
```bash
FLASK_PORT=20010
DIFY_GENERAL_TOKEN=your-token
OCR_LANGUAGE=ch
```

## 测试

```bash
# 运行所有测试
cd backend/tests && python run_tests.py

# 单独测试
python test_ocr_service.py
python test_ai_analysis_api.py
```

## 许可证

MIT License