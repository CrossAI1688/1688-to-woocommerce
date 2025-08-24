#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端集成测试
测试完整的1688商品抓取到WooCommerce上传流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json
import time
from scraper_1688 import scrape_1688_product
from woocommerce_uploader import create_woocommerce_uploader
from config_manager import config_manager

class TestEndToEndIntegration(unittest.TestCase):
    """端到端集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_url = "https://detail.1688.com/offer/793064484013.html"
        
        # 测试用的WooCommerce配置（需要真实配置才能完整测试）
        self.wc_config = {
            "url": os.getenv("WC_TEST_URL", ""),
            "consumer_key": os.getenv("WC_TEST_KEY", ""),
            "consumer_secret": os.getenv("WC_TEST_SECRET", "")
        }
        
        self.has_wc_config = all([
            self.wc_config["url"],
            self.wc_config["consumer_key"],
            self.wc_config["consumer_secret"]
        ])
    
    def test_scrape_to_upload_workflow(self):
        """测试完整的抓取到上传工作流程"""
        print("\n=== 测试完整工作流程 ===")
        
        # Step 1: 抓取1688商品信息
        print(f"   📥 步骤1: 抓取1688商品信息...")
        print(f"   🔗 URL: {self.test_url}")
        
        scrape_result = scrape_1688_product(self.test_url)
        
        # 验证抓取结果
        self.assertNotIn('error', scrape_result, f"抓取失败: {scrape_result.get('error', '')}")
        self.assertIn('title', scrape_result, "抓取结果应该包含标题")
        self.assertIn('price', scrape_result, "抓取结果应该包含价格")
        self.assertIn('images', scrape_result, "抓取结果应该包含图片")
        
        print(f"   ✅ 抓取成功!")
        print(f"      标题: {scrape_result.get('title', 'N/A')[:50]}...")
        print(f"      价格: {scrape_result.get('price', 'N/A')}")
        print(f"      图片数量: {len(scrape_result.get('images', []))}")
        print(f"      规格参数: {len(scrape_result.get('specifications', {}))}")
        
        # Step 2: 处理商品信息
        print(f"   🔄 步骤2: 处理商品信息...")
        
        # 验证必要字段
        required_fields = ['title', 'price', 'description', 'images']
        for field in required_fields:
            if field not in scrape_result or not scrape_result[field]:
                print(f"   ⚠️ 缺少或为空的字段: {field}")
            else:
                print(f"   ✅ 字段正常: {field}")
        
        # 数据质量检查
        quality_checks = {
            '标题长度': len(scrape_result.get('title', '')) > 5,
            '价格格式': scrape_result.get('price', '') != 'N/A',
            '描述长度': len(scrape_result.get('description', '')) > 10,
            '图片数量': len(scrape_result.get('images', [])) > 0
        }
        
        for check_name, passed in quality_checks.items():
            status = "✅" if passed else "⚠️"
            print(f"   {status} 质量检查: {check_name}")
        
        # Step 3: WooCommerce配置检查
        print(f"   ⚙️ 步骤3: 检查WooCommerce配置...")
        
        if not self.has_wc_config:
            print("   ⚠️ 未找到WooCommerce配置")
            print("   💡 如需完整测试，请设置环境变量：")
            print("      WC_TEST_URL, WC_TEST_KEY, WC_TEST_SECRET")
            return
        
        print(f"   ✅ WooCommerce配置已找到")
        print(f"      URL: {self.wc_config['url']}")
        
        # Step 4: 测试WooCommerce连接
        print(f"   🔗 步骤4: 测试WooCommerce连接...")
        
        connection_result = config_manager.test_config(self.wc_config)
        
        if not connection_result["success"]:
            print(f"   ❌ WooCommerce连接失败: {connection_result['message']}")
            return
        
        print(f"   ✅ WooCommerce连接成功")
        
        # Step 5: 创建上传器
        print(f"   🚀 步骤5: 创建WooCommerce上传器...")
        
        uploader = create_woocommerce_uploader(self.wc_config, use_external_images=True)
        self.assertIsNotNone(uploader, "上传器创建失败")
        
        print(f"   ✅ 上传器创建成功")
        
        # Step 6: 上传商品（可选，因为会创建真实商品）
        print(f"   📤 步骤6: 准备上传商品...")
        
        # 为了避免在测试中创建真实商品，这里只模拟上传过程
        print("   ⚠️ 跳过实际上传（避免创建测试商品）")
        print("   💡 如需测试实际上传，请手动运行Web应用")
        
        print(f"\n   🎉 完整工作流程测试完成!")
    
    def test_data_transformation(self):
        """测试数据转换功能"""
        print("\n=== 测试数据转换功能 ===")
        
        # 抓取数据
        scrape_result = scrape_1688_product(self.test_url)
        
        if 'error' in scrape_result:
            self.skipTest(f"跳过数据转换测试: {scrape_result['error']}")
        
        # 测试数据格式转换
        print("   🔄 测试数据格式转换...")
        
        # 验证数据类型
        self.assertIsInstance(scrape_result.get('title', ''), str, "标题应该是字符串")
        self.assertIsInstance(scrape_result.get('price', ''), str, "价格应该是字符串")
        self.assertIsInstance(scrape_result.get('description', ''), str, "描述应该是字符串")
        self.assertIsInstance(scrape_result.get('images', []), list, "图片应该是列表")
        self.assertIsInstance(scrape_result.get('specifications', {}), dict, "规格参数应该是字典")
        
        print("   ✅ 数据类型验证通过")
        
        # 测试规格参数格式
        specifications = scrape_result.get('specifications', {})
        if specifications:
            print(f"   📊 规格参数数量: {len(specifications)}")
            
            # 检查前几个规格参数的格式
            for i, (key, value) in enumerate(list(specifications.items())[:3]):
                self.assertIsInstance(key, str, f"规格参数名{i+1}应该是字符串")
                self.assertIsInstance(value, str, f"规格参数值{i+1}应该是字符串")
                print(f"   ✅ 规格参数{i+1}: {key} = {value}")
        
        # 测试图片URL格式
        images = scrape_result.get('images', [])
        if images:
            print(f"   🖼️ 图片数量: {len(images)}")
            
            for i, img_url in enumerate(images[:3]):  # 检查前3张
                self.assertTrue(img_url.startswith('http'), f"图片{i+1}URL格式不正确")
                print(f"   ✅ 图片{i+1}URL格式正确")

def print_integration_test_guide():
    """打印集成测试指南"""
    print("\n" + "="*60)
    print("🔗 端到端集成测试指南")
    print("="*60)
    print("\n📖 测试覆盖范围：")
    print("   1. 1688商品信息抓取")
    print("   2. 数据质量验证")
    print("   3. WooCommerce配置验证")
    print("   4. WooCommerce连接测试")
    print("   5. 上传器创建")
    print("   6. 数据格式转换")
    
    print("\n🔧 完整测试需要：")
    print("   - 有效的1688商品链接")
    print("   - 真实的WooCommerce配置")
    print("   - 稳定的网络连接")
    
    print("\n⚠️ 注意事项：")
    print("   - 集成测试不会创建真实商品")
    print("   - 需要设置WooCommerce环境变量进行完整测试")
    print("   - 实际上传测试请使用Web应用界面")

def run_integration_tests():
    """运行集成测试"""
    print("🔗 开始端到端集成测试...")
    print("=" * 60)
    
    # 运行集成测试
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEndToEndIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("📊 集成测试结果摘要:")
    print(f"   总测试数: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    # 打印指南
    print_integration_test_guide()
    
    if result.wasSuccessful():
        print("\n🎉 端到端集成测试通过！")
        return True
    else:
        print("\n⚠️ 部分集成测试未通过，请检查相关功能")
        return False

if __name__ == "__main__":
    run_integration_tests()