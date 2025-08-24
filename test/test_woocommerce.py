#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WooCommerce连接和配置测试
测试config_manager和woocommerce_uploader模块功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from config_manager import config_manager
from woocommerce_uploader import create_woocommerce_uploader
import json

class TestWooCommerceConfig(unittest.TestCase):
    """WooCommerce配置测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 测试配置（无效配置，用于测试）
        self.invalid_configs = [
            # 无效URL格式
            {
                "url": "invalid-url",
                "consumer_key": "test_key",
                "consumer_secret": "test_secret"
            },
            # 缺少必要字段
            {
                "url": "https://test-site.com",
                "consumer_key": "",
                "consumer_secret": "test_secret"
            },
            # Consumer Key过短
            {
                "url": "https://test-site.com",
                "consumer_key": "short",
                "consumer_secret": "test_secret_123456789"
            },
            # Consumer Secret过短
            {
                "url": "https://test-site.com",
                "consumer_key": "test_key_123456789",
                "consumer_secret": "short"
            }
        ]
        
        # 有效格式的测试配置（但可能无法连接）
        self.valid_format_config = {
            "url": "https://demo.woocommerce.com",
            "consumer_key": "ck_test_123456789abcdef",
            "consumer_secret": "cs_test_123456789abcdef"
        }
    
    def test_config_validation(self):
        """测试配置验证功能"""
        print("\n=== 测试配置验证功能 ===")
        
        # 测试无效配置
        for i, config in enumerate(self.invalid_configs, 1):
            print(f"\n{i}. 测试无效配置...")
            result = config_manager.test_config(config)
            
            # 无效配置应该返回失败
            self.assertFalse(result["success"], f"无效配置{i}应该验证失败")
            self.assertIn("message", result, "应该包含错误消息")
            print(f"   ✅ 正确识别无效配置: {result['message']}")
    
    def test_valid_format_config(self):
        """测试有效格式配置"""
        print("\n=== 测试有效格式配置 ===")
        
        result = config_manager.test_config(self.valid_format_config)
        
        # 检查结果结构
        self.assertIn("success", result, "结果应该包含success字段")
        self.assertIn("message", result, "结果应该包含message字段")
        
        if result["success"]:
            print("   ✅ 配置格式有效，连接成功")
        else:
            print(f"   ⚠️ 配置格式有效，但连接失败: {result['message']}")
            # 这是正常的，因为使用的是测试配置
    
    def test_uploader_creation(self):
        """测试上传器创建功能"""
        print("\n=== 测试上传器创建功能 ===")
        
        # 测试有效格式配置创建上传器
        uploader = create_woocommerce_uploader(self.valid_format_config)
        
        if uploader:
            print("   ✅ 上传器创建成功")
            self.assertIsNotNone(uploader, "上传器不应该为None")
        else:
            print("   ⚠️ 上传器创建失败（可能是因为测试配置无效）")
        
        # 测试无效配置创建上传器
        uploader_invalid = create_woocommerce_uploader(self.invalid_configs[0])
        self.assertIsNone(uploader_invalid, "无效配置应该返回None")
        print("   ✅ 无效配置正确返回None")

class TestWooCommerceConnection(unittest.TestCase):
    """WooCommerce真实连接测试类（需要真实配置）"""
    
    def setUp(self):
        """测试前准备"""
        # 尝试从环境变量读取真实配置
        self.real_config = {
            "url": os.getenv("WC_TEST_URL", ""),
            "consumer_key": os.getenv("WC_TEST_KEY", ""),
            "consumer_secret": os.getenv("WC_TEST_SECRET", "")
        }
        
        # 检查是否有真实配置
        self.has_real_config = all([
            self.real_config["url"],
            self.real_config["consumer_key"],
            self.real_config["consumer_secret"]
        ])
    
    def test_real_connection(self):
        """测试真实连接（如果有配置的话）"""
        print("\n=== 测试真实WooCommerce连接 ===")
        
        if not self.has_real_config:
            print("   ⚠️ 未找到真实WooCommerce配置")
            print("   💡 如需测试真实连接，请设置环境变量：")
            print("      WC_TEST_URL=你的WooCommerce网站URL")
            print("      WC_TEST_KEY=你的Consumer Key")
            print("      WC_TEST_SECRET=你的Consumer Secret")
            self.skipTest("跳过真实连接测试：未配置真实WooCommerce信息")
        
        print(f"   🔗 测试连接到: {self.real_config['url']}")
        result = config_manager.test_config(self.real_config)
        
        if result["success"]:
            print("   ✅ 真实连接测试成功！")
            if "details" in result:
                print(f"   📊 详细信息: {result['details']}")
        else:
            print(f"   ❌ 真实连接测试失败: {result['message']}")
            if "details" in result:
                print(f"   📋 错误详情: {result['details']}")
        
        # 测试结果应该包含正确的字段
        self.assertIn("success", result)
        self.assertIn("message", result)

def print_connection_test_guide():
    """打印连接测试指南"""
    print("\n" + "="*60)
    print("📖 WooCommerce连接测试指南")
    print("="*60)
    print("\n🔧 如何进行真实连接测试：")
    print("\n1. 在你的WooCommerce网站中创建API密钥：")
    print("   - 登录WordPress后台")
    print("   - 导航至 WooCommerce > 设置 > 高级 > REST API")
    print("   - 点击'添加密钥'")
    print("   - 权限选择'读/写'")
    print("   - 复制生成的Consumer Key和Consumer Secret")
    
    print("\n2. 设置环境变量（Windows）：")
    print("   set WC_TEST_URL=https://your-site.com")
    print("   set WC_TEST_KEY=ck_your_consumer_key")
    print("   set WC_TEST_SECRET=cs_your_consumer_secret")
    
    print("\n3. 设置环境变量（Linux/Mac）：")
    print("   export WC_TEST_URL=https://your-site.com")
    print("   export WC_TEST_KEY=ck_your_consumer_key")
    print("   export WC_TEST_SECRET=cs_your_consumer_secret")
    
    print("\n4. 重新运行测试：")
    print("   python test_woocommerce.py")
    
    print("\n⚠️ 注意事项：")
    print("   - 确保WooCommerce网站可以从外网访问")
    print("   - 确保API密钥权限设置为'读/写'")
    print("   - 确保WordPress和WooCommerce插件是最新版本")

def run_woocommerce_tests():
    """运行WooCommerce测试"""
    print("🏪 开始WooCommerce功能测试...")
    print("=" * 60)
    
    # 运行配置测试
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestWooCommerceConfig)
    runner = unittest.TextTestRunner(verbosity=2)
    result1 = runner.run(suite1)
    
    # 运行连接测试
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestWooCommerceConnection)
    result2 = runner.run(suite2)
    
    # 合并结果
    total_tests = result1.testsRun + result2.testsRun
    total_failures = len(result1.failures) + len(result2.failures)
    total_errors = len(result1.errors) + len(result2.errors)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("📊 WooCommerce测试结果摘要:")
    print(f"   总测试数: {total_tests}")
    print(f"   成功: {total_tests - total_failures - total_errors}")
    print(f"   失败: {total_failures}")
    print(f"   错误: {total_errors}")
    
    # 打印指南
    print_connection_test_guide()
    
    success = (total_failures + total_errors) == 0
    if success:
        print("\n🎉 WooCommerce功能测试通过！")
    else:
        print("\n⚠️ 部分WooCommerce测试未通过，请检查相关功能")
    
    return success

if __name__ == "__main__":
    run_woocommerce_tests()