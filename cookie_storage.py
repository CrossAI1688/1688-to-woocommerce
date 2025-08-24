#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Cookie的配置存储管理器
使用streamlit-cookies-manager实现可靠的浏览器配置持久化
适合Web应用部署环境，提供真正的租户隔离
"""

import streamlit as st
import json
import base64
from typing import Dict, Optional
from datetime import datetime, timedelta

try:
    import extra_streamlit_components as stx
    COOKIES_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    COOKIES_AVAILABLE = False
    IMPORT_ERROR = str(e)
except Exception as e:
    COOKIES_AVAILABLE = False
    IMPORT_ERROR = f"Import exception: {str(e)}"

class CookieStorageManager:
    """基于extra-streamlit-components的配置存储管理器"""
    
    def __init__(self, cookie_prefix: str = "wc_config_"):
        """
        初始化Cookie存储管理器
        
        Args:
            cookie_prefix: Cookie前缀
        """
        self.cookie_prefix = cookie_prefix
        self.cookie_manager = None
        self.init_error = None
        self._init_cookie_manager()
    
    def _init_cookie_manager(self):
        """初始化Cookie管理器"""
        if not COOKIES_AVAILABLE:
            self.init_error = IMPORT_ERROR or "extra-streamlit-components not available"
            return None
        
        try:
            # 使用extra-streamlit-components的CookieManager
            self.cookie_manager = stx.CookieManager()
            self.init_error = None
            return self.cookie_manager
            
        except Exception as e:
            # 记录初始化错误
            self.init_error = f"CookieManager init failed: {str(e)}"
            return None
    
    def is_ready(self) -> bool:
        """检查Cookie管理器是否准备就绪"""
        return COOKIES_AVAILABLE and self.cookie_manager is not None
    
    def _get_cookie_key(self, key: str) -> str:
        """获取带前缀的Cookie键名"""
        return f"{self.cookie_prefix}{key}"
    
    def save_config(self, key: str, data: Dict, expires_days: int = 365) -> bool:
        """
        保存配置到Cookie
        
        Args:
            key: 配置键名
            data: 配置数据
            expires_days: Cookie过期天数
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not self.is_ready():
                print(f"❌ Cookie管理器未准备就绪: {self.init_error}")
                return False
            
            # 准备要保存的数据，包装成标准格式
            config_data = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            cookie_key = self._get_cookie_key(key)
            print(f"🍪 准备保存Cookie: {cookie_key}")
            print(f"📊 数据内容: {config_data}")
            
            # 使用extra-streamlit-components保存到Cookie
            # 注意：直接保存dict对象，让CookieManager自动处理序列化
            try:
                self.cookie_manager.set(cookie_key, config_data)
                print(f"✅ Cookie设置成功: {cookie_key}")
                
                # 立即验证保存是否成功
                import time
                time.sleep(0.1)  # 短暂等待
                
                verify_data = self.cookie_manager.get(cookie_key)
                if verify_data:
                    print(f"✅ Cookie验证成功，已保存")
                    print(f"📝 验证数据类型: {type(verify_data)}")
                    return True
                else:
                    print(f"⚠️ Cookie保存后验证失败")
                    return False
                    
            except Exception as e:
                print(f"❌ Cookie设置失败: {str(e)}")
                return False
            
        except Exception as e:
            print(f"❌ 保存配置时发生错误: {str(e)}")
            return False
    
    def load_config(self, key: str) -> Optional[Dict]:
        """
        从Cookie加载配置
        
        Args:
            key: 配置键名
            
        Returns:
            Dict: 配置数据，如果没有找到返回None
        """
        try:
            if not self.is_ready():
                print(f"❌ Cookie管理器未准备就绪: {self.init_error}")
                return None
            
            cookie_key = self._get_cookie_key(key)
            print(f"🔍 尝试加载Cookie: {cookie_key}")
            
            # 从Cookie加载，使用简化的API
            cookie_data = self.cookie_manager.get(cookie_key)
            
            if not cookie_data:
                print(f"⚠️ Cookie数据为空: {cookie_key}")
                return None
            
            print(f"✅ 找到Cookie数据，长度: {len(str(cookie_data))}")
            print(f"📊 Cookie数据类型: {type(cookie_data)}")
            
            # 根据数据类型进行不同处理
            if isinstance(cookie_data, dict):
                # 如果已经是字典，直接使用
                config_data = cookie_data
                print(f"✅ Cookie数据已是dict格式")
            elif isinstance(cookie_data, str):
                # 如果是字符串，解析JSON
                config_data = json.loads(cookie_data)
                print(f"✅ 从JSON字符串解析成功")
            else:
                print(f"❌ 未知的Cookie数据格式: {type(cookie_data)}")
                return None
            
            # 获取实际的配置数据
            result = config_data.get('data') if isinstance(config_data, dict) else config_data
            
            if result:
                print(f"✅ 成功加载配置，包含 {len(result)} 个字段")
                print(f"📝 配置字段: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            return result
            
        except Exception as e:
            print(f"❌ 加载配置时发生错误: {str(e)}")
            # 打印更详细的调试信息
            try:
                cookie_data = self.cookie_manager.get(cookie_key)
                print(f"🔍 调试信息 - Cookie原始数据: {cookie_data}")
                print(f"🔍 调试信息 - 数据类型: {type(cookie_data)}")
            except:
                pass
            return None
    
    def clear_config(self, key: str) -> bool:
        """
        清除配置
        
        Args:
            key: 配置键名
            
        Returns:
            bool: 清除是否成功
        """
        try:
            if not self.is_ready():
                print(f"❌ Cookie管理器未准备就绪: {self.init_error}")
                return False
            
            cookie_key = self._get_cookie_key(key)
            print(f"🗑️ 清除Cookie: {cookie_key}")
            
            # 清除Cookie，使用简化的API
            try:
                self.cookie_manager.delete(cookie_key)
                print(f"✅ Cookie清除成功: {cookie_key}")
                return True
            except Exception as e:
                print(f"❌ Cookie清除失败: {str(e)}")
                return False
            
        except Exception as e:
            print(f"❌ 清除配置时发生错误: {str(e)}")
            return False
    
    def get_all_keys(self) -> list:
        """获取所有配置键名"""
        try:
            if not self.is_ready():
                return []
            
            # 获取所有Cookie键名并过滤出带前缀的，使用简化的API
            all_cookies = self.cookie_manager.get_all()
            filtered_keys = []
            
            if all_cookies:
                for cookie_key in all_cookies.keys():
                    if cookie_key.startswith(self.cookie_prefix):
                        # 移除前缀获取原始键名
                        original_key = cookie_key[len(self.cookie_prefix):]
                        filtered_keys.append(original_key)
            
            return filtered_keys
            
        except Exception:
            # 静默处理错误，避免打印引起key冲突
            return []
    
    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        info = {
            'cookies_available': COOKIES_AVAILABLE,
            'manager_ready': self.is_ready(),
            'storage_type': 'Cookie' if self.is_ready() else 'Unavailable',
            'import_error': IMPORT_ERROR,
            'init_error': getattr(self, 'init_error', None)
        }
        
        if self.is_ready():
            try:
                info['cookie_keys'] = self.get_all_keys()
            except Exception:
                info['cookie_keys'] = []
        
        return info
    



# 全局实例（延迟初始化）
_cookie_storage_instance = None

def get_cookie_storage():
    """获取Cookie存储管理器实例（延迟初始化）"""
    global _cookie_storage_instance
    if _cookie_storage_instance is None:
        _cookie_storage_instance = CookieStorageManager()
    return _cookie_storage_instance

# 便捷函数，兼容原有接口
def save_wc_config(config: Dict) -> bool:
    """保存WooCommerce配置到Cookie"""
    return get_cookie_storage().save_config('wc_config', config)

def load_wc_config() -> Optional[Dict]:
    """从Cookie加载WooCommerce配置"""
    return get_cookie_storage().load_config('wc_config')

def clear_wc_config() -> bool:
    """清除WooCommerce配置"""
    return get_cookie_storage().clear_config('wc_config')

def get_wc_storage_info() -> Dict:
    """获取WooCommerce存储信息"""
    return get_cookie_storage().get_storage_info()