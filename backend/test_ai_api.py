#!/usr/bin/env python3
"""
AI分析API测试脚本
测试不同模型的API调用，并打印HTTP状态码和返回内容
"""
import requests
import json
import time
from typing import Dict, Any


class AIAPITester:
    """AI API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:20010"):
        """
        初始化测试器
        
        Args:
            base_url: 后端API基础URL
        """
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/api/ai-analysis"
        
        # 测试用例数据
        self.test_cases = [
            {
                "name": "短文本通用分析",
                "content": "今天是个好日子，阳光明媚，心情愉快。",
                "analysis_type": "general"
            },
            {
                "name": "长文本摘要",
                "content": """
                人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
                它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
                该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
                人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大，
                可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。
                """,
                "analysis_type": "summary"
            },
            {
                "name": "关键词提取",
                "content": "机器学习是人工智能的核心技术之一，通过算法让机器能够从数据中学习模式和规律。",
                "analysis_type": "extract"
            },
            {
                "name": "情感分析",
                "content": "这次购物体验非常糟糕，产品质量差，客服态度恶劣，强烈不推荐！",
                "analysis_type": "sentiment"
            }
        ]
    
    def test_health_check(self) -> bool:
        """
        测试健康检查接口
        
        Returns:
            是否通过健康检查
        """
        print("=" * 50)
        print("健康检查测试")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            print(f"健康检查失败: {e}")
            return False
    
    def test_ai_analysis(self, content: str, analysis_type: str, test_name: str) -> Dict[str, Any]:
        """
        测试AI分析接口
        
        Args:
            content: 测试内容
            analysis_type: 分析类型
            test_name: 测试名称
            
        Returns:
            测试结果
        """
        print(f"\n{'=' * 60}")
        print(f"测试用例: {test_name}")
        print(f"分析类型: {analysis_type}")
        print(f"内容长度: {len(content)} 字符")
        print(f"{'=' * 60}")
        
        payload = {
            "content": content.strip(),
            "analysis_type": analysis_type
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # 增加超时时间
            )
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应时间: {elapsed_time:.2f} 秒")
            print(f"响应头: {dict(response.headers)}")
            
            # 尝试解析JSON响应
            try:
                response_json = response.json()
                print(f"响应内容:")
                print(json.dumps(response_json, indent=2, ensure_ascii=False))
                
                # 如果成功，提取结果摘要
                if response_json.get('success') and 'data' in response_json:
                    result_text = response_json['data'].get('result', '')
                    if len(result_text) > 200:
                        print(f"\n分析结果摘要 (前200字符):")
                        print(result_text[:200] + "...")
                    
            except json.JSONDecodeError:
                print(f"响应内容 (非JSON): {response.text}")
            
            return {
                "test_name": test_name,
                "analysis_type": analysis_type,
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": elapsed_time,
                "content_length": len(content)
            }
            
        except requests.exceptions.Timeout:
            print("请求超时!")
            return {
                "test_name": test_name,
                "analysis_type": analysis_type,
                "status_code": 0,
                "success": False,
                "error": "timeout",
                "response_time": 120,
                "content_length": len(content)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return {
                "test_name": test_name,
                "analysis_type": analysis_type,
                "status_code": 0,
                "success": False,
                "error": str(e),
                "response_time": 0,
                "content_length": len(content)
            }
    
    def run_all_tests(self) -> None:
        """运行所有测试"""
        print("开始AI分析API测试")
        print(f"目标服务器: {self.base_url}")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 首先进行健康检查
        if not self.test_health_check():
            print("\n⚠️  健康检查失败，请确认服务器是否正常运行")
            return
        
        # 运行所有AI分析测试
        results = []
        for test_case in self.test_cases:
            result = self.test_ai_analysis(
                test_case["content"],
                test_case["analysis_type"],
                test_case["name"]
            )
            results.append(result)
            
            # 避免请求过于频繁
            time.sleep(1)
        
        # 输出测试总结
        self.print_summary(results)
    
    def print_summary(self, results: list) -> None:
        """
        打印测试总结
        
        Args:
            results: 测试结果列表
        """
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        
        print(f"\n详细结果:")
        print("-" * 80)
        for result in results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            print(f"{status} | {result['test_name']:20} | {result['analysis_type']:10} | "
                  f"{result['status_code']:3d} | {result['response_time']:6.2f}s")
        
        # 输出失败的测试详情
        failed_results = [r for r in results if not r['success']]
        if failed_results:
            print(f"\n失败测试详情:")
            print("-" * 80)
            for result in failed_results:
                print(f"❌ {result['test_name']} ({result['analysis_type']})")
                if 'error' in result:
                    print(f"   错误: {result['error']}")
                else:
                    print(f"   HTTP状态码: {result['status_code']}")
    
    def test_single_analysis_type(self, analysis_type: str) -> None:
        """
        测试特定的分析类型
        
        Args:
            analysis_type: 要测试的分析类型
        """
        test_content = "这是一个测试内容，用于验证AI分析功能是否正常工作。"
        
        result = self.test_ai_analysis(
            test_content,
            analysis_type,
            f"单独测试-{analysis_type}"
        )
        
        self.print_summary([result])


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI分析API测试工具")
    parser.add_argument("--url", default="http://localhost:20010", 
                       help="后端服务器URL (默认: http://localhost:20010)")
    parser.add_argument("--type", choices=["general", "summary", "extract", "sentiment"],
                       help="测试特定的分析类型")
    
    args = parser.parse_args()
    
    tester = AIAPITester(args.url)
    
    if args.type:
        # 测试特定类型
        tester.test_single_analysis_type(args.type)
    else:
        # 运行所有测试
        tester.run_all_tests()


if __name__ == "__main__":
    main()