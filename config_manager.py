import json
import os
from typing import Dict, Optional, List
import logging
from cryptography.fernet import Fernet
import base64

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器，用于安全存储和加载WooCommerce配置"""
    
    def __init__(self, config_file: str = "wc_config.json", encrypted: bool = False):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
            encrypted: 是否启用加密存储
        """
        self.config_file = config_file
        self.encrypted = encrypted
        self.key_file = "config.key"
        
        if self.encrypted:
            self._init_encryption()
    
    def _init_encryption(self):
        """初始化加密功能"""
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    self.key = f.read()
            else:
                self.key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(self.key)
            
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"初始化加密功能失败: {str(e)}")
            self.encrypted = False
    
    def save_config(self, config: Dict) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证配置
            if not self._validate_config(config):
                logger.error("配置验证失败")
                return False
            
            # 准备保存的数据
            config_data = {
                "url": config.get("url", "").strip(),
                "consumer_key": config.get("consumer_key", "").strip(),
                "consumer_secret": config.get("consumer_secret", "").strip(),
                "version": "1.0",
                "created_at": self._get_timestamp()
            }
            
            if self.encrypted:
                # 加密保存
                json_str = json.dumps(config_data, ensure_ascii=False, indent=2)
                encrypted_data = self.cipher.encrypt(json_str.encode('utf-8'))
                
                with open(self.config_file, 'wb') as f:
                    f.write(encrypted_data)
            else:
                # 普通保存
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("配置保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def load_config(self) -> Optional[Dict]:
        """
        从文件加载配置
        
        Returns:
            Dict: 配置字典，如果失败返回None
        """
        try:
            if not os.path.exists(self.config_file):
                logger.info("配置文件不存在")
                return None
            
            if self.encrypted:
                # 解密加载
                with open(self.config_file, 'rb') as f:
                    encrypted_data = f.read()
                
                decrypted_data = self.cipher.decrypt(encrypted_data)
                config_data = json.loads(decrypted_data.decode('utf-8'))
            else:
                # 普通加载
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            
            # 验证加载的配置
            if self._validate_config(config_data):
                logger.info("配置加载成功")
                return config_data
            else:
                logger.error("加载的配置验证失败")
                return None
                
        except Exception as e:
            logger.error(f"加载配置失败: {str(e)}")
            return None
    
    def _validate_config(self, config: Dict) -> bool:
        """
        验证配置有效性
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 配置是否有效
        """
        required_fields = ["url", "consumer_key", "consumer_secret"]
        
        for field in required_fields:
            if not config.get(field) or not isinstance(config[field], str) or not config[field].strip():
                logger.error(f"配置字段 {field} 无效")
                return False
        
        # 验证URL格式
        url = config["url"].strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            logger.error("URL格式无效，必须以http://或https://开头")
            return False
        
        # 验证Consumer Key和Secret长度
        if len(config["consumer_key"].strip()) < 10:
            logger.error("Consumer Key长度不足")
            return False
        
        if len(config["consumer_secret"].strip()) < 10:
            logger.error("Consumer Secret长度不足")
            return False
        
        return True
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def delete_config(self) -> bool:
        """
        删除配置文件
        
        Returns:
            bool: 删除是否成功
        """
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
                logger.info("配置文件已删除")
            
            if self.encrypted and os.path.exists(self.key_file):
                os.remove(self.key_file)
                logger.info("加密密钥文件已删除")
            
            return True
        except Exception as e:
            logger.error(f"删除配置文件失败: {str(e)}")
            return False
    
    def save_browser_config(self, config: Dict) -> bool:
        """
        保存浏览器配置到专用文件
        
        Args:
            config: 配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 验证配置
            if not self._validate_config(config):
                logger.error("配置验证失败")
                return False
            
            # 准备保存的数据
            config_data = {
                "url": config.get("url", "").strip(),
                "consumer_key": config.get("consumer_key", "").strip(),
                "consumer_secret": config.get("consumer_secret", "").strip(),
                "version": "2.0",
                "storage_type": "browser_local",
                "created_at": self._get_timestamp(),
                "updated_at": self._get_timestamp()
            }
            
            # 保存到浏览器专用配置文件
            browser_config_file = "browser_config.json"
            with open(browser_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            logger.info("浏览器配置保存成功")
            return True
            
        except Exception as e:
            logger.error(f"保存浏览器配置失败: {str(e)}")
            return False
    
    def load_browser_config(self) -> Optional[Dict]:
        """
        从浏览器专用文件加载配置
        
        Returns:
            Dict: 配置字典，如果失败返回None
        """
        try:
            browser_config_file = "browser_config.json"
            if not os.path.exists(browser_config_file):
                logger.info("浏览器配置文件不存在")
                return None
            
            with open(browser_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证加载的配置
            if self._validate_config(config_data):
                logger.info("浏览器配置加载成功")
                return config_data
            else:
                logger.error("加载的浏览器配置验证失败")
                return None
                
        except Exception as e:
            logger.error(f"加载浏览器配置失败: {str(e)}")
            return None
    
    def delete_browser_config(self) -> bool:
        """
        删除浏览器配置文件
        
        Returns:
            bool: 删除是否成功
        """
        try:
            browser_config_file = "browser_config.json"
            if os.path.exists(browser_config_file):
                os.remove(browser_config_file)
                logger.info("浏览器配置文件已删除")
            return True
        except Exception as e:
            logger.error(f"删除浏览器配置文件失败: {str(e)}")
            return False
    
    def test_config(self, config: Dict) -> Dict:
        """
        测试配置连接
        
        Args:
            config: 配置字典
            
        Returns:
            Dict: 测试结果
        """
        try:
            # 首先验证配置格式
            if not self._validate_config(config):
                return {
                    "success": False, 
                    "message": "配置格式验证失败",
                    "details": "请检查URL格式和API密钥长度"
                }
            
            from woocommerce_uploader import create_woocommerce_uploader
            
            # 创建上传器
            uploader = create_woocommerce_uploader(config)
            if not uploader:
                return {
                    "success": False, 
                    "message": "无法创建WooCommerce连接",
                    "details": "请检查API密钥是否正确"
                }
            
            # 执行连接测试
            result = uploader.test_connection()
            
            # 如果基本连接成功，进行详细测试
            if result.get("success"):
                # 测试更多API端点以确保权限正确
                detailed_result = uploader.detailed_test()
                return {
                    "success": True,
                    "message": "连接测试成功",
                    "details": detailed_result.get("details", "API连接正常，权限验证通过")
                }
            else:
                return {
                    "success": False,
                    "message": "连接测试失败",
                    "details": result.get("message", "未知错误")
                }
            
        except Exception as e:
            logger.error(f"测试配置连接失败: {str(e)}")
            return {
                "success": False, 
                "message": "连接测试异常",
                "details": f"错误详情: {str(e)}"
            }
        """
        测试配置连接
        
        Args:
            config: 配置字典
            
        Returns:
            Dict: 测试结果
        """
        try:
            # 首先验证配置格式
            if not self._validate_config(config):
                return {
                    "success": False, 
                    "message": "配置格式验证失败",
                    "details": "请检查URL格式和API密钥长度"
                }
            
            from woocommerce_uploader import create_woocommerce_uploader
            
            # 创建上传器
            uploader = create_woocommerce_uploader(config)
            if not uploader:
                return {
                    "success": False, 
                    "message": "无法创建WooCommerce连接",
                    "details": "请检查API密钥是否正确"
                }
            
            # 执行连接测试
            result = uploader.test_connection()
            
            # 如果基本连接成功，进行详细测试
            if result.get("success"):
                # 测试更多API端点以确保权限正确
                detailed_result = uploader.detailed_test()
                return {
                    "success": True,
                    "message": "连接测试成功",
                    "details": detailed_result.get("details", "API连接正常，权限验证通过")
                }
            else:
                return {
                    "success": False,
                    "message": "连接测试失败",
                    "details": result.get("message", "未知错误")
                }
            
        except Exception as e:
            logger.error(f"测试配置连接失败: {str(e)}")
            return {
                "success": False, 
                "message": "连接测试异常",
                "details": f"错误详情: {str(e)}"
            }

class HistoryManager:
    """操作历史管理器"""
    
    def __init__(self, history_file: str = "upload_history.json"):
        """
        初始化历史管理器
        
        Args:
            history_file: 历史文件路径
        """
        self.history_file = history_file
    
    def add_record(self, record: Dict) -> bool:
        """
        添加操作记录
        
        Args:
            record: 操作记录字典
            
        Returns:
            bool: 添加是否成功
        """
        try:
            # 加载现有历史
            history = self.load_history()
            
            # 添加时间戳
            record["timestamp"] = self._get_timestamp()
            record["id"] = len(history) + 1
            
            # 添加到历史
            history.append(record)
            
            # 保持最多100条记录
            if len(history) > 100:
                history = history[-100:]
            
            # 保存历史
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"添加历史记录失败: {str(e)}")
            return False
    
    def load_history(self) -> List[Dict]:
        """
        加载操作历史
        
        Returns:
            List[Dict]: 历史记录列表
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            logger.error(f"加载历史记录失败: {str(e)}")
            return []
    
    def clear_history(self) -> bool:
        """
        清空历史记录
        
        Returns:
            bool: 清空是否成功
        """
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            return True
        except Exception as e:
            logger.error(f"清空历史记录失败: {str(e)}")
            return False
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 创建全局实例
config_manager = ConfigManager()
history_manager = HistoryManager()