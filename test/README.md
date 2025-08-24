# 测试文档

本目录包含1688商品同步到WooCommerce工具的全面测试套件。

## 🧪 测试模块

### 1. 1688抓取功能测试 (`test_scraper_1688.py`)
- **功能**: 测试1688商品信息抓取功能
- **覆盖范围**:
  - 基本商品信息抓取 (标题、价格、描述)
  - 图片提取功能
  - 规格参数提取功能
  - 移动版降级机制
  - 错误处理机制

### 2. WooCommerce连接测试 (`test_woocommerce.py`)
- **功能**: 测试WooCommerce API连接和配置
- **覆盖范围**:
  - 配置验证功能
  - API连接测试
  - 上传器创建功能
  - 错误处理和提示

### 3. Cookie存储测试 (`test_cookie_storage.py`)
- **功能**: 测试浏览器Cookie配置存储
- **覆盖范围**:
  - 配置保存功能
  - 配置加载功能
  - 配置清除功能
  - 数据结构验证

### 4. 端到端集成测试 (`test_integration.py`)
- **功能**: 测试完整的业务流程
- **覆盖范围**:
  - 抓取到上传的完整流程
  - 数据转换和验证
  - 系统集成测试

## 🚀 快速开始

### 运行所有测试
```bash
cd test
python run_tests.py
```

### 运行单个测试模块
```bash
# 1688抓取测试
python test_scraper_1688.py

# WooCommerce连接测试
python test_woocommerce.py

# Cookie存储测试
python test_cookie_storage.py

# 集成测试
python test_integration.py
```

## ⚙️ 配置要求

### 基础测试
大部分测试无需特殊配置即可运行，包括：
- 1688抓取功能测试
- Cookie存储功能测试
- 配置验证测试

### 完整测试 (需要真实WooCommerce配置)
为了运行完整的WooCommerce连接测试和集成测试，需要设置以下环境变量：

**Windows:**
```cmd
set WC_TEST_URL=https://your-woocommerce-site.com
set WC_TEST_KEY=ck_your_consumer_key
set WC_TEST_SECRET=cs_your_consumer_secret
```

**Linux/Mac:**
```bash
export WC_TEST_URL=https://your-woocommerce-site.com
export WC_TEST_KEY=ck_your_consumer_key
export WC_TEST_SECRET=cs_your_consumer_secret
```

### 获取WooCommerce API密钥
1. 登录WordPress后台
2. 导航至 **WooCommerce > 设置 > 高级 > REST API**
3. 点击 **添加密钥**
4. 权限选择 **读/写**
5. 复制生成的Consumer Key和Consumer Secret

## 📊 测试报告

运行测试后会自动生成测试报告：
- 控制台实时输出测试结果
- 保存详细报告到 `test_report_YYYYMMDD_HHMMSS.txt`
- 包含测试统计、详细结果和建议

## 🔧 测试环境

### Python版本
- 支持 Python 3.7+
- 推荐 Python 3.8+

### 依赖包
测试需要以下Python包：
- `streamlit`
- `beautifulsoup4`
- `requests`
- `woocommerce`
- `pandas`
- `pillow`
- `unittest` (Python内置)

### 网络要求
- 稳定的互联网连接
- 能够访问1688.com
- 能够访问你的WooCommerce网站

## 🎯 测试策略

### 单元测试
- 测试各个模块的独立功能
- 验证函数输入输出
- 检查错误处理机制

### 集成测试
- 测试模块间的协作
- 验证数据流转
- 检查端到端流程

### 性能测试
- 监控测试执行时间
- 检查资源使用情况
- 验证响应速度

## 🛠️ 故障排除

### 常见问题

**1. 1688抓取失败**
- 检查网络连接
- 确认1688网站可访问
- 可能需要处理反爬机制

**2. WooCommerce连接失败**
- 检查API配置是否正确
- 确认网站URL可访问
- 验证Consumer Key/Secret权限

**3. Cookie存储测试失败**
- Cookie存储需要在Streamlit环境中测试
- 单元测试主要验证函数调用
- 真实功能需要在Web应用中验证

**4. 测试超时**
- 增加网络超时时间
- 检查网络连接稳定性
- 分批运行测试模块

### 调试方法
1. 查看详细错误信息
2. 运行单个测试模块定位问题
3. 检查环境配置和依赖包
4. 查看测试报告文件

## 📝 贡献指南

### 添加新测试
1. 在相应的测试文件中添加测试方法
2. 遵循现有的命名规范
3. 添加适当的文档和注释
4. 更新本README文档

### 测试规范
- 使用描述性的测试方法名
- 添加适当的断言验证
- 包含正向和负向测试用例
- 处理异常情况

## 📞 技术支持

如果遇到测试相关问题，请联系：
- 邮箱：crossai1688@outlook.com
- 查看项目主README文档
- 检查测试日志和报告文件