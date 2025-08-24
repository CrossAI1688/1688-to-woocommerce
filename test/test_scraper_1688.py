#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688商品抓取功能测试
测试scraper_1688模块的各项功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from scraper_1688 import scrape_1688_product
import json
import time

class Test1688Scraper(unittest.TestCase):
    """1688抓取器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_urls = [
            "https://detail.1688.com/offer/793064484013.html",
            "https://detail.1688.com/offer/825677770251.html",
            "https://detail.1688.com/offer/800015139408.html"
        ]
        
    def test_basic_scraping(self):
        """测试基本抓取功能"""
        print("\n=== 测试基本抓取功能 ===")
        
        for i, url in enumerate(self.test_urls, 1):
            print(f"\n{i}. 测试URL: {url}")
            
            try:
                result = scrape_1688_product(url)
                
                # 检查结果是否包含错误
                self.assertNotIn('error', result, f"抓取URL {url} 时出现错误: {result.get('error', '')}")
                
                # 检查必需字段
                required_fields = ['title', 'price', 'url', 'product_id']
                for field in required_fields:
                    self.assertIn(field, result, f"缺少必需字段: {field}")
                    self.assertIsNotNone(result[field], f"字段 {field} 为None")
                    self.assertNotEqual(result[field], 'N/A', f"字段 {field} 为N/A")
                
                # 打印抓取结果摘要
                print(f"   ✅ 标题: {result.get('title', 'N/A')[:50]}...")
                print(f"   ✅ 价格: {result.get('price', 'N/A')}")
                print(f"   ✅ 图片数量: {len(result.get('images', []))}")
                print(f"   ✅ 规格参数数量: {len(result.get('specifications', {}))}")
                print(f"   ✅ 描述长度: {len(result.get('description', ''))}")
                
                # 验证抓取质量
                self.assertGreater(len(result.get('title', '')), 5, "标题太短")
                self.assertGreater(len(result.get('images', [])), 0, "没有抓取到图片")
                
            except Exception as e:
                self.fail(f"抓取URL {url} 时发生异常: {str(e)}")
                
            # 避免请求过快
            time.sleep(2)
    
    def test_image_extraction(self):
        """测试图片提取功能"""
        print("\n=== 测试图片提取功能 ===")
        
        url = self.test_urls[0]
        result = scrape_1688_product(url)
        
        images = result.get('images', [])
        self.assertGreater(len(images), 0, "没有提取到任何图片")
        
        # 检查图片URL格式
        for i, img_url in enumerate(images[:3]):  # 只检查前3张
            self.assertTrue(img_url.startswith('http'), f"图片{i+1}的URL格式不正确: {img_url}")
            print(f"   ✅ 图片{i+1}: {img_url}")
    
    def test_specifications_extraction(self):
        """测试规格参数提取功能"""
        print("\n=== 测试规格参数提取功能 ===")
        
        url = self.test_urls[0]
        result = scrape_1688_product(url)
        
        specifications = result.get('specifications', {})
        print(f"   提取到 {len(specifications)} 个规格参数")
        
        if specifications:
            # 打印前5个规格参数
            for i, (key, value) in enumerate(list(specifications.items())[:5]):
                print(f"   ✅ {key}: {value}")
                self.assertIsInstance(key, str, "规格参数名应该是字符串")
                self.assertIsInstance(value, str, "规格参数值应该是字符串")
        else:
            print("   ⚠️ 未提取到规格参数")
    
    def test_mobile_fallback(self):
        """测试移动版降级功能"""
        print("\n=== 测试移动版降级功能 ===")
        
        # 使用一个可能在桌面版抓取困难的URL
        url = self.test_urls[1]
        result = scrape_1688_product(url)
        
        self.assertNotIn('error', result, f"移动版降级失败: {result.get('error', '')}")
        print(f"   ✅ 移动版降级成功")
        print(f"   ✅ 标题: {result.get('title', 'N/A')[:50]}...")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        invalid_urls = [
            "https://invalid-url.com",
            "https://detail.1688.com/offer/invalid.html",
            "not-a-url"
        ]
        
        for url in invalid_urls:
            print(f"   测试无效URL: {url}")
            result = scrape_1688_product(url)
            
            # 无效URL应该返回错误信息
            if 'error' in result:
                print(f"   ✅ 正确处理了无效URL: {result['error']}")
            else:
                print(f"   ⚠️ 无效URL未返回错误，可能需要检查")

def run_scraper_tests():
    """运行抓取器测试"""
    print("🔍 开始1688抓取功能测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(Test1688Scraper)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("📊 测试结果摘要:")
    print(f"   总测试数: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失败: {len(result.failures)}")
    print(f"   错误: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n🎉 所有抓取功能测试通过！")
        return True
    else:
        print("\n⚠️ 部分测试未通过，请检查相关功能")
        return False

if __name__ == "__main__":
    run_scraper_tests()