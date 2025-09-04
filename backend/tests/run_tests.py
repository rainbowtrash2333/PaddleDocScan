#!/usr/bin/env python3
"""
测试运行器
统一运行所有测试脚本
"""
import sys
import os
import subprocess
import time

def run_test(test_file, description):
    """运行单个测试文件"""
    print(f"\n{'='*60}")
    print(f"运行测试: {description}")
    print(f"测试文件: {test_file}")
    print(f"{'='*60}")
    
    try:
        # 切换到tests目录
        test_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(test_dir)
        
        # 运行测试
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"\n✓ {description} - 测试通过")
            return True
        else:
            print(f"\n✗ {description} - 测试失败 (退出码: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n✗ {description} - 测试超时")
        return False
    except Exception as e:
        print(f"\n✗ {description} - 测试异常: {e}")
        return False

def main():
    """主函数"""
    print("PaddleDocScan 测试套件")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 定义测试列表
    tests = [
        ("test_dify_integration.py", "Dify API集成测试"),
        ("test_ai_analysis_api.py", "AI分析API测试"),
        ("test_ocr_service.py", "OCR服务测试"),
    ]
    
    results = []
    
    for test_file, description in tests:
        print(f"\n准备运行: {description}")
        time.sleep(1)
        
        success = run_test(test_file, description)
        results.append((description, success))
        
        time.sleep(2)  # 测试间隔
    
    # 总结报告
    print(f"\n{'='*60}")
    print("测试结果总结")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{description}: {status}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {passed/len(results)*100:.1f}%")
    
    print(f"\n结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 如果有失败的测试，返回非零退出码
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()