#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主测试运行器
统一运行所有测试模块，生成完整的测试报告
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入各个测试模块
try:
    from test_scraper_1688 import run_scraper_tests
except ImportError as e:
    print(f"⚠️ 无法导入1688抓取测试: {e}")
    run_scraper_tests = None

try:
    from test_woocommerce import run_woocommerce_tests
except ImportError as e:
    print(f"⚠️ 无法导入WooCommerce测试: {e}")
    run_woocommerce_tests = None

try:
    from test_cookie_storage import run_cookie_storage_tests
except ImportError as e:
    print(f"⚠️ 无法导入Cookie存储测试: {e}")
    run_cookie_storage_tests = None

try:
    from test_integration import run_integration_tests
except ImportError as e:
    print(f"⚠️ 无法导入集成测试: {e}")
    run_integration_tests = None

def print_header():
    """打印测试开始头部信息"""
    print("=" * 80)
    print("🧪 1688商品同步到WooCommerce工具 - 全面测试套件")
    print("=" * 80)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 项目目录: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    print("=" * 80)

def print_test_menu():
    """打印测试菜单"""
    print("\n🎯 可用的测试模块:")
    print("   1. 1688商品抓取功能测试")
    print("   2. WooCommerce连接和配置测试")
    print("   3. Cookie存储功能测试")
    print("   4. 端到端集成测试")
    print("   5. 运行所有测试")
    print("   0. 退出")

def run_single_test(test_name, test_function):
    """运行单个测试模块"""
    print(f"\n{'='*60}")
    print(f"🧪 开始运行: {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        if test_function:
            success = test_function()
            end_time = time.time()
            duration = end_time - start_time
            
            status = "✅ 通过" if success else "⚠️ 部分失败"
            print(f"\n📊 {test_name} 测试结果: {status}")
            print(f"⏱️ 耗时: {duration:.2f}秒")
            
            return success
        else:
            print(f"❌ 无法运行 {test_name}: 模块未正确导入")
            return False
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n💥 {test_name} 测试出现异常: {str(e)}")
        print(f"⏱️ 耗时: {duration:.2f}秒")
        return False

def run_all_tests():
    """运行所有测试"""
    print(f"\n{'='*60}")
    print("🚀 开始运行全部测试...")
    print(f"{'='*60}")
    
    total_start_time = time.time()
    test_results = {}
    
    # 定义测试模块
    test_modules = [
        ("1688商品抓取功能测试", run_scraper_tests),
        ("WooCommerce连接和配置测试", run_woocommerce_tests),
        ("Cookie存储功能测试", run_cookie_storage_tests),
        ("端到端集成测试", run_integration_tests)
    ]
    
    # 运行每个测试模块
    for test_name, test_function in test_modules:
        print(f"\n{'-'*40}")
        success = run_single_test(test_name, test_function)
        test_results[test_name] = success
        print(f"{'-'*40}")
        
        # 模块间暂停一下
        time.sleep(1)
    
    # 计算总耗时
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # 生成测试报告
    generate_test_report(test_results, total_duration)
    
    return test_results

def generate_test_report(test_results, total_duration):
    """生成测试报告"""
    print(f"\n{'='*80}")
    print("📋 测试报告汇总")
    print(f"{'='*80}")
    
    # 统计结果
    total_tests = len(test_results)
    passed_tests = sum(1 for success in test_results.values() if success)
    failed_tests = total_tests - passed_tests
    
    print(f"📊 测试统计:")
    print(f"   总测试模块: {total_tests}")
    print(f"   通过模块: {passed_tests}")
    print(f"   失败模块: {failed_tests}")
    print(f"   成功率: {(passed_tests/total_tests*100):.1f}%")
    print(f"   总耗时: {total_duration:.2f}秒")
    
    print(f"\n📋 详细结果:")
    for test_name, success in test_results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"   {status} {test_name}")
    
    # 生成建议
    print(f"\n💡 建议:")
    if failed_tests == 0:
        print("   🎉 所有测试都通过了！系统功能正常。")
    else:
        print("   ⚠️ 部分测试未通过，请检查:")
        for test_name, success in test_results.items():
            if not success:
                print(f"      - {test_name}")
    
    # 保存测试报告到文件
    save_test_report(test_results, total_duration)

def save_test_report(test_results, total_duration):
    """保存测试报告到文件"""
    try:
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = os.path.join(os.path.dirname(__file__), report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("1688商品同步到WooCommerce工具 - 测试报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总耗时: {total_duration:.2f}秒\n\n")
            
            # 统计信息
            total_tests = len(test_results)
            passed_tests = sum(1 for success in test_results.values() if success)
            failed_tests = total_tests - passed_tests
            
            f.write("测试统计:\n")
            f.write(f"  总测试模块: {total_tests}\n")
            f.write(f"  通过模块: {passed_tests}\n")
            f.write(f"  失败模块: {failed_tests}\n")
            f.write(f"  成功率: {(passed_tests/total_tests*100):.1f}%\n\n")
            
            # 详细结果
            f.write("详细结果:\n")
            for test_name, success in test_results.items():
                status = "通过" if success else "失败"
                f.write(f"  {status}: {test_name}\n")
        
        print(f"\n💾 测试报告已保存: {report_path}")
        
    except Exception as e:
        print(f"\n⚠️ 保存测试报告失败: {e}")

def print_environment_info():
    """打印环境信息"""
    print(f"\n{'='*60}")
    print("🔧 环境信息检查")
    print(f"{'='*60}")
    
    # 检查Python环境
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查必要的包
    required_packages = [
        'streamlit', 'beautifulsoup4', 'requests', 
        'woocommerce', 'pandas', 'pillow'
    ]
    
    print(f"\n📦 依赖包检查:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
    
    # 检查环境变量
    print(f"\n🔧 环境变量检查:")
    env_vars = ['WC_TEST_URL', 'WC_TEST_KEY', 'WC_TEST_SECRET']
    for var in env_vars:
        value = os.getenv(var, '')
        if value:
            # 隐藏敏感信息
            display_value = value[:10] + "***" if len(value) > 10 else "***"
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️ {var}: 未设置")

def main():
    """主函数"""
    print_header()
    print_environment_info()
    
    while True:
        print_test_menu()
        
        try:
            choice = input("\n🎯 请选择要运行的测试 (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 测试退出")
                break
            elif choice == "1":
                run_single_test("1688商品抓取功能测试", run_scraper_tests)
            elif choice == "2":
                run_single_test("WooCommerce连接和配置测试", run_woocommerce_tests)
            elif choice == "3":
                run_single_test("Cookie存储功能测试", run_cookie_storage_tests)
            elif choice == "4":
                run_single_test("端到端集成测试", run_integration_tests)
            elif choice == "5":
                run_all_tests()
            else:
                print("❌ 无效选择，请输入 0-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 测试被用户中断")
            break
        except Exception as e:
            print(f"\n💥 发生错误: {e}")

if __name__ == "__main__":
    main()