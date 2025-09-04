/**
 * API配置文件
 * 集中管理前端应用的后端API配置
 */

const CONFIG = {
    // 后端API基础URL
    API_BASE_URL: 'http://localhost:20010',
    
    // API端点
    ENDPOINTS: {
        UPLOAD: '/api/upload',
        AI_ANALYSIS: '/api/ai-analysis',
        ANALYSIS_TYPES: '/api/analysis-types'
    },
    
    // 其他配置
    MAX_FILE_SIZE: 16 * 1024 * 1024, // 16MB
    MAX_TEXT_LENGTH: 50000,
    ALLOWED_FILE_TYPES: ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
};

// 导出配置对象
window.CONFIG = CONFIG;