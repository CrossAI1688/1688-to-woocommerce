import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
import time
import random
from typing import Dict, List, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Product1688Scraper:
    """1688商品信息抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def validate_url(self, url: str) -> bool:
        """验证1688商品链接格式"""
        patterns = [
            r'https?://detail\.1688\.com/offer/\d+\.html',
            r'https?://m\.1688\.com/offer/\d+\.html',
            r'https?://.*\.1688\.com/.*offer.*'
        ]
        
        for pattern in patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def extract_product_id(self, url: str) -> Optional[str]:
        """从URL中提取商品ID"""
        match = re.search(r'offer/(\d+)', url)
        if match:
            return match.group(1)
        return None
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        try:
            # 添加随机延迟
            time.sleep(random.uniform(1, 3))
            
            logger.info(f"开始请求页面: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"请求成功，状态码: {response.status_code}，内容长度: {len(response.content)}")
            
            # 检查是否被重定向到登录页面
            if 'login' in response.url or 'passport' in response.url:
                logger.warning("可能需要登录才能访问该页面")
                return None
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '')
            logger.info(f"内容类型: {content_type}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 检查页面是否正常加载
            if soup.find('title'):
                logger.info(f"页面标题: {soup.find('title').get_text()[:100]}")
            
            # 检查是否有错误页面
            error_indicators = [
                '页面不存在',
                '404',
                '网页错误',
                'page not found',
                '服务器错误'
            ]
            
            page_text = soup.get_text().lower()
            for indicator in error_indicators:
                if indicator in page_text:
                    logger.warning(f"检测到错误页面指示器: {indicator}")
                    return None
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"请求页面失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"解析页面失败: {str(e)}")
            return None
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """提取商品标题"""
        # 更全面的标题选择器，包括新版陶1688页面
        selectors = [
            # 新版陶1688页面选择器
            '[data-testid="product-title"]',
            '.offer-title',
            '.product-title',
            '.product-name',
            '.detail-title',
            '.offer-detail-title',
            '.fd-clr-title',
            '[class*="title"] h1',
            '[class*="Title"] h1',
            
            # 传统选择器
            'h1[data-spm-anchor-id]',
            '.product-title h1',
            '.offer-title h1',
            'h1.product-name',
            '.mod-detail-title h1',
            '.mod-detail-title',
            
            # 通用选择器
            'h1',
            '[class*="product"][class*="title"]',
            '[class*="offer"][class*="title"]'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    if elem:
                        title_text = elem.get_text(strip=True)
                        # 过滤太短或无意义的标题
                        if title_text and len(title_text) > 5 and len(title_text) < 200:
                            # 过滤一些无意义的内容
                            if not any(word in title_text.lower() for word in ['javascript', 'function', 'error', 'undefined']):
                                logger.info(f"使用选择器 {selector} 找到标题: {title_text[:50]}...")
                                return title_text
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {str(e)}")
                continue
        
        # 从页面标题中提取
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            logger.info(f"页面title标签内容: {title}")
            
            # 移除常见的后缀
            title = re.sub(r'[-–—].*?(阿里巴巴|1688|中国制造网|批发网).*?$', '', title).strip()
            title = re.sub(r'_.*?(阿里巴巴|1688).*?$', '', title).strip()
            
            if title and len(title) > 5:
                logger.info(f"从页面标题提取到: {title}")
                return title
        
        # 从 JSON-LD 结构化数据中提取
        try:
            json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and 'name' in data:
                            return data['name']
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and 'name' in item:
                                    return item['name']
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.debug(f"JSON-LD提取失败: {str(e)}")
        
        # 从 JavaScript变量中提取
        try:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_text = script.string
                    
                    # 查找常见的标题字段
                    title_patterns = [
                        r'"title"\s*:\s*"([^"]{10,100})"',
                        r'"productName"\s*:\s*"([^"]{10,100})"',
                        r'"name"\s*:\s*"([^"]{10,100})"',
                        r"'title'\s*:\s*'([^']{10,100})'",
                        r"'productName'\s*:\s*'([^']{10,100})'",
                        r"'name'\s*:\s*'([^']{10,100})'"
                    ]
                    
                    for pattern in title_patterns:
                        matches = re.findall(pattern, script_text, re.IGNORECASE)
                        for match in matches:
                            if match and len(match.strip()) > 5:
                                # 过滤无意义的内容
                                if not any(word in match.lower() for word in ['function', 'undefined', 'null', 'error']):
                                    logger.info(f"从JavaScript中提取到标题: {match.strip()}")
                                    return match.strip()
        except Exception as e:
            logger.debug(f"JavaScript提取失败: {str(e)}")
        
        logger.warning("未能找到商品标题")
        return "未找到商品标题"
    
    def extract_price(self, soup: BeautifulSoup) -> str:
        """提取商品价格"""
        # 多种价格选择器
        price_selectors = [
            '.price-range .price-value',
            '.price .price-value',
            '.mod-price .price-value',
            '.offer-price .price-original',
            '.price-original',
            '.price-now',
            '[data-role="price"]',
            '.price-text'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # 提取数字和货币符号
                price_match = re.search(r'[¥$￥]?\s*[\d,]+\.?\d*', price_text)
                if price_match:
                    return price_match.group(0)
        
        # 从脚本中提取价格信息
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'price' in script.string.lower():
                # 寻找价格相关的JSON数据
                price_matches = re.findall(r'"price[^"]*":\s*"?([¥$￥]?\s*[\d,]+\.?\d*)"?', script.string)
                if price_matches:
                    return price_matches[0]
        
        return "价格面议"
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取商品图片"""
        images = []
        
        # 多种图片选择器
        img_selectors = [
            '.mod-detail-gallery img',
            '.detail-gallery img',
            '.product-images img',
            '.offer-image img',
            '.main-image img',
            '.preview-image img'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                img_url = img.get('src') or img.get('data-src') or img.get('data-original')
                if img_url:
                    # 处理相对链接
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif img_url.startswith('/'):
                        img_url = urljoin(base_url, img_url)
                    
                    # 过滤无效图片
                    if self.is_valid_image_url(img_url):
                        images.append(img_url)
        
        # 从脚本中提取图片
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 寻找图片URL模式
                img_matches = re.findall(r'https?://[^"\s]+\.(?:jpg|jpeg|png|gif|webp)', script.string, re.IGNORECASE)
                for img_url in img_matches:
                    if self.is_valid_image_url(img_url):
                        images.append(img_url)
        
        # 去重并限制数量
        images = list(dict.fromkeys(images))  # 去重保持顺序
        return images[:10]  # 最多返回10张图片
    
    def is_valid_image_url(self, url: str) -> bool:
        """验证图片URL是否有效"""
        if not url or len(url) < 10:
            return False
        
        # 排除无效的图片
        invalid_patterns = [
            r'1x1\.gif',
            r'placeholder',
            r'loading',
            r'icon',
            r'logo',
            r'btn',
            r'bg\.',
            r'\.svg$'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """提取商品描述"""
        logger.info("开始提取商品描述")
        
        # 更全面的描述选择器，包括新版陶1688页面
        desc_selectors = [
            # 新版陶1688页面选择器
            '[data-testid="product-description"]',
            '.product-detail-description',
            '.offer-detail-description', 
            '.detail-desc',
            '.product-desc',
            '.offer-desc',
            '.description-content',
            '.product-introduction',
            
            # 传统选择器
            '.mod-detail-description',
            '.product-description',
            '.offer-description',
            '.detail-description',
            '.mod-detail-info .text',
            '.product-info .desc',
            
            # 移动版选择器
            '.mobile-desc',
            '.m-desc',
            '.desc-wrap',
            '.detail-wrap .desc',
            
            # 通用选择器
            '[class*="desc"]',
            '[class*="description"]',
            '.content-wrap .content'
        ]
        
        # 尝试使用各种选择器提取描述
        for selector in desc_selectors:
            try:
                desc_elements = soup.select(selector)
                for desc_elem in desc_elements:
                    if desc_elem:
                        desc_text = desc_elem.get_text(strip=True)
                        # 过滤太短或无意义的描述
                        if len(desc_text) > 10 and len(desc_text) < 2000:
                            # 过滤一些无意义的内容
                            if not any(word in desc_text.lower() for word in ['javascript', 'function', 'error', 'undefined', 'script']):
                                logger.info(f"使用选择器 {selector} 找到描述: {desc_text[:50]}...")
                                return self.clean_description(desc_text)
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {str(e)}")
                continue
        
        # 从元数据中提取描述
        try:
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_content = meta_desc.get('content').strip()
                if len(desc_content) > 10:
                    logger.info(f"从元数据提取到描述: {desc_content[:50]}...")
                    return self.clean_description(desc_content)
        except Exception as e:
            logger.debug(f"元数据提取失败: {str(e)}")
        
        # 从 JSON-LD 结构化数据中提取
        try:
            json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
            for script in json_scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        desc = self.extract_description_from_json(data)
                        if desc:
                            logger.info(f"从JSON-LD提取到描述: {desc[:50]}...")
                            return self.clean_description(desc)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.debug(f"JSON-LD描述提取失败: {str(e)}")
        
        # 从 JavaScript变量中提取
        try:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_text = script.string
                    
                    # 查找常见的描述字段
                    desc_patterns = [
                        r'"description"\s*:\s*"([^"]{20,500})"',
                        r'"productDescription"\s*:\s*"([^"]{20,500})"',
                        r'"desc"\s*:\s*"([^"]{20,500})"',
                        r"'description'\s*:\s*'([^']{20,500})'" ,
                        r"'productDescription'\s*:\s*'([^']{20,500})'" ,
                        r"'desc'\s*:\s*'([^']{20,500})'"
                    ]
                    
                    for pattern in desc_patterns:
                        matches = re.findall(pattern, script_text, re.IGNORECASE)
                        for match in matches:
                            if match and len(match.strip()) > 10:
                                # 过滤无意义的内容
                                if not any(word in match.lower() for word in ['function', 'undefined', 'null', 'error', 'script']):
                                    logger.info(f"从JavaScript中提取到描述: {match[:50]}...")
                                    return self.clean_description(match)
        except Exception as e:
            logger.debug(f"JavaScript描述提取失败: {str(e)}")
        
        # 提取商品特征/卖点作为描述
        features = self.extract_product_features(soup)
        if features:
            feature_desc = "产品特点：" + "；".join(features[:5])
            logger.info(f"使用产品特点作为描述: {feature_desc[:50]}...")
            return feature_desc
        
        # 从商品标题生成简单描述
        title = self.extract_title(soup)
        if title and title != "未找到商品标题":
            simple_desc = f"这是一款{title}。商品来自1688平台，详细信息请查看原链接。"
            logger.info("使用标题生成简单描述")
            return simple_desc
        
        logger.warning("未能找到商品描述")
        return "暂无详细描述"
    
    def clean_description(self, desc_text: str) -> str:
        """清理描述文本"""
        if not desc_text:
            return ""
        
        # 移除HTML标签
        import re
        desc_text = re.sub(r'<[^>]+>', '', desc_text)
        
        # 移除多余的空白字符
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
        
        # 移除特殊字符
        desc_text = desc_text.replace('\xa0', ' ').replace('\u200b', '')
        
        # 限制长度
        if len(desc_text) > 800:
            desc_text = desc_text[:800] + "..."
        
        return desc_text
    
    def extract_description_from_json(self, data) -> str:
        """从 JSON 数据中提取描述"""
        if isinstance(data, dict):
            # 查找常见的描述字段
            desc_fields = ['description', 'productDescription', 'desc', 'content', 'summary']
            for field in desc_fields:
                if field in data and isinstance(data[field], str) and len(data[field]) > 10:
                    return data[field]
            
            # 递归搜索子对象
            for value in data.values():
                if isinstance(value, (dict, list)):
                    result = self.extract_description_from_json(value)
                    if result:
                        return result
        
        elif isinstance(data, list):
            for item in data:
                result = self.extract_description_from_json(item)
                if result:
                    return result
        
        return None
    
    def extract_product_features(self, soup: BeautifulSoup) -> List[str]:
        """提取产品特征/卖点"""
        features = []
        
        # 更全面的特征选择器
        feature_selectors = [
            # 新版陶1688页面
            '.product-features li',
            '.selling-points li', 
            '.product-highlights li',
            '.feature-list li',
            '.advantages li',
            '.key-features li',
            
            # 移动版选择器
            '.m-features li',
            '.mobile-features li',
            
            # 通用选择器
            '[class*="feature"] li',
            '[class*="highlight"] li',
            '[class*="advantage"] li',
            '.desc-list li',
            '.point-list li'
        ]
        
        for selector in feature_selectors:
            try:
                feature_elements = soup.select(selector)
                for elem in feature_elements:
                    if elem:
                        feature_text = elem.get_text(strip=True)
                        # 过滤有效的特征文本
                        if feature_text and 5 < len(feature_text) < 200:
                            # 过滤无意义的内容
                            if not any(word in feature_text.lower() for word in ['function', 'undefined', 'null', 'error', 'script', 'click']):
                                if feature_text not in features:
                                    features.append(feature_text)
                                    logger.debug(f"找到产品特征: {feature_text}")
                
                # 如果已经找到足够的特征，停止搜索
                if len(features) >= 8:
                    break
            except Exception as e:
                logger.debug(f"特征选择器 {selector} 失败: {str(e)}")
                continue
        
        return features[:8]  # 最多返8个特征
    
    def extract_specifications(self, soup: BeautifulSoup) -> Dict:
        """提取商品规格参数"""
        specs = {}
        logger.info("开始提取商品规格参数")
        
        # 桌面版规格表格选择器
        desktop_selectors = [
            '.mod-detail-attributes table',
            '.product-params table', 
            '.spec-table',
            '.product-attributes table',
            '.offer-attributes table',
            '.detail-attributes table'
        ]
        
        # 移动版规格选择器
        mobile_selectors = [
            '.m-params table',
            '.mobile-params table',
            '.m-spec-table',
            '.spec-list',
            '.param-list',
            '.m-attributes',
            '.mobile-attributes'
        ]
        
        # 通用规格选择器
        general_selectors = [
            '[class*="param"] table',
            '[class*="spec"] table',
            '[class*="attribute"] table',
            '.props-list',
            '.property-list'
        ]
        
        all_selectors = desktop_selectors + mobile_selectors + general_selectors
        
        # 尝试从表格中提取规格
        for selector in all_selectors:
            try:
                spec_tables = soup.select(selector)
                for table in spec_tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            if key and value and len(key) < 50 and len(value) < 200:
                                # 过滤无意义的键值对
                                if not any(word in key.lower() for word in ['序号', 'number', 'index', '操作']):
                                    specs[key] = value
                                    logger.debug(f"从表格提取规格: {key}: {value}")
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {str(e)}")
                continue
        
        # 寻找dl/dt/dd结构的规格列表
        dl_selectors = [
            '.product-attributes dl',
            '.spec-list dl', 
            '.params-list dl',
            '.m-params dl',
            '.mobile-params dl'
        ]
        
        for selector in dl_selectors:
            try:
                spec_lists = soup.select(selector)
                for dl in spec_lists:
                    dt = dl.find('dt')
                    dd = dl.find('dd')
                    if dt and dd:
                        key = dt.get_text(strip=True)
                        value = dd.get_text(strip=True)
                        if key and value and len(key) < 50 and len(value) < 200:
                            specs[key] = value
                            logger.debug(f"从列表提取规格: {key}: {value}")
            except Exception as e:
                logger.debug(f"DL选择器 {selector} 失败: {str(e)}")
                continue
        
        # 从JavaScript数据中提取规格参数
        try:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    script_text = script.string
                    
                    # 查找包含规格参数的数据结构
                    # 特别针对1688页面中的props、attributes等字段
                    spec_patterns = [
                        r'"props"\s*:\s*\[([^\]]+)\]',
                        r'"attributes"\s*:\s*\[([^\]]+)\]',
                        r'"params"\s*:\s*\[([^\]]+)\]',
                        r'"specifications"\s*:\s*\[([^\]]+)\]'
                    ]
                    
                    for pattern in spec_patterns:
                        matches = re.findall(pattern, script_text, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            try:
                                # 尝试解析JSON数组
                                array_text = '[' + match + ']'
                                spec_array = json.loads(array_text)
                                
                                if isinstance(spec_array, list):
                                    for item in spec_array:
                                        if isinstance(item, dict):
                                            # 提取name和value字段
                                            name = item.get('name', '').strip()
                                            value = item.get('value', '').strip()
                                            
                                            if name and value and len(name) < 50 and len(value) < 200:
                                                # 清理特殊字符和JSON残留
                                                name = re.sub(r'["\\]', '', name)
                                                value = re.sub(r'["\\]', '', value)
                                                
                                                # 移除JSON格式残留
                                                if '"},{\'name' in value or '},{"name' in value:
                                                    value = re.split(r'\}\s*,\s*\{', value)[0]
                                                
                                                # 进一步清理
                                                value = re.sub(r'\}\s*$', '', value)
                                                value = re.sub(r'^[^a-zA-Z0-9\u4e00-\u9fff]*', '', value)
                                                
                                                if name and value and len(value) > 0:
                                                    specs[name] = value
                                                    logger.debug(f"从JS数组提取规格: {name}: {value}")
                                            
                                            # 也尝试其他可能的字段名组合
                                            for key_field in ['key', 'label', 'title']:
                                                for value_field in ['value', 'val', 'content']:
                                                    if key_field in item and value_field in item:
                                                        k = str(item[key_field]).strip()
                                                        v = str(item[value_field]).strip()
                                                        if k and v and len(k) < 50 and len(v) < 200:
                                                            specs[k] = v
                                                            logger.debug(f"从JS提取规格: {k}: {v}")
                                            
                            except (json.JSONDecodeError, ValueError) as e:
                                logger.debug(f"JSON解析失败: {str(e)}")
                                continue
                    
                    # 查找简单的键值对格式
                    simple_patterns = [
                        r'"name"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*"([^"]+)"',
                        r'"key"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*"([^"]+)"'
                    ]
                    
                    for pattern in simple_patterns:
                        matches = re.findall(pattern, script_text, re.IGNORECASE)
                        for name, value in matches:
                            name = name.strip()
                            value = value.strip()
                            if name and value and len(name) < 50 and len(value) < 200:
                                specs[name] = value
                                logger.debug(f"从简单模式提取规格: {name}: {value}")
                    
        except Exception as e:
            logger.debug(f"JavaScript规格提取失败: {str(e)}")
        
        # 从页面中寻找键值对格式的信息
        try:
            # 寻找类似 "材质：树脂" 格式的文本
            page_text = soup.get_text()
            kv_patterns = [
                r'([^\n\r，。；！？]{2,15})[:：]\s*([^\n\r，。；！？]{1,50})',
                r'([^\n\r，。；！？]{2,15})\s*[=＝]\s*([^\n\r，。；！？]{1,50})'
            ]
            
            for pattern in kv_patterns:
                matches = re.findall(pattern, page_text)
                for key, value in matches:
                    key = key.strip()
                    value = value.strip()
                    
                    # 过滤常见的规格参数关键词
                    if any(keyword in key for keyword in ['材质', '颜色', '尺寸', '重量', '规格', '型号', '品牌', '产地', '工艺']):
                        if len(key) < 20 and len(value) < 100 and value not in ['', '详见描述', '请咨询客服']:
                            specs[key] = value
                            logger.debug(f"从文本提取规格: {key}: {value}")
                            
        except Exception as e:
            logger.debug(f"文本规格提取失败: {str(e)}")
        
        if specs:
            logger.info(f"成功提取到 {len(specs)} 个规格参数")
        else:
            logger.warning("未找到商品规格参数")
        
        return specs
    
    def scrape_product(self, url: str) -> Dict:
        """抓取商品信息"""
        logger.info(f"开始抓取商品信息: {url}")
        
        # 验证URL
        if not self.validate_url(url):
            return {"error": "无效的1688商品链接格式"}
        
        # 尝试抓取原始URL
        soup = self.get_page_content(url)
        original_url = url
        
        # 如果原始URL失败，或者是桌面版但无法提取到有效信息，尝试移动版
        should_try_mobile = False
        
        if not soup and 'detail.1688.com' in url:
            # 页面加载失败，尝试移动版
            should_try_mobile = True
            logger.info("桌面版页面加载失败，尝试移动版")
        elif soup and 'detail.1688.com' in url:
            # 页面加载成功，但检查是否能提取到有效信息
            test_title = self.extract_title(soup)
            if test_title == "未找到商品标题":
                # 无法提取到有效标题，尝试移动版
                should_try_mobile = True
                logger.info("桌面版无法提取有效商品信息，尝试移动版")
        
        if should_try_mobile:
            mobile_url = original_url.replace('detail.1688.com', 'm.1688.com')
            logger.info(f"尝试移动版: {mobile_url}")
            mobile_soup = self.get_page_content(mobile_url)
            if mobile_soup:
                # 检查移动版是否能提取到更好的信息
                mobile_title = self.extract_title(mobile_soup)
                if mobile_title != "未找到商品标题":
                    soup = mobile_soup
                    url = mobile_url  # 更新URL为移动版
                    logger.info("移动版抓取成功，使用移动版数据")
                else:
                    logger.warning("移动版也无法提取到有效信息，使用原始版本")
        
        if not soup:
            return {"error": "无法获取页面内容，可能需要登录或页面不存在"}
        
        try:
            # 提取商品信息
            product_info = {
                "url": url,
                "product_id": self.extract_product_id(url),
                "title": self.extract_title(soup),
                "price": self.extract_price(soup),
                "images": self.extract_images(soup, url),
                "description": self.extract_description(soup),
                "specifications": self.extract_specifications(soup),
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"成功抓取商品信息: {product_info['title']}")
            return product_info
            
        except Exception as e:
            logger.error(f"抓取商品信息时发生错误: {str(e)}")
            return {"error": f"抓取过程中发生错误: {str(e)}"}

# 创建全局抓取器实例
scraper = Product1688Scraper()

def scrape_1688_product(url: str) -> Dict:
    """抓取1688商品信息的主要函数"""
    return scraper.scrape_product(url)