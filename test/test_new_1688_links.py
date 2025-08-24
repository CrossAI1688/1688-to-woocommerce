#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688新商品链接抓取测试
测试用户提供的具体商品链接的抓取效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper_1688 import scrape_1688_product
import time
import json
from datetime import datetime

class New1688LinkTester:
    """新1688链接测试器"""
    
    def __init__(self):
        # 用户提供的测试链接
        self.test_links = [
            "https://detail.1688.com/offer/846064965230.html?spm=a2637j.22917583.home-list.d_846064965230.63dc24feH9cCpj",
            "https://detail.1688.com/offer/700617772348.html?spm=a2637j.22917583.home-list.d_700617772348.63dc24feH9cCpj",
            "https://detail.1688.com/offer/650660978552.html?spm=a2637j.22917583.home-list.d_650660978552.63dc24feH9cCpj",
            "https://detail.1688.com/offer/631449166045.html?spm=a2637j.22917583.home-list.d_631449166045.63dc24feH9cCpj",
            "https://detail.1688.com/offer/747728125951.html?spm=a2637j.22917583.home-list.d_747728125951.63dc24feH9cCpj",
            "https://detail.1688.com/offer/701440679743.html?spm=a2637j.22917583.home-list.d_701440679743.63dc24feH9cCpj",
            "https://detail.1688.com/offer/698942559456.html?spm=a2637j.22917583.home-list.d_698942559456.63dc24feyDGsDB",
            "https://detail.1688.com/offer/925586266727.html?offerId=925586266727&spm=a260k.home2025.recommendpart.9",
            "https://detail.1688.com/offer/851636385634.html?offerId=851636385634&spm=a260k.home2025.recommendpart.13"
        ]
        self.test_results = []
    
    def test_single_link(self, url, index):
        """测试单个链接"""
        print(f"\n{'='*70}")
        print(f"🔍 测试链接 {index}/{len(self.test_links)}")
        print(f"🔗 URL: {url}")
        print(f"{'='*70}")
        
        test_result = {
            'index': index,
            'url': url,
            'success': False,
            'error': None,
            'data': {},
            'start_time': datetime.now(),
            'duration': 0
        }
        
        try:
            start_time = time.time()
            
            # 调用抓取函数
            result = scrape_1688_product(url)
            
            end_time = time.time()
            test_result['duration'] = round(end_time - start_time, 2)
            
            # 检查抓取结果
            if 'error' in result:
                test_result['error'] = result['error']
                print(f"❌ 抓取失败: {result['error']}")
            else:
                test_result['success'] = True
                test_result['data'] = result
                
                # 打印抓取结果
                print(f"✅ 抓取成功！耗时: {test_result['duration']}秒")
                print(f"📝 标题: {result.get('title', 'N/A')}")
                print(f"💰 价格: {result.get('price', 'N/A')}")
                print(f"🖼️ 图片数量: {len(result.get('images', []))}")
                print(f"📊 规格参数: {len(result.get('specifications', {}))}")
                print(f"📄 描述长度: {len(result.get('description', ''))}")
                
                # 验证数据质量
                quality_score = self.evaluate_data_quality(result)
                test_result['quality_score'] = quality_score
                print(f"⭐ 数据质量评分: {quality_score}/10")
                
                # 显示部分规格参数
                specs = result.get('specifications', {})
                if specs:
                    print("📋 规格参数示例:")
                    for i, (key, value) in enumerate(list(specs.items())[:3]):
                        print(f"   • {key}: {value}")
                
                # 显示前3张图片URL
                images = result.get('images', [])
                if images:
                    print("🖼️ 图片示例:")
                    for i, img_url in enumerate(images[:3]):
                        print(f"   • 图片{i+1}: {img_url[:60]}{'...' if len(img_url) > 60 else ''}")
                
        except Exception as e:
            test_result['error'] = str(e)
            test_result['duration'] = round(time.time() - start_time, 2)
            print(f"💥 抓取异常: {str(e)}")
        
        return test_result
    
    def evaluate_data_quality(self, data):
        """评估抓取数据质量"""
        score = 0
        
        # 标题评分 (2分)
        title = data.get('title', '')
        if title and title != 'N/A' and len(title) > 5:
            score += 2
        elif title and len(title) > 0:
            score += 1
        
        # 价格评分 (2分)
        price = data.get('price', '')
        if price and price != 'N/A' and ('￥' in price or '¥' in price or any(c.isdigit() for c in price)):
            score += 2
        elif price and price != 'N/A':
            score += 1
        
        # 图片评分 (2分)
        images = data.get('images', [])
        if len(images) >= 3:
            score += 2
        elif len(images) > 0:
            score += 1
        
        # 描述评分 (2分)
        description = data.get('description', '')
        if len(description) > 100:
            score += 2
        elif len(description) > 0:
            score += 1
        
        # 规格参数评分 (2分)
        specifications = data.get('specifications', {})
        if len(specifications) >= 5:
            score += 2
        elif len(specifications) > 0:
            score += 1
        
        return score
    
    def run_test(self):
        """运行测试"""
        print("🧪 开始新1688商品链接抓取测试")
        print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 测试链接数量: {len(self.test_links)}")
        print("="*80)
        
        # 逐一测试每个链接
        for i, url in enumerate(self.test_links, 1):
            test_result = self.test_single_link(url, i)
            self.test_results.append(test_result)
            
            # 避免请求过快
            time.sleep(3)  # 稍微延长间隔时间
        
        # 生成测试报告
        self.generate_report()
        
        return True
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*80)
        print("📋 新1688商品链接抓取测试报告")
        print("="*80)
        
        # 统计信息
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {successful_tests}")
        print(f"   失败数: {failed_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        # 平均耗时
        if self.test_results:
            avg_duration = sum([r['duration'] for r in self.test_results]) / len(self.test_results)
            print(f"   平均耗时: {avg_duration:.2f}秒")
        
        # 数据质量统计
        quality_scores = [r.get('quality_score', 0) for r in self.test_results if r['success']]
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"   平均数据质量: {avg_quality:.1f}/10")
        
        # 详细结果
        print(f"\n📋 详细测试结果:")
        for result in self.test_results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            duration = f"{result['duration']}秒"
            quality = f"({result.get('quality_score', 0)}/10)" if result['success'] else ""
            
            print(f"   {result['index']:2d}. {status} {duration} {quality}")
            
            if result['success']:
                data = result['data']
                title = data.get('title', 'N/A')[:50] + ('...' if len(data.get('title', '')) > 50 else '')
                print(f"       标题: {title}")
                print(f"       数据: 图片{len(data.get('images', []))}张, 规格{len(data.get('specifications', {}))}个")
            else:
                error_short = result['error'][:60] + ('...' if len(result['error']) > 60 else '')
                print(f"       错误: {error_short}")
        
        # 成功案例详情
        if successful_tests > 0:
            print(f"\n🏆 成功案例详情:")
            successful_results = [r for r in self.test_results if r['success']]
            for result in successful_results:
                data = result['data']
                print(f"\n   📦 商品 {result['index']}:")
                print(f"      标题: {data.get('title', 'N/A')}")
                print(f"      价格: {data.get('price', 'N/A')}")
                print(f"      图片: {len(data.get('images', []))}张")
                print(f"      规格: {len(data.get('specifications', {}))}个参数")
                print(f"      质量: {result.get('quality_score', 0)}/10分")
        
        # 错误分析
        if failed_tests > 0:
            print(f"\n❌ 失败原因分析:")
            error_counts = {}
            for result in self.test_results:
                if not result['success']:
                    error = result['error'][:50]  # 截断长错误信息
                    error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   • {error}: {count}次")
        
        # 保存报告到文件
        self.save_report()
    
    def save_report(self):
        """保存测试报告到文件"""
        try:
            report_filename = f"new_1688_links_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(os.path.dirname(__file__), report_filename)
            
            report_data = {
                'test_time': datetime.now().isoformat(),
                'total_tests': len(self.test_results),
                'successful_tests': len([r for r in self.test_results if r['success']]),
                'failed_tests': len([r for r in self.test_results if not r['success']]),
                'success_rate': (len([r for r in self.test_results if r['success']]) / len(self.test_results) * 100) if self.test_results else 0,
                'test_links': self.test_links,
                'test_results': self.test_results
            }
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 测试报告已保存: {report_filename}")
            
        except Exception as e:
            print(f"\n⚠️ 保存报告失败: {e}")

def main():
    """主函数"""
    print("🧪 新1688商品链接抓取测试工具")
    print("="*50)
    
    # 创建测试器并运行
    tester = New1688LinkTester()
    success = tester.run_test()
    
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n⚠️ 测试过程中遇到问题")

if __name__ == "__main__":
    main()