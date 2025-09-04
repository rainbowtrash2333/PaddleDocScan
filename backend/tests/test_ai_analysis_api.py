#!/usr/bin/env python3
"""
AI分析API测试脚本
测试本地API服务器的AI分析功能
"""
import sys
import os
import requests
import json
import time
from typing import Dict, Any

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AIAPITester:
    """AI API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:20010"):
        """
        初始化测试器
        
        Args:
            base_url: 后端API基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_analysis_types_api(self) -> bool:
        """测试获取分析类型API"""
        print("=== 测试获取分析类型API ===")
        try:
            url = f"{self.base_url}/api/analysis-types"
            response = self.session.get(url, timeout=10)
            
            print(f"状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    print(f"可用的分析类型: {len(data['data'])}个")
                    for item in data['data']:
                        print(f"  - {item['id']}: {item['name']} - {item['description']}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    def test_ai_analysis_api(self, content: str, analysis_type: str = "general") -> bool:
        """测试AI分析API"""
        print(f"=== 测试AI分析API ({analysis_type}) ===")
        try:
            url = f"{self.base_url}/api/ai-analysis"
            payload = {
                "content": content,
                "analysis_type": analysis_type
            }
            
            print(f"请求URL: {url}")
            print(f"请求内容长度: {len(content)}")
            
            response = self.session.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {response.elapsed.total_seconds():.2f}秒")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应成功: {data.get('success', False)}")
                if data.get('success') and 'data' in data:
                    result_data = data['data']
                    print(f"分析结果长度: {len(str(result_data.get('result', '')))}")
                    print(f"分析结果预览: {str(result_data.get('result', ''))[:200]}...")
                    return True
            else:
                print(f"错误响应: {response.text}")
            
            return False
            
        except Exception as e:
            print(f"测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始AI分析API测试...")
        print(f"测试服务器: {self.base_url}")
        print("-" * 50)
        
        # 测试样本内容
        test_content = """
        人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
        它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
        该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
        """
        
        # 1. 测试分析类型获取
        types_success = self.test_analysis_types_api()
        print()
        
        if not types_success:
            print("获取分析类型失败，跳过后续测试")
            return
        
        # 2. 测试各种分析类型
        analysis_types = ["general", "summary", "extract", "sentiment"]
        
        for analysis_type in analysis_types:
            success = self.test_ai_analysis_api(test_content, analysis_type)
            print(f"{analysis_type} 分析测试: {'成功' if success else '失败'}")
            print()
            time.sleep(1)  # 避免请求过于频繁
        
        print("所有测试完成！")


def main():
    """主函数"""
    # 可以通过命令行参数指定服务器地址
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:20010"
    
    tester = AIAPITester(base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()