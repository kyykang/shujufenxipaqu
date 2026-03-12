# 致远OA数据抓取工具

基于Playwright的Web自动化工具，用于从致远Seeyon OA系统中安全地读取数据。

## ✨ 功能特点

- ✅ 自动登录致远OA系统
- ✅ 智能元素识别和点击
- ✅ 支持无界面（headless）模式
- ✅ 完整的日志记录
- ✅ 自动截图保存
- ✅ 支持定时任务
- ✅ 数据导出（CSV/JSON）
- ✅ Docker部署支持
- ✅ Linux服务器部署

## 🚀 快速开始

### 本地开发（macOS/Windows）

```bash
# 1. 克隆项目
git clone git@github.com:kyykang/shujufenxipaqu.git
cd shujufenxipaqu

# 2. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的OA账号密码

# 4. 运行
python3 click_dashboard_final.py
```

### Linux服务器部署

```bash
# 一键部署
bash deploy.sh

# 或使用Docker
docker-compose up
```

详细部署文档：[README_DEPLOY.md](README_DEPLOY.md)

## 📁 项目结构

```
.
├── oa_scraper.py              # 核心抓取工具
├── click_dashboard_final.py   # 主执行脚本
├── seeyon_helper.py           # Seeyon系统专用工具
├── scheduler.py               # 定时任务调度器
├── test_login.py              # 登录测试脚本
├── selector_finder.py         # 选择器查找工具
├── requirements.txt           # Python依赖
├── .env.example               # 配置文件模板
├── deploy.sh                  # Linux部署脚本
├── Dockerfile                 # Docker镜像配置
├── docker-compose.yml         # Docker Compose配置
├── examples/                  # 使用示例
│   ├── basic_usage.py        # 基础用法
│   └── advanced_usage.py     # 高级用法
└── docs/                      # 文档
    ├── QUICKSTART.md         # 快速开始
    ├── USAGE_GUIDE.md        # 使用指南
    ├── LINUX_DEPLOY.md       # Linux部署指南
    └── README_DEPLOY.md      # 部署快速参考
```

## 🔧 配置说明

编辑 `.env` 文件：

```env
# OA系统地址
OA_URL=https://your-oa-system.com/seeyon/main.do?method=index

# 登录凭证
OA_USERNAME=your_username
OA_PASSWORD=your_password

# 请求延迟（秒）
REQUEST_DELAY=2.0

# 文件传输配置（可选）
TRANSFER_METHOD=scp
REMOTE_HOST=your-server.com
REMOTE_USER=username
REMOTE_PATH=/path/to/destination
SSH_KEY_PATH=/path/to/key.pem  # 支持.pem格式（AWS EC2等）
```

### 使用.pem密钥（AWS/阿里云等）

```env
# AWS EC2示例
REMOTE_HOST=ec2-xx-xx-xx-xx.compute.amazonaws.com
REMOTE_USER=ec2-user
SSH_KEY_PATH=/path/to/aws-key.pem

# 设置密钥权限
# chmod 400 /path/to/aws-key.pem
```

详细配置：[PEM_KEY_GUIDE.md](PEM_KEY_GUIDE.md)

## 📖 使用示例

### 基本使用

```python
from oa_scraper import OAScraper

scraper = OAScraper()
scraper.start(headless=True)
scraper.login()

# 抓取数据
data = scraper.fetch_data(
    data_url="http://oa-system/data-page",
    selector=".data-container"
)

# 保存数据
scraper.save_to_csv(data, "output.csv")
scraper.close()
```

### 抓取表格数据

```python
table_data = scraper.fetch_table_data(
    table_url="http://oa-system/table-page",
    table_selector="table.data-table"
)
scraper.save_to_csv(table_data, "table.csv")
```

### 定时任务

```bash
# 运行调度器
python3 scheduler.py

# 或使用crontab
crontab -e
# 添加: 0 9 * * * cd /path/to/project && python3 click_dashboard_final.py
```

## 🐳 Docker部署

```bash
# 使用docker-compose（推荐）
docker-compose up

# 或使用Dockerfile
docker build -t oa-scraper .
docker run --rm -v $(pwd)/screenshots:/app/screenshots oa-scraper
```

## 📊 功能说明

### 核心功能

- **自动登录**：智能识别登录表单，支持多种登录方式
- **元素查找**：自动尝试多种选择器，提高成功率
- **截图保存**：关键步骤自动截图，便于调试
- **日志记录**：完整的操作日志，便于排查问题
- **错误处理**：完善的异常捕获和重试机制

### 数据导出

- CSV格式（支持中文）
- JSON格式
- Excel格式（需要额外安装openpyxl）

### 定时任务

- 支持crontab定时执行
- 支持systemd定时器
- 支持Docker定时任务

## 🔒 安全建议

1. **保护配置文件**：
   ```bash
   chmod 600 .env
   ```

2. **不要提交敏感信息**：
   - `.env` 文件已在 `.gitignore` 中
   - 截图可能包含敏感信息，不要上传

3. **定期更新密码**

4. **使用专用账号**：建议为自动化脚本创建专用OA账号

## 🐛 故障排查

### 登录失败

```bash
# 运行测试脚本
python3 test_login.py

# 查看日志
tail -f oa_scraper.log

# 查看截图
open screenshots/
```

### 找不到元素

```bash
# 使用选择器查找工具
python3 selector_finder.py

# 使用手动导航工具
python3 manual_navigate.py
```

### 系统依赖问题

```bash
# Ubuntu/Debian
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0

# CentOS/RHEL
sudo yum install -y nss nspr atk
```

## 📚 文档

- [快速开始](QUICKSTART.md) - 5分钟上手指南
- [使用指南](USAGE_GUIDE.md) - 详细使用说明
- [Linux部署](LINUX_DEPLOY.md) - Linux服务器部署
- [部署参考](README_DEPLOY.md) - 快速部署参考

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

本工具仅供学习和研究使用，使用前请确保：

1. 有权限访问目标OA系统
2. 遵守公司数据安全政策
3. 不要抓取敏感或机密信息
4. 合理控制访问频率，避免对系统造成压力

## 📞 联系方式

如有问题，请提交Issue或联系项目维护者。

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 强大的浏览器自动化工具
- [Python-dotenv](https://github.com/theskumar/python-dotenv) - 环境变量管理

---

⭐ 如果这个项目对你有帮助，请给个Star！
