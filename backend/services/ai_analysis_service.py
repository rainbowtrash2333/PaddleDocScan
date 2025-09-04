"""
AI分析服务
直接调用Dify工作流API进行内容分析
"""
import logging
import requests
from typing import Dict, Any, Optional
from .exceptions import AIAnalysisError

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """AI分析服务类 - 直接调用Dify工作流"""
    
    def __init__(self, dify_models_config: Dict[str, Dict[str, str]] = None):
        """
        初始化AI分析服务
        
        Args:
            dify_models_config: Dify模型配置字典
        """
        self.dify_models = dify_models_config or {}
        self.timeout = 60  # 增加超时时间以适应AI响应
        
    def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        分析内容 - 直接调用指定类型的Dify模型
        
        Args:
            content: 要分析的文本内容
            analysis_type: 分析类型 (general, summary, extract, sentiment等)
            
        Returns:
            包含分析结果的字典
            
        Raises:
            AIAnalysisError: AI分析失败
        """
        if not content or not content.strip():
            raise AIAnalysisError("分析内容不能为空")
            
        if analysis_type not in self.dify_models:
            raise AIAnalysisError(f"不支持的分析类型: {analysis_type}")
            
        model_config = self.dify_models[analysis_type]
        if not model_config.get('token'):
            raise AIAnalysisError(f"分析类型 {analysis_type} 缺少API token配置")
            
        try:
            # 直接调用Dify API
            response = self._call_dify_api(content, model_config)
            
            # 处理响应
            result = self._process_response(response)
            
            logger.info(f"AI分析完成，内容长度: {len(content)}, 分析类型: {analysis_type}")
            
            return {
                "success": True,
                "analysis_type": analysis_type,
                "original_content_length": len(content),
                "result": result,
                "timestamp": self._get_timestamp()
            }
            
        except requests.RequestException as e:
            logger.error(f"Dify API请求失败: {e}")
            raise AIAnalysisError(f"AI服务请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"AI分析过程中发生错误: {e}")
            raise AIAnalysisError(f"AI分析失败: {str(e)}")
    
    def _call_dify_api(self, content: str, model_config: Dict[str, str]) -> Dict[str, Any]:
        """
        调用Dify工作流API
        
        Args:
            content: 输入内容
            model_config: 模型配置 (包含url和token)
            
        Returns:
            API响应结果
        """
        headers = {
            "Authorization": f"Bearer {model_config['token']}",
            "Content-Type": "application/json"
        }
        
        # 按照Dify官方API格式构建请求体
        payload = {
            "inputs": {
                "rec": content
            },
            "response_mode": "blocking", 
            "user": "paddle-doc-scan-user"
        }
        
        logger.info(f"调用Dify API: {model_config['url']}")
        logger.debug(f"请求头: {headers}")
        logger.debug(f"请求体: {payload}")
        
        response = requests.post(
            model_config['url'],
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        
        # 记录响应状态
        logger.info(f"API响应状态: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"API响应内容: {response.text}")
        
        response.raise_for_status()
        return response.json()
    
    def _process_response(self, response: Dict[str, Any]) -> str:
        """
        处理Dify API响应
        
        Args:
            response: API响应
            
        Returns:
            处理后的分析结果
        """
        # Dify工作流响应格式
        if "data" in response and "outputs" in response["data"]:
            outputs = response["data"]["outputs"]
            # 尝试获取结果，通常在result或answer字段
            if "result" in outputs:
                return str(outputs["result"])
            elif "answer" in outputs:
                return str(outputs["answer"])
            elif "output" in outputs:
                return str(outputs["output"])
            else:
                # 如果没有明确的结果字段，返回整个outputs
                return str(outputs)
        elif "answer" in response:
            return response["answer"]
        elif "result" in response:
            return response["result"]
        else:
            logger.warning(f"未识别的响应格式: {response}")
            return "AI分析完成，但未获取到具体结果"
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息
        
        Returns:
            服务信息字典
        """
        return {
            "service": "AI Analysis Service",
            "version": "2.0.0",
            "provider": "Dify",
            "available_models": list(self.dify_models.keys()),
            "status": "ready",
            "timeout": self.timeout
        }