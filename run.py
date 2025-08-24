#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1688商品同步到WooCommerce工具启动脚本
运行此脚本启动Streamlit应用
"""

import subprocess
import sys
import os

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import streamlit
        import requests
        import bs4
        import woocommerce
        import PIL
        import pandas
        import cryptography
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("🛒 1688商品同步到WooCommerce工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查应用文件
    if not os.path.exists("app.py"):
        print("❌ 找不到app.py文件")
        sys.exit(1)
    
    print("🚀 启动Streamlit应用...")
    
    try:
        # 运行Streamlit应用
        subprocess.run([
            sys.executable, 
            "-m", 
            "streamlit", 
            "run", 
            "app.py",
            "--server.port=8509",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()