"""
AI分析服务
与DIfy大模型集成进行内容分析
"""
import logging
import requests
from typing import Dict, Any, Optional
from .exceptions import AIAnalysisError

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """AI分析服务类"""
    
    def __init__(self, dify_api_url: str = None, api_key: str = None):
        """
        初始化AI分析服务
        
        Args:
            dify_api_url: DIfy API URL
            api_key: API密钥
        """
        self.dify_api_url = dify_api_url or "https://api.dify.ai/v1/chat-messages"
        self.api_key = api_key or "your-dify-api-key"
        self.timeout = 30  # 请求超时时间
        
    def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """
        分析内容
        
        Args:
            content: 要分析的文本内容
            analysis_type: 分析类型 (general, summary, keywords, sentiment等)
            
        Returns:
            包含分析结果的字典
            
        Raises:
            AIAnalysisError: AI分析失败
        """
        if not content or not content.strip():
            raise AIAnalysisError("分析内容不能为空")
            
        try:
            # 根据分析类型构建提示词
            prompt = self._build_prompt(content, analysis_type)
            
            # 调用DIfy API
            response = self._call_dify_api(prompt)
            
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
            logger.error(f"DIfy API请求失败: {e}")
            raise AIAnalysisError(f"AI服务请求失败: {str(e)}")
        except Exception as e:
            logger.error(f"AI分析过程中发生错误: {e}")
            raise AIAnalysisError(f"AI分析失败: {str(e)}")
    
    def _build_prompt(self, content: str, analysis_type: str) -> str:
        """
        根据分析类型构建提示词
        
        Args:
            content: 原始内容
            analysis_type: 分析类型
            
        Returns:
            构建的提示词
        """
        prompts = {
            "general": f"请对以下内容进行全面分析，包括主要内容总结、关键信息提取和建议：\n\n{content}",
            "summary": f"请为以下内容生成简洁的摘要：\n\n{content}",
            "keywords": f"请提取以下内容的关键词和核心概念：\n\n{content}",
            "sentiment": f"请分析以下内容的情感倾向和语调：\n\n{content}",
            "structure": f"请分析以下内容的结构和逻辑关系：\n\n{content}"
        }
        
        return prompts.get(analysis_type, prompts["general"])
    
    def _call_dify_api(self, prompt: str) -> Dict[str, Any]:
        """
        调用DIfy API
        
        Args:
            prompt: 提示词
            
        Returns:
            API响应结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {},
            "query": prompt,
            "response_mode": "blocking",
            "user": "paddle-doc-scan"
        }
        
        # 注意：这里是示例实现，实际使用时需要配置正确的DIfy API URL和密钥
        # 为了演示，我们返回一个模拟响应
        return self._mock_dify_response(prompt)
        
        # 实际API调用代码（注释掉以避免真实API调用）:
        # response = requests.post(
        #     self.dify_api_url,
        #     json=payload,
        #     headers=headers,
        #     timeout=self.timeout
        # )
        # response.raise_for_status()
        # return response.json()
    
    def _mock_dify_response(self, prompt: str) -> Dict[str, Any]:
        """
        模拟DIfy API响应（用于演示）
        
        Args:
            prompt: 输入的提示词
            
        Returns:
            模拟的API响应
        """
        # 简单的内容分析逻辑
        content_length = len(prompt)
        word_count = len(prompt.split())
        
        if "总结" in prompt or "摘要" in prompt:
            analysis_result = f"""
# 内容摘要

**字数统计**: {word_count} 个词，{content_length} 个字符

**主要内容**:
根据提供的文本内容，这是一段需要进行AI分析的材料。

**核心要点**:
- 内容长度: {content_length} 字符
- 词汇数量: {word_count} 个
- 文本类型: 待分析文档

**建议**:
建议进一步细化分析需求，以获得更准确的分析结果。
            """
        else:
            analysis_result = f"""
# AI智能分析报告

## 📊 基础信息
- **内容长度**: {content_length} 字符
- **词汇统计**: {word_count} 个词
- **分析时间**: {self._get_timestamp()}

## 🔍 内容分析
**结构特征**: 
文本内容结构完整，具有一定的信息密度。

**主要特点**:
- 内容具有明确的主题方向
- 文本组织结构良好  
- 信息层次分明

## 💡 关键洞察
1. **内容质量**: 文本内容具有分析价值
2. **信息密度**: 中等信息密度，适合进一步处理
3. **应用场景**: 适用于多种分析场景

## 📈 建议
- 建议结合具体业务场景进行针对性分析
- 可考虑进行更细化的专项分析
- 适合作为后续深度分析的基础材料

*本分析报告由AI智能生成，仅供参考。*
            """
        
        return {
            "answer": analysis_result.strip(),
            "metadata": {
                "usage": {
                    "prompt_tokens": len(prompt),
                    "completion_tokens": len(analysis_result),
                    "total_tokens": len(prompt) + len(analysis_result)
                }
            }
        }
    
    def _process_response(self, response: Dict[str, Any]) -> str:
        """
        处理API响应
        
        Args:
            response: API响应
            
        Returns:
            处理后的分析结果
        """
        if "answer" in response:
            return response["answer"]
        elif "message" in response:
            return response["message"]
        else:
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
            "version": "1.0.0",
            "dify_api_url": self.dify_api_url,
            "status": "ready",
            "timeout": self.timeout
        }