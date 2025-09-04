class OCRApp {
    constructor() {
        this.initElements();
        this.initEventListeners();
        this.apiUrl = CONFIG.API_BASE_URL;
    }

    initElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.loadingDiv = document.getElementById('loadingDiv');
        this.previewContainer = document.getElementById('previewContainer');
        this.previewContent = document.getElementById('previewContent');
        this.textOutput = document.getElementById('textOutput');
        this.copyBtn = document.getElementById('copyBtn');
        this.aiAnalysisBtn = document.getElementById('aiAnalysisBtn');
        this.toast = new bootstrap.Toast(document.getElementById('toast'));
        this.toastBody = document.getElementById('toastBody');
        this.currentText = ''; // 存储当前识别的文本
    }

    initEventListeners() {
        // 文件选择
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // 拖拽上传
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });

        // 复制按钮
        this.copyBtn.addEventListener('click', () => {
            this.copyText();
        });

        // AI分析按钮
        this.aiAnalysisBtn.addEventListener('click', () => {
            this.openAIAnalysis();
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        // 打印文件全名（包含后缀）到控制台
        console.log('Selected file:', file.name);

        // 验证文件类型
        const allowedTypes = CONFIG.ALLOWED_FILE_TYPES;
        if (!allowedTypes.includes(file.type)) {
            this.showToast('请选择支持的文件格式（PDF, JPG, PNG, BMP, TIFF）', 'error');
            return;
        }

        // 验证文件大小（16MB）
        if (file.size > CONFIG.MAX_FILE_SIZE) {
            this.showToast('文件大小不能超过16MB', 'error');
            return;
        }

        this.uploadFile(file);
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            this.showLoading(true);
            this.hidePreview();
            this.clearTextOutput();

            const response = await fetch(`${this.apiUrl}${CONFIG.ENDPOINTS.UPLOAD}`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                const data = result.data;
                this.showPreview(data.preview, data.file_type, data.original_filename);
                this.showTextOutput(data.text);
                this.showToast(result.message || '文档识别完成！', 'success');
            } else {
                this.showToast(result.message || '上传失败', 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast('上传过程中发生错误', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    showLoading(show) {
        if (show) {
            this.loadingDiv.classList.add('show');
        } else {
            this.loadingDiv.classList.remove('show');
        }
    }

    showPreview(previewData, fileType, fileName) {
        let previewHtml = '';
        
        if (fileType === 'pdf') {
            previewHtml = `
                <div class="mb-2">
                    <strong><i class="fas fa-file-pdf text-danger me-2"></i>${fileName}</strong>
                    <small class="text-muted d-block">PDF文档预览（第一页）</small>
                </div>
                <img src="data:image/png;base64,${previewData}" class="preview-image" alt="PDF预览">
            `;
        } else {
            previewHtml = `
                <div class="mb-2">
                    <strong><i class="fas fa-image text-primary me-2"></i>${fileName}</strong>
                    <small class="text-muted d-block">图片预览</small>
                </div>
                <img src="data:image/${fileType};base64,${previewData}" class="preview-image" alt="图片预览">
            `;
        }

        this.previewContent.innerHTML = previewHtml;
        this.previewContainer.style.display = 'block';
    }

    hidePreview() {
        this.previewContainer.style.display = 'none';
        this.previewContent.innerHTML = '';
    }

    showTextOutput(text) {
        this.currentText = text; // 保存当前文本
        if (text && text.trim()) {
            this.textOutput.innerHTML = `<pre style="white-space: pre-wrap; margin: 0;">${this.escapeHtml(text)}</pre>`;
            this.copyBtn.style.display = 'block';
            this.aiAnalysisBtn.style.display = 'block'; // 显示AI分析按钮
        } else {
            this.textOutput.innerHTML = `
                <div class="text-center text-muted mt-5">
                    <i class="fas fa-exclamation-triangle fa-2x mb-3"></i>
                    <p>未能识别到文本内容</p>
                    <small>请确保文档图像清晰，文字清楚可见</small>
                </div>
            `;
            this.copyBtn.style.display = 'none';
            this.aiAnalysisBtn.style.display = 'none'; // 隐藏AI分析按钮
        }
    }

    clearTextOutput() {
        this.currentText = ''; // 清空当前文本
        this.textOutput.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="fas fa-file-text fa-3x mb-3"></i>
                <p>上传文档后，识别的文本将显示在这里</p>
            </div>
        `;
        this.copyBtn.style.display = 'none';
        this.aiAnalysisBtn.style.display = 'none'; // 隐藏AI分析按钮
    }

    async copyText() {
        const textElement = this.textOutput.querySelector('pre');
        if (!textElement) return;

        try {
            await navigator.clipboard.writeText(textElement.textContent);
            this.showToast('文本已复制到剪贴板', 'success');
            
            // 临时改变按钮状态
            const originalHtml = this.copyBtn.innerHTML;
            this.copyBtn.innerHTML = '<i class="fas fa-check me-2"></i>已复制';
            this.copyBtn.classList.remove('btn-outline-primary');
            this.copyBtn.classList.add('btn-success');
            
            setTimeout(() => {
                this.copyBtn.innerHTML = originalHtml;
                this.copyBtn.classList.remove('btn-success');
                this.copyBtn.classList.add('btn-outline-primary');
            }, 2000);
        } catch (error) {
            console.error('Copy failed:', error);
            this.showToast('复制失败，请手动选择文本', 'error');
        }
    }

    showToast(message, type = 'info') {
        const iconMap = {
            success: 'fas fa-check-circle text-success',
            error: 'fas fa-exclamation-circle text-danger',
            info: 'fas fa-info-circle text-primary'
        };

        const icon = iconMap[type] || iconMap.info;
        
        // 更新toast图标
        const toastHeader = document.querySelector('#toast .toast-header i');
        toastHeader.className = `${icon} me-2`;
        
        this.toastBody.textContent = message;
        this.toast.show();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    openAIAnalysis() {
        if (!this.currentText || !this.currentText.trim()) {
            this.showToast('没有可分析的文本内容', 'warning');
            return;
        }
        
        // 编码文本内容作为URL参数
        const encodedContent = encodeURIComponent(this.currentText);
        
        // 打开AI分析页面并传递内容
        const analysisUrl = `/analysis.html?content=${encodedContent}`;
        window.open(analysisUrl, '_blank');
        
        this.showToast('已打开AI分析页面', 'info');
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OCRApp();
});