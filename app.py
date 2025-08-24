import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Streamlit版本兼容性检测
def rerun_app():
    """根据Streamlit版本选择合适的重新运行方法"""
    try:
        st.rerun()  # 新版本(1.18.0+)
    except AttributeError:
        st.experimental_rerun()  # 旧版本

# 导入自定义模块
from scraper_1688 import scrape_1688_product
from woocommerce_uploader import create_woocommerce_uploader
from config_manager import config_manager, history_manager
# from browser_config_manager import browser_config_manager  # 已删除
from cookie_storage import save_wc_config, load_wc_config, clear_wc_config, get_wc_storage_info

# 页面配置
st.set_page_config(
    page_title="1688商品同步到WooCommerce",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    /* 隐藏右上角的Deploy按钮 */
    .stDeployButton {
        display: none;
    }
    
    /* 隐藏右上角的部署相关按钮 */
    [data-testid="stToolbar"] {
        display: none;
    }
    
    /* 隐藏Deploy菜单选项 */
    .css-17eq0hr, .css-1dp5vir {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# 配置管理函数
def load_wc_config_from_storage():
    """从Cookie加载WooCommerce配置"""
    # 优先使用当前会话的配置（作为缓存）
    if 'wc_config' in st.session_state:
        return st.session_state.wc_config
    
    # 从Cookie加载配置
    browser_config = load_wc_config()
    if browser_config:
        # 保存到session作为缓存
        st.session_state.wc_config = browser_config
        return browser_config
    
    return None

def save_wc_config_to_storage(config):
    """保存配置到Cookie"""
    try:
        success = save_wc_config(config)
        if success:
            # 同时保存到session_state作为缓存
            st.session_state.wc_config = config
        return success
    except Exception as e:
        st.error(f"保存配置失败: {e}")
        return False

def clear_wc_config_from_storage():
    """清除配置"""
    # 清除session配置
    if 'wc_config' in st.session_state:
        del st.session_state.wc_config
    # 清除Cookie配置
    clear_wc_config()

# 抓取商品信息函数
def scrape_product_info(url: str) -> Dict:
    """抓取1688商品信息"""
    try:
        result = scrape_1688_product(url)
        return result
    except Exception as e:
        return {"error": f"抓取失败: {str(e)}"}

# 上传商品到WooCommerce
def upload_to_woocommerce(product_info: Dict, wc_config: Dict) -> Dict:
    """上传商品到WooCommerce"""
    try:
        # 使用外部图片链接模式，避免上传权限问题
        uploader = create_woocommerce_uploader(wc_config, use_external_images=True)
        if not uploader:
            return {"success": False, "message": "无法创建WooCommerce连接"}
        
        result = uploader.upload_product(product_info)
        return result
    except Exception as e:
        return {"success": False, "message": f"上传失败: {str(e)}"}

# 主标题
st.markdown('<h1 class="main-header">🛒 1688商品同步到WooCommerce</h1>', unsafe_allow_html=True)

# 侧边栏配置
st.sidebar.header("⚙️ WooCommerce配置")

# 初始化已加载的配置
loaded_config = load_wc_config_from_storage()
default_url = loaded_config.get('url', '') if loaded_config else ''
default_key = loaded_config.get('consumer_key', '') if loaded_config else ''
default_secret = loaded_config.get('consumer_secret', '') if loaded_config else ''

if loaded_config:
    # 简单显示配置已加载
    st.sidebar.success("✅ 已加载保存的配置")

# WooCommerce配置表单
with st.sidebar.expander("WooCommerce API设置", expanded=True):
    wc_url = st.text_input("WooCommerce网站URL", value=default_url, placeholder="https://your-site.com")
    wc_consumer_key = st.text_input("Consumer Key", value=default_key, type="password")
    wc_consumer_secret = st.text_input("Consumer Secret", value=default_secret, type="password")
    
    # 按钮行
    col1, col2, col3 = st.columns(3)
    
    # 测试连接按钮
    with col1:
        test_connection_clicked = st.button("🔧 测试", use_container_width=True)
    
    # 保存配置按钮  
    with col2:
        save_config_clicked = st.button("💾 保存", use_container_width=True)
    
    # 清除配置按钮
    with col3:
        clear_config_clicked = st.button("🗑️ 清除", use_container_width=True)

# 处理测试连接按钮点击（在expander外部）
if test_connection_clicked:
    if all([wc_url.strip(), wc_consumer_key.strip(), wc_consumer_secret.strip()]):
        config = {
            "url": wc_url.strip(),
            "consumer_key": wc_consumer_key.strip(),
            "consumer_secret": wc_consumer_secret.strip()
        }
        
        with st.sidebar:
            with st.spinner("正在测试连接..."):
                test_result = config_manager.test_config(config)
            
            if test_result["success"]:
                st.success(f"✅ {test_result['message']}")
                if "details" in test_result and test_result["details"]:
                    st.info("📊 详细测试结果:")
                    st.text(test_result["details"])
            else:
                st.error(f"❌ {test_result['message']}")
                if "details" in test_result and test_result["details"]:
                    st.warning("📋 错误详情:")
                    st.text(test_result["details"])
    else:
        with st.sidebar:
            st.error("请填写完整的配置信息！")

# 处理保存配置按钮点击（在expander外部）
if save_config_clicked:
    if all([wc_url.strip(), wc_consumer_key.strip(), wc_consumer_secret.strip()]):
        config = {
            "url": wc_url.strip(),
            "consumer_key": wc_consumer_key.strip(),
            "consumer_secret": wc_consumer_secret.strip()
        }
        
        with st.sidebar:
            # 测试配置
            with st.spinner("正在测试连接..."):
                test_result = config_manager.test_config(config)
            
            if test_result["success"]:
                # 保存配置
                if save_wc_config_to_storage(config):
                    st.success("✅ 配置已保存！")
                else:
                    st.error("❌ 配置保存失败！")
                rerun_app()
            else:
                st.error(f"❌ 连接测试失败: {test_result['message']}")
                if "details" in test_result:
                    st.caption(f"详情: {test_result['details']}")
    else:
        with st.sidebar:
            st.error("请填写完整的配置信息！")

# 处理清除配置按钮点击
if clear_config_clicked:
    with st.sidebar:
        clear_wc_config_from_storage()
        st.info("🗑️ 配置已清除")
        rerun_app()

# 图片处理设置
with st.sidebar.expander("🖼️ 图片处理设置"):
    use_external_images = st.radio(
        "选择图片处理方式：",
        options=[True, False],
        format_func=lambda x: "直接使用原图链接（推荐）" if x else "上传到媒体库",
        index=0,
        help="直接使用原图链接可以避免401权限错误"
    )
    
    if use_external_images:
        st.success("✅ 将直接使用匹1688原图片链接，不上传到WooCommerce媒体库")
    else:
        st.warning("⚠️ 将上传图片到WooCommerce媒体库，需要相应权限")
# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 1688商品链接输入")
    
    # 1688商品链接输入
    product_url = st.text_area(
        "请输入1688商品链接：",
        placeholder="https://detail.1688.com/offer/...",
        height=100
    )
    
    # 抓取商品信息按钮
    if st.button("🔍 抓取商品信息", type="primary"):
        if product_url.strip():
            with st.spinner("正在抓取1688商品信息..."):
                result = scrape_product_info(product_url.strip())
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.product_info = result
                    st.success("✅ 1688商品信息抓取成功！")
                    rerun_app()
        else:
            st.error("请输入有效的1688商品链接！")

with col2:
    st.header("📦 商品信息预览")
    
    if 'product_info' in st.session_state:
        product_info = st.session_state.product_info
        
        # 显示商品信息
        st.subheader(f"📝 {product_info.get('title', 'N/A')}")
        
        # 显示平台信息
        platform_info = product_info.get('platform', '未知平台')
        st.caption(f"🏢 来源平台: {platform_info}")
        
        # 显示主图和图片数量信息
        images = product_info.get('images', [])
        if images:
            # 显示图片数量
            st.write(f"🖼️ **采集图片:** {len(images)}张")
            
            # 显示主图
            st.image(images[0], caption=f"主图 (1/{len(images)})", width=300)
            
            # 添加图片预览区域
            if len(images) > 1:
                with st.expander(f"📷 查看全部图片 ({len(images)}张)", expanded=False):
                    # 创建图片网格显示，每行3列
                    cols_per_row = 3
                    for i in range(0, len(images), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, col in enumerate(cols):
                            img_index = i + j
                            if img_index < len(images):
                                with col:
                                    st.image(images[img_index], 
                                            caption=f"图片 {img_index + 1}", 
                                            width=150)
                                    # 显示图片URL（截断显示）
                                    img_url = images[img_index]
                                    if len(img_url) > 40:
                                        display_url = img_url[:40] + "..."
                                    else:
                                        display_url = img_url
                                    st.caption(f"🔗 {display_url}")
        else:
            st.write("🖼️ **采集图片:** 0张")
            st.info("未采集到商品图片")
        
        st.write(f"💰 **价格:** {product_info.get('price', 'N/A')}")
        st.write(f"📋 **描述:** {product_info.get('description', 'N/A')[:200]}...")
        
        # 显示规格参数
        specifications = product_info.get('specifications', {})
        specs_count = len(specifications)
        if specs_count > 0:
            st.write(f"📈 **规格参数:** {specs_count}个")
            
            # 添加规格参数展示区域
            with st.expander(f"🔍 查看详细规格参数 ({specs_count}个)", expanded=False):
                # 创建规格参数表格显示，每行2列
                spec_items = list(specifications.items())
                cols_per_row = 2
                
                for i in range(0, len(spec_items), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j, col in enumerate(cols):
                        spec_index = i + j
                        if spec_index < len(spec_items):
                            key, value = spec_items[spec_index]
                            with col:
                                # 使用清晰的格式显示规格参数
                                st.markdown(f"**{key}:**")
                                st.text(value)
                                st.markdown("---")  # 分割线
        else:
            st.info("📈 未采集到规格参数")
        
        # 编辑商品信息
        with st.expander("✏️ 编辑商品信息", expanded=False):
            edited_title = st.text_input("商品标题", value=product_info.get('title', ''))
            edited_price = st.text_input("商品价格", value=product_info.get('price', ''))
            edited_description = st.text_area("商品描述", value=product_info.get('description', ''), height=100)
            
            if st.button("✅ 应用修改"):
                st.session_state.product_info.update({
                    'title': edited_title,
                    'price': edited_price,
                    'description': edited_description
                })
                st.success("商品信息已更新！")
                rerun_app()
        
        # 上传到WooCommerce按钮
        if st.button("🚀 上传到WooCommerce", type="primary", use_container_width=True):
            config = load_wc_config_from_storage()
            if config and all([config.get('url'), config.get('consumer_key'), config.get('consumer_secret')]):
                with st.spinner("正在上传商品到WooCommerce..."):
                    # 使用用户选择的图片处理模式
                    uploader = create_woocommerce_uploader(config, use_external_images=use_external_images)
                    if not uploader:
                        st.error("❌ 无法创建WooCommerce连接")
                    else:
                        upload_result = uploader.upload_product(product_info)
                    
                    if upload_result.get('success'):
                        st.success(f"✅ 商品上传成功！商品ID: {upload_result.get('product_id')}")
                        
                        # 添加到历史记录（使用会话历史）
                        history_record = {
                            "title": product_info.get('title', 'N/A'),
                            "source_url": product_info.get('url', 'N/A'),
                            "wc_product_id": upload_result.get('product_id'),
                            "status": "成功",
                            "message": "上传成功"
                        }
                        # 保存到会话历史
                        if 'session_history' not in st.session_state:
                            st.session_state.session_history = []
                        history_record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.session_history.append(history_record)
                        
                        # 清除当前商品信息
                        if 'product_info' in st.session_state:
                            del st.session_state.product_info
                        
                        rerun_app()
                    else:
                        error_msg = upload_result.get('message', '未知错误')
                        st.error(f"❌ {error_msg}")
                        
                        # 添加失败记录到历史（使用会话历史）
                        history_record = {
                            "title": product_info.get('title', 'N/A'),
                            "source_url": product_info.get('url', 'N/A'),
                            "wc_product_id": None,
                            "status": "失败",
                            "message": error_msg
                        }
                        # 保存到会话历史
                        if 'session_history' not in st.session_state:
                            st.session_state.session_history = []
                        history_record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.session_history.append(history_record)
            else:
                st.error("❌ 请先在侧边栏配置WooCommerce API信息！")

# 操作历史
st.header("📊 操作历史")

# 加载历史记录（使用会话历史）
history_records = st.session_state.get('session_history', [])

if history_records:
    # 显示统计信息
    col1, col2, col3 = st.columns(3)
    
    total_records = len(history_records)
    success_records = len([r for r in history_records if r.get('status') == '成功'])
    failure_records = total_records - success_records
    
    col1.metric("总操作数", total_records)
    col2.metric("成功数", success_records)
    col3.metric("失败数", failure_records)
    
    # 转换为DataFrame显示
    df_data = []
    for record in reversed(history_records[-20:]):  # 显示最近20条记录
        df_data.append({
            "时间": record.get('timestamp', 'N/A'),
            "商品标题": record.get('title', 'N/A')[:50] + ('...' if len(record.get('title', '')) > 50 else ''),
            "状态": "✅" if record.get('status') == '成功' else "❌",
            "WC商品ID": record.get('wc_product_id', 'N/A'),
            "消息": record.get('message', 'N/A')[:30] + ('...' if len(record.get('message', '')) > 30 else '')
        })
    
    if df_data:
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
    
    # 清空历史按钮
    if st.button("🗑️ 清空历史记录"):
        st.session_state.session_history = []
        st.success("历史记录已清空！")
        rerun_app()
else:
    st.info("暂无操作历史")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 如何使用这个Web工具：
    
    1. **配置WooCommerce API**
       - 在侧边栏输入您的WooCommerce网站URL
       - 输入Consumer Key和Consumer Secret
       - 点击"保存"按钮，配置会保存在当前浏览器会话中
    
    2. **抓取商品信息**
       - 输入1688商品链接
       - 点击"抓取商品信息"按钮
       - 预览商品信息和图片
    
    3. **上传到WooCommerce**
       - 确认商品信息无误
       - 点击"上传到WooCommerce"按钮
       - 等待上传完成
    
    ### 如何创建WooCommerce API密钥：
    
    #### 步骤1：进入WooCommerce REST API设置
    1. 登录您的WordPress后台
    2. 导航至 **WooCommerce > 设置**
    3. 点击 **高级** 选项卡
    4. 选择 **REST API** 子菜单
    
    #### 步骤2：创建新的API密钥
    1. 点击 **添加密钥** 按钮
    2. 填写以下信息：
       - **描述**: `1688商品同步工具` (或您喜欢的名称)
       - **用户**: 选择一个具有管理员权限的用户
       - **权限**: 选择 **读/写**
    3. 点击 **生成API密钥** 按钮
    
    #### 步骤3：保存API凭据
    1. 系统会显示生成的 **Consumer Key** 和 **Consumer Secret**
    2. **重要**: 立即复制并安全保存这些信息
    3. Consumer Secret只会显示一次，请务必保存
    
    #### 步骤4：在工具中配置
    1. 打开1688同步工具
    2. 在侧边栏"WooCommerce API设置"中输入：
       - **WooCommerce网站URL**: 您的网站地址（如：`https://your-site.com`）
       - **Consumer Key**: 刚刚复制的Consumer Key
       - **Consumer Secret**: 刚刚复制的Consumer Secret
    3. 点击 **测试** 按钮验证连接
    4. 测试成功后点击 **保存** 按钮
    
    ### API权限要求：
    
    确保创建的API密钥具有以下权限：
    - ✅ **products** - 读写权限（创建和更新商品）
    - ✅ **media** - 读写权限（上传商品图片）
    - ✅ **product_categories** - 读权限（获取商品分类）
    
    ### 详细文档参考：
    
    更多关于WooCommerce REST API的信息，请参考官方文档：  
    🔗 [WooCommerce REST API Documentation](https://woocommerce.com/document/woocommerce-rest-api/)
    
    ### 支持的1688链接格式：
    
    - `https://detail.1688.com/offer/[商品ID].html`
    - `https://m.1688.com/offer/[商品ID].html`
    - 其他1688商品页面链接
    
    ### 故障排除：
    
    - 如果抓取失败，请检查1688链接是否需要登录
    - 如果上传失败，请检查WooCommerce API配置
    - 网络问题可能导致超时，请重试
    - 如果配置丢失，请检查浏览器是否清除了localStorage数据
    """)

# 页脚
st.markdown("---")
st.markdown("💡 **提示:** 此工具仅用于合法的商品信息同步，请遵守相关平台的使用条款。")
st.markdown("📧 **支持:** 如遇问题请联系技术支持：crossai1688@outlook.com")