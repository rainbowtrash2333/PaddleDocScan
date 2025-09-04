#!/usr/bin/env python3
"""
Dify API集成测试
直接测试Dify工作流API的调用格式和响应
"""
import sys
import os
import requests
import json
import time

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dify_api():
    """测试Dify API调用"""
    print("=== 测试Dify工作流API ===")
    
    url = "https://api.dify.ai/v1/workflows/run"
    token = "app-dAUUqBRS185OrvicXgikgb8K"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 按照Dify官方API格式构建请求体
    payload = {
        "inputs": {
            "rec": "测试内容：这是一个测试文本，用于验证Dify工作流API的调用格式。"
        },
        "response_mode": "blocking",
        "user": "test-user"
    }
    
    print(f"请求URL: {url}")
    print(f"请求头: {json.dumps(headers, indent=2, ensure_ascii=False)}")
    print(f"请求体: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        print("\n发送请求...")
        start_time = time.time()
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=30
        )
        
        end_time = time.time()
        
        print(f"响应时间: {end_time - start_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"响应成功!")
                print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                # 尝试提取结果
                if "data" in result and "outputs" in result["data"]:
                    outputs = result["data"]["outputs"]
                    print(f"\n工作流输出: {outputs}")
                else:
                    print("\n未找到预期的输出格式")
                    
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始响应内容: {response.text}")
        else:
            print(f"请求失败!")
            print(f"错误响应: {response.text}")
            
            # 分析常见错误
            if response.status_code == 401:
                print("可能的原因: API Token无效或已过期")
            elif response.status_code == 400:
                print("可能的原因: 请求格式错误或参数不正确")
            elif response.status_code == 404:
                print("可能的原因: 工作流不存在或URL错误")
                
    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.ConnectionError:
        print("连接错误，请检查网络")
    except Exception as e:
        print(f"请求异常: {e}")

def test_different_inputs():
    """测试不同的输入参数"""
    print("\n=== 测试不同输入格式 ===")
    
    # 测试用例
    test_cases = [
        {
            "name": "标准文本输入",
            "inputs": {"rec": "这是一个标准的文本分析测试。"}
        },
        {
            "name": "空输入测试", 
            "inputs": {"rec": ""}
        },
        {
            "name": "长文本测试",
            "inputs": {"rec": "这是一个很长的测试文本。" * 100}
        }
    ]
    
    url = "https://api.dify.ai/v1/workflows/run"
    token = "app-dAUUqBRS185OrvicXgikgb8K"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        payload = {
            "inputs": test_case["inputs"],
            "response_mode": "blocking",
            "user": f"test-user-{i}"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✓ 测试通过")
            else:
                print(f"  ✗ 测试失败: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ✗ 请求异常: {e}")
        
        time.sleep(1)  # 避免请求过于频繁

def main():
    """主函数"""
    print("Dify API集成测试开始...")
    print("=" * 50)
    
    # 基础API测试
    test_dify_api()
    
    # 不同输入测试
    test_different_inputs()
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()