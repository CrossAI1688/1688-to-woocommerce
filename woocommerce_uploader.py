import requests
from woocommerce import API
import json
import logging
from typing import Dict, List, Optional
import time
from urllib.parse import urlparse
import base64
from io import BytesIO
from PIL import Image

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WooCommerceUploader:
    """WooCommerce商品上传器"""
    
    def __init__(self, url: str, consumer_key: str, consumer_secret: str, use_external_images: bool = True):
        """
        初始化WooCommerce API连接
        
        Args:
            url: WooCommerce网站URL
            consumer_key: Consumer Key
            consumer_secret: Consumer Secret
            use_external_images: 是否直接使用外部图片链接（默认True，避免上传权限问题）
        """
        self.url = url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.use_external_images = use_external_images
        
        # 初始化WooCommerce API
        self.wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            wp_api=True,
            version="wc/v3",
            timeout=30
        )
    
    def test_connection(self) -> Dict:
        """测试WooCommerce API连接"""
        try:
            response = self.wcapi.get("products", params={"per_page": 1})
            if response.status_code == 200:
                return {"success": True, "message": "连接成功"}
            elif response.status_code == 401:
                return {"success": False, "message": "API密钥验证失败，请检查Consumer Key和Secret"}
            elif response.status_code == 403:
                return {"success": False, "message": "权限不足，请检查API密钥权限设置"}
            elif response.status_code == 404:
                return {"success": False, "message": "API端点不存在，请检查网站URL是否正确"}
            else:
                return {"success": False, "message": f"连接失败: HTTP {response.status_code}"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "无法连接到服务器，请检查网站URL是否正确"}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "连接超时，请检查网络或服务器状态"}
        except requests.exceptions.SSLError:
            return {"success": False, "message": "SSL证书验证失败，请检查网站HTTPS配置"}
        except Exception as e:
            return {"success": False, "message": f"连接错误: {str(e)}"}
    
    def detailed_test(self) -> Dict:
        """详细的API功能测试"""
        test_results = []
        
        try:
            # 1. 测试获取商品列表
            response = self.wcapi.get("products", params={"per_page": 1})
            if response.status_code == 200:
                test_results.append("✅ 商品列表获取: 成功")
            else:
                test_results.append(f"❌ 商品列表获取: 失败 (HTTP {response.status_code})")
            
            # 2. 测试获取商品分类
            response = self.wcapi.get("products/categories", params={"per_page": 1})
            if response.status_code == 200:
                test_results.append("✅ 商品分类获取: 成功")
            else:
                test_results.append(f"❌ 商品分类获取: 失败 (HTTP {response.status_code})")
            
            # 3. 测试媒体库权限（仅在不使用外部图片模式时）
            if not self.use_external_images:
                try:
                    import requests
                    headers = {
                        'Authorization': f'Basic {base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()}'
                    }
                    media_url = f"{self.url}/wp-json/wp/v2/media"
                    response = requests.get(media_url, headers=headers, params={"per_page": 1}, timeout=10)
                    if response.status_code == 200:
                        test_results.append("✅ 媒体库访问: 成功")
                    else:
                        test_results.append(f"⚠️ 媒体库访问: 权限不足 (HTTP {response.status_code})")
                except:
                    test_results.append("⚠️ 媒体库访问: 无法测试")
            else:
                test_results.append("ℹ️ 媒体库访问: 已启用外部图片模式，跳过测试")
            
            # 4. 获取店铺基本信息
            response = self.wcapi.get("system_status")
            if response.status_code == 200:
                system_info = response.json()
                wp_version = system_info.get('environment', {}).get('wp_version', 'Unknown')
                wc_version = system_info.get('environment', {}).get('wc_version', 'Unknown')
                test_results.append(f"✅ 系统信息: WordPress {wp_version}, WooCommerce {wc_version}")
            else:
                test_results.append("⚠️ 系统信息获取: 权限不足")
            
        except Exception as e:
            test_results.append(f"❌ 详细测试异常: {str(e)}")
        
        return {
            "success": True,
            "details": "\n".join(test_results)
        }
    
    def download_image(self, image_url: str) -> Optional[bytes]:
        """下载图片并返回字节数据"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.warning(f"URL不是图片类型: {image_url}")
                return None
            
            return response.content
        except Exception as e:
            logger.error(f"下载图片失败 {image_url}: {str(e)}")
            return None
    
    def upload_image_to_media(self, image_url: str, filename: str) -> Optional[int]:
        """上传图片到WordPress媒体库"""
        try:
            # 下载图片
            image_data = self.download_image(image_url)
            if not image_data:
                return None
            
            # 准备上传数据
            files = {
                'file': (filename, image_data)
            }
            
            # 上传到媒体库
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()}'
            }
            
            upload_url = f"{self.url}/wp-json/wp/v2/media"
            response = requests.post(upload_url, files=files, headers=headers, timeout=60)
            
            if response.status_code == 201:
                media_data = response.json()
                logger.info(f"图片上传成功: {filename}")
                return media_data['id']
            else:
                logger.error(f"图片上传失败: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"上传图片时发生错误: {str(e)}")
            return None
    
    def process_images(self, images: List[str]) -> List[Dict]:
        """处理图片列表，根据配置选择上传或直接使用外部链接"""
        processed_images = []
        
        if self.use_external_images:
            # 直接使用外部图片链接，避免上传权限问题
            logger.info("使用外部图片链接模式，跳过上传到媒体库")
            for i, image_url in enumerate(images[:10]):  # 最多处理10张图片
                try:
                    # 验证图片URL是否有效
                    if self.is_valid_external_image_url(image_url):
                        processed_images.append({
                            "src": image_url,
                            "name": f"商品图片_{i+1}",
                            "alt": f"商品图片 {i+1}"
                        })
                        logger.info(f"添加外部图片: {image_url}")
                    else:
                        logger.warning(f"跳过无效图片URL: {image_url}")
                except Exception as e:
                    logger.error(f"处理外部图片时发生错误: {str(e)}")
                    continue
        else:
            # 原有的上传到媒体库的方式
            logger.info("使用上传到媒体库模式")
            for i, image_url in enumerate(images[:10]):  # 最多处理10张图片
                try:
                    # 生成文件名
                    filename = f"product_image_{int(time.time())}_{i+1}.jpg"
                    
                    # 上传图片
                    media_id = self.upload_image_to_media(image_url, filename)
                    
                    if media_id:
                        processed_images.append({
                            "id": media_id,
                            "src": image_url,
                            "name": filename,
                            "alt": f"商品图片 {i+1}"
                        })
                    
                    # 添加延迟避免过于频繁的请求
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"处理图片时发生错误: {str(e)}")
                    continue
        
        return processed_images
    
    def is_valid_external_image_url(self, url: str) -> bool:
        """验证外部图片URL是否有效"""
        if not url or len(url) < 10:
            return False
        
        # 检查URL格式
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        
        # 检查文件扩展名
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        url_lower = url.lower()
        
        # 直接检查扩展名或包含图片格式参数
        for ext in valid_extensions:
            if ext in url_lower:
                return True
        
        # 如果没有明显的扩展名，但是是常见的图片服务域名
        image_domains = ['img.alicdn.com', 'cbu01.alicdn.com', 'sc04.alicdn.com']
        for domain in image_domains:
            if domain in url_lower:
                return True
        
        return False
    
    def create_product_data(self, product_info: Dict) -> Dict:
        """根据1688商品信息创建WooCommerce商品数据"""
        
        # 处理价格
        price_str = product_info.get('price', '0')
        price = self.extract_price_number(price_str)
        
        # 处理图片
        images_data = []
        if product_info.get('images'):
            images_data = self.process_images(product_info['images'])
        
        # 构建商品数据
        product_data = {
            "name": product_info.get('title', '商品标题'),
            "type": "simple",
            "regular_price": str(price),
            "sale_price": str(price * 0.9),  # 设置为原价的90%作为促销价
            "description": self.format_description(product_info),
            "short_description": product_info.get('description', '')[:160],  # 短描述限制160字符
            "categories": [
                {"id": 1}  # 默认分类，需要根据实际情况调整
            ],
            "images": images_data,
            "status": "draft",  # 默认为草稿状态
            "featured": False,
            "catalog_visibility": "visible",
            "meta_data": [
                {
                    "key": "_1688_source_url",
                    "value": product_info.get('url', '')
                },
                {
                    "key": "_1688_product_id",
                    "value": product_info.get('product_id', '')
                },
                {
                    "key": "_scraped_at",
                    "value": product_info.get('scraped_at', '')
                }
            ]
        }
        
        # 注意：根据用户要求，不再将规格参数作为WooCommerce产品属性上传
        # 规格参数只保留在产品描述中，通过format_description方法处理
        
        return product_data
    
    def extract_price_number(self, price_str: str) -> float:
        """从价格字符串中提取数字"""
        import re
        
        # 移除货币符号和空格
        price_clean = re.sub(r'[¥$￥\s]', '', str(price_str))
        
        # 提取数字
        numbers = re.findall(r'[\d,]+\.?\d*', price_clean)
        if numbers:
            # 移除逗号并转换为浮点数
            try:
                return float(numbers[0].replace(',', ''))
            except ValueError:
                pass
        
        return 0.0
    
    def format_description(self, product_info: Dict) -> str:
        """格式化商品描述"""
        description_parts = []
        
        # 基本描述
        if product_info.get('description'):
            description_parts.append(f"<p>{product_info['description']}</p>")
        
        # 添加规格参数
        if product_info.get('specifications'):
            description_parts.append("<h3>产品规格</h3>")
            description_parts.append("<ul>")
            for key, value in product_info['specifications'].items():
                description_parts.append(f"<li><strong>{key}:</strong> {value}</li>")
            description_parts.append("</ul>")
        
        # 添加来源信息
        description_parts.append("<hr>")
        description_parts.append("<p><small>商品信息来源：1688平台</small></p>")
        if product_info.get('url'):
            description_parts.append(f"<p><small>原链接：<a href='{product_info['url']}' target='_blank'>查看原商品</a></small></p>")
        
        return "".join(description_parts)
    
    def upload_product(self, product_info: Dict) -> Dict:
        """上传商品到WooCommerce"""
        try:
            logger.info(f"开始上传商品: {product_info.get('title', 'N/A')}")
            
            # 测试连接
            connection_test = self.test_connection()
            if not connection_test['success']:
                return {"success": False, "message": f"连接失败: {connection_test['message']}"}
            
            # 创建商品数据
            product_data = self.create_product_data(product_info)
            
            # 上传商品
            response = self.wcapi.post("products", product_data)
            
            if response.status_code == 201:
                product_result = response.json()
                logger.info(f"商品上传成功: ID {product_result['id']}")
                
                return {
                    "success": True,
                    "message": "商品上传成功",
                    "product_id": product_result['id'],
                    "product_url": product_result.get('permalink', ''),
                    "data": product_result
                }
            else:
                error_message = "上传失败"
                if response.text:
                    try:
                        error_data = response.json()
                        error_message = error_data.get('message', error_message)
                    except:
                        error_message = response.text[:200]
                
                logger.error(f"商品上传失败: HTTP {response.status_code}, {error_message}")
                return {
                    "success": False,
                    "message": f"上传失败: {error_message}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"上传商品时发生错误: {str(e)}")
            return {"success": False, "message": f"上传过程中发生错误: {str(e)}"}
    
    def get_categories(self) -> List[Dict]:
        """获取商品分类列表"""
        try:
            response = self.wcapi.get("products/categories", params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except Exception as e:
            logger.error(f"获取分类失败: {str(e)}")
            return []
    
    def create_category(self, name: str, parent_id: int = 0) -> Optional[int]:
        """创建商品分类"""
        try:
            category_data = {
                "name": name,
                "parent": parent_id
            }
            
            response = self.wcapi.post("products/categories", category_data)
            if response.status_code == 201:
                category_result = response.json()
                return category_result['id']
            else:
                return None
        except Exception as e:
            logger.error(f"创建分类失败: {str(e)}")
            return None

def create_woocommerce_uploader(config: Dict, use_external_images: bool = True) -> Optional[WooCommerceUploader]:
    """创建WooCommerce上传器实例"""
    try:
        if not all([config.get('url'), config.get('consumer_key'), config.get('consumer_secret')]):
            return None
        
        uploader = WooCommerceUploader(
            url=config['url'],
            consumer_key=config['consumer_key'],
            consumer_secret=config['consumer_secret'],
            use_external_images=use_external_images
        )
        
        return uploader
    except Exception as e:
        logger.error(f"创建WooCommerce上传器失败: {str(e)}")
        return None