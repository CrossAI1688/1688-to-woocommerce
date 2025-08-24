# 1688商品同步到WooCommerce工具

这是一个使用Streamlit构建的Web应用，可以自动抓取1688商品信息并上传到WooCommerce自建站。

## 功能特点

- 🔍 **智能抓取**: 自动抓取1688商品标题、价格、图片、描述等信息
- 🚀 **一键上传**: 将商品信息快速上传到WooCommerce商店
- ⚙️ **配置管理**: 安全存储WooCommerce API配置信息
- 📊 **操作历史**: 记录所有上传操作，便于跟踪和管理
- ✏️ **信息编辑**: 上传前可编辑商品信息
- 🛡️ **错误处理**: 完善的错误处理和日志记录

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run app.py
```

### 3. 访问应用

在浏览器中打开 `http://localhost:8501`

## 使用方法

### 第一步：配置WooCommerce API

1. 在侧边栏的"WooCommerce配置"中输入：
   - WooCommerce网站URL（如：https://your-site.com）
   - Consumer Key
   - Consumer Secret

2. 点击"保存配置"按钮，系统会自动测试连接

### 第二步：抓取1688商品信息

1. 在"商品链接输入"区域粘贴1688商品链接
2. 点击"抓取商品信息"按钮
3. 等待系统抓取并显示商品信息

### 第三步：上传到WooCommerce

1. 在"商品信息预览"区域检查抓取的信息
2. 如需要，可以在"编辑商品信息"中修改商品信息
3. 点击"上传到WooCommerce"按钮
4. 等待上传完成

## WooCommerce API配置

### 如何创建Consumer Key和Consumer Secret

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

### API权限要求

确保创建的API密钥具有以下权限：
- ✅ **products** - 读写权限（创建和更新商品）
- ✅ **media** - 读写权限（上传商品图片）
- ✅ **product_categories** - 读权限（获取商品分类）

### 详细文档参考

更多关于WooCommerce REST API的信息，请参考官方文档：  
🔗 [WooCommerce REST API Documentation](https://woocommerce.com/document/woocommerce-rest-api/)

## 支持的1688链接格式

- `https://detail.1688.com/offer/[商品ID].html`
- `https://m.1688.com/offer/[商品ID].html`
- 其他1688商品页面链接

## 故障排除

### 抓取失败
- 检查1688链接是否正确
- 确认1688页面是否需要登录
- 检查网络连接

### 上传失败
- 验证WooCommerce API配置
- 检查API权限设置
- 查看错误日志获取详细信息

### 图片上传问题
- 确保WooCommerce支持的图片格式
- 检查服务器存储空间
- 验证媒体库权限

## 文件结构

```
├── app.py                    # 主应用文件
├── scraper_1688.py          # 1688商品抓取模块
├── woocommerce_uploader.py  # WooCommerce上传模块
├── config_manager.py        # 配置管理模块
├── requirements.txt         # 依赖包列表
└── README.md               # 项目说明文档
```

