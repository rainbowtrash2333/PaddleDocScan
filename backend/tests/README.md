# PaddleDocScan 测试文档

本目录包含了PaddleDocScan项目的所有测试文件，按功能分类组织。

## 目录结构

```
tests/
├── fixtures/                    # 测试数据文件
│   ├── sample_image.png         # 测试用图片
│   └── sample_document.pdf      # 测试用PDF文档
├── test_ocr_service.py          # OCR服务测试
├── test_ai_analysis_api.py      # AI分析API测试
├── test_dify_integration.py     # Dify API集成测试
├── run_tests.py                 # 测试运行器
└── README.md                    # 本文档
```

## 测试文件说明

### 1. test_ocr_service.py
- **功能**: 测试OCR服务的图片和PDF文档识别功能
- **测试内容**:
  - 图片OCR识别
  - PDF文档转换和OCR识别
- **运行方式**: `python test_ocr_service.py`

### 2. test_ai_analysis_api.py
- **功能**: 测试本地API服务器的AI分析功能
- **测试内容**:
  - 获取分析类型API
  - 不同类型的AI分析API调用
- **运行方式**: `python test_ai_analysis_api.py [服务器地址]`
- **默认服务器**: http://localhost:20010

### 3. test_dify_integration.py
- **功能**: 直接测试Dify工作流API的调用格式和响应
- **测试内容**:
  - Dify API基础调用测试
  - 不同输入参数测试
- **运行方式**: `python test_dify_integration.py`

### 4. run_tests.py
- **功能**: 测试运行器，统一执行所有测试
- **特点**:
  - 按顺序运行所有测试
  - 提供详细的测试报告
  - 支持超时控制
- **运行方式**: `python run_tests.py`

## 测试数据

### fixtures/ 目录
包含测试所需的样本文件：
- `sample_image.png`: 用于OCR识别测试的图片文件
- `sample_document.pdf`: 用于PDF处理测试的文档文件

## 使用指南

### 运行所有测试
```bash
cd backend/tests
python run_tests.py
```

### 运行单个测试
```bash
cd backend/tests
python test_ocr_service.py
python test_ai_analysis_api.py
python test_dify_integration.py
```

### 自定义API服务器测试
```bash
python test_ai_analysis_api.py http://your-server:port
```

## 注意事项

1. **环境要求**: 
   - 确保已安装所有依赖包
   - OCR测试需要PaddleOCR环境
   - API测试需要服务器运行

2. **网络要求**:
   - Dify集成测试需要互联网连接
   - API测试需要本地服务器运行

3. **测试数据**:
   - fixtures目录包含测试用的样本文件
   - 请勿删除或修改这些文件

4. **超时设置**:
   - OCR测试超时: 根据文件大小自动调整
   - API测试超时: 60秒
   - Dify API测试超时: 30秒

## 故障排除

### 常见问题

1. **OCR测试失败**
   - 检查PaddleOCR是否正确安装
   - 确认样本文件存在

2. **API测试失败**
   - 确认本地服务器已启动
   - 检查端口号是否正确

3. **Dify测试失败**
   - 检查网络连接
   - 确认API Token有效

### 调试方法

1. 单独运行失败的测试文件
2. 检查控制台输出的详细错误信息
3. 确认环境配置和依赖安装