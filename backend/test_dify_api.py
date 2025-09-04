#!/usr/bin/env python3
"""
测试Dify API调用格式
"""
import requests
import json

# 测试API调用
def test_dify_api():
    url = "https://api.dify.ai/v1/workflows/run"
    token = "app-dAUUqBRS185OrvicXgikgb8K"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": {
            "rec": "测试内容"
        },
        "response_mode": "blocking",
        "user": "test-user"
    }
    
    print("测试Dify API调用...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"解析后的响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print("API调用失败")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_dify_api()