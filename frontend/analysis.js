/**
 * AI分析页面JavaScript逻辑
 */

class AIAnalysis {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.isAnalyzing = false;
    }

    initializeElements() {
        // 获取页面元素
        this.contentInput = document.getElementById('contentInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.copyResultBtn = document.getElementById('copyResultBtn');
        this.charCounter = document.getElementById('charCounter');
        this.defaultMessage = document.getElementById('defaultMessage');
        this.loadingContainer = document.getElementById('loadingContainer');
        this.analysisResult = document.getElementById('analysisResult');
        this.toast = document.getElementById('toast');
        this.toastBody = document.getElementById('toastBody');
        
        // 初始化Bootstrap Toast
        this.toastInstance = new bootstrap.Toast(this.toast);
    }

    bindEvents() {
        // 内容输入事件
        this.contentInput.addEventListener('input', () => {
            this.updateCharCounter();
            this.updateAnalyzeButton();
        });

        // 分析按钮点击事件
        this.analyzeBtn.addEventListener('click', () => {
            this.performAnalysis();
        });

        // 清空按钮点击事件
        this.clearBtn.addEventListener('click', () => {
            this.clearContent();
        });

        // 复制结果按钮点击事件
        this.copyResultBtn.addEventListener('click', () => {
            this.copyResult();
        });

        // 键盘快捷键
        this.contentInput.addEventListener('keydown', (e) => {
            // Ctrl+Enter 触发分析
            if (e.ctrlKey && e.key === 'Enter') {
                if (!this.analyzeBtn.disabled && !this.isAnalyzing) {
                    this.performAnalysis();
                }
            }
        });

        // 页面加载时检查是否有URL参数传入的内容
        this.checkUrlParameters();
    }

    updateCharCounter() {
        const content = this.contentInput.value;
        const charCount = content.length;
        const maxChars = 50000;
        
        this.charCounter.textContent = `${charCount.toLocaleString()} / ${maxChars.toLocaleString()} 字符`;
        
        if (charCount > maxChars * 0.9) {
            this.charCounter.classList.add('warning');
        } else {
            this.charCounter.classList.remove('warning');
        }
    }

    updateAnalyzeButton() {
        const content = this.contentInput.value.trim();
        const isValid = content.length > 0 && content.length <= 50000 && !this.isAnalyzing;
        
        this.analyzeBtn.disabled = !isValid;
        
        if (content.length > 50000) {
            this.showToast('内容长度超过限制，最多支持50,000个字符', 'warning');
        }
    }

    async performAnalysis() {
        const content = this.contentInput.value.trim();
        
        if (!content) {
            this.showToast('请输入需要分析的内容', 'warning');
            return;
        }

        if (content.length > 50000) {
            this.showToast('内容长度超过限制，最多支持50,000个字符', 'error');
            return;
        }

        try {
            this.setAnalyzingState(true);
            
            const response = await fetch('/api/ai-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    analysis_type: 'general'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayAnalysisResult(result.data);
                this.showToast('AI分析完成！', 'success');
            } else {
                throw new Error(result.message || 'AI分析失败');
            }
        } catch (error) {
            console.error('AI分析错误:', error);
            this.displayError(error.message || 'AI分析服务暂时不可用，请稍后再试');
            this.showToast('AI分析失败: ' + (error.message || '服务暂时不可用'), 'error');
        } finally {
            this.setAnalyzingState(false);
        }
    }

    setAnalyzingState(analyzing) {
        this.isAnalyzing = analyzing;
        
        if (analyzing) {
            // 显示加载状态
            this.defaultMessage.style.display = 'none';
            this.analysisResult.classList.remove('show');
            this.loadingContainer.classList.add('show');
            this.copyResultBtn.style.display = 'none';
            
            // 禁用按钮
            this.analyzeBtn.disabled = true;
            this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>分析中...';
        } else {
            // 隐藏加载状态
            this.loadingContainer.classList.remove('show');
            
            // 恢复按钮
            this.analyzeBtn.innerHTML = '<i class="fas fa-magic me-2"></i>开始AI分析';
            this.updateAnalyzeButton();
        }
    }

    displayAnalysisResult(data) {
        // 隐藏默认消息和加载状态
        this.defaultMessage.style.display = 'none';
        this.loadingContainer.classList.remove('show');
        
        // 处理分析结果
        const result = data.result || '分析完成，但未获取到结果内容。';
        
        // 将Markdown格式的文本转换为HTML（简单实现）
        const htmlResult = this.markdownToHtml(result);
        
        // 显示结果
        this.analysisResult.innerHTML = htmlResult;
        this.analysisResult.classList.add('show');
        
        // 显示复制按钮
        this.copyResultBtn.style.display = 'inline-block';
        
        // 滚动到结果区域
        this.analysisResult.scrollTop = 0;
    }

    displayError(errorMessage) {
        this.defaultMessage.style.display = 'none';
        this.loadingContainer.classList.remove('show');
        
        this.analysisResult.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <h5>分析失败</h5>
                <p>${errorMessage}</p>
                <p class="text-muted small">请检查网络连接或稍后重试</p>
            </div>
        `;
        this.analysisResult.classList.add('show');
        this.copyResultBtn.style.display = 'none';
    }

    markdownToHtml(markdown) {
        // 简单的Markdown到HTML转换
        let html = markdown;
        
        // 标题转换
        html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // 粗体和斜体
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // 列表项
        html = html.replace(/^[\s]*[-\*\+]\s+(.*$)/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // 段落
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';
        
        // 清理空段落
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>\s*<h/g, '<h');
        html = html.replace(/<\/h([1-6])>\s*<\/p>/g, '</h$1>');
        html = html.replace(/<p>\s*<ul>/g, '<ul>');
        html = html.replace(/<\/ul>\s*<\/p>/g, '</ul>');
        
        return html;
    }

    clearContent() {
        if (this.contentInput.value.trim()) {
            if (confirm('确定要清空输入内容吗？')) {
                this.contentInput.value = '';
                this.updateCharCounter();
                this.updateAnalyzeButton();
                
                // 重置显示状态
                this.analysisResult.classList.remove('show');
                this.loadingContainer.classList.remove('show');
                this.defaultMessage.style.display = 'block';
                this.copyResultBtn.style.display = 'none';
            }
        }
    }

    async copyResult() {
        try {
            const resultText = this.analysisResult.textContent || this.analysisResult.innerText;
            await navigator.clipboard.writeText(resultText);
            this.showToast('分析结果已复制到剪贴板', 'success');
        } catch (error) {
            console.error('复制失败:', error);
            this.showToast('复制失败，请手动选择复制', 'error');
        }
    }

    checkUrlParameters() {
        // 检查URL参数，支持从其他页面传入内容
        const urlParams = new URLSearchParams(window.location.search);
        const content = urlParams.get('content');
        
        if (content) {
            this.contentInput.value = decodeURIComponent(content);
            this.updateCharCounter();
            this.updateAnalyzeButton();
        }
    }

    showToast(message, type = 'info') {
        // 设置Toast图标和样式
        const toastHeader = this.toast.querySelector('.toast-header i');
        toastHeader.className = 'me-2';
        
        switch (type) {
            case 'success':
                toastHeader.classList.add('fas', 'fa-check-circle', 'text-success');
                break;
            case 'error':
                toastHeader.classList.add('fas', 'fa-exclamation-circle', 'text-danger');
                break;
            case 'warning':
                toastHeader.classList.add('fas', 'fa-exclamation-triangle', 'text-warning');
                break;
            default:
                toastHeader.classList.add('fas', 'fa-info-circle', 'text-primary');
        }
        
        this.toastBody.textContent = message;
        this.toastInstance.show();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.aiAnalysis = new AIAnalysis();
});