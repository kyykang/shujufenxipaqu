# Linux服务器部署指南

## 系统要求

- Linux系统（Ubuntu 18.04+, CentOS 7+, Debian 10+等）
- Python 3.8+
- 无需图形界面（headless模式）

## 部署步骤

### 1. 安装Python依赖

```bash
# 安装pip（如果没有）
sudo apt-get update
sudo apt-get install -y python3-pip

# 或者在CentOS上
sudo yum install -y python3-pip

# 安装项目依赖
pip3 install -r requirements.txt
```

### 2. 安装Playwright浏览器

Playwright会自动下载Chromium浏览器（无需系统已安装浏览器）：

```bash
# 安装Chromium及其依赖
python3 -m playwright install chromium

# 安装系统依赖（重要！）
python3 -m playwright install-deps chromium
```

如果遇到权限问题，使用sudo：
```bash
sudo python3 -m playwright install-deps chromium
```

### 3. 上传项目文件

将以下文件上传到Linux服务器：

```
项目目录/
├── oa_scraper.py           # 核心抓取工具
├── click_dashboard_final.py # 主执行脚本
├── .env                     # 配置文件（包含账号密码）
├── requirements.txt         # Python依赖
└── screenshots/             # 截图保存目录（自动创建）
```

### 4. 配置环境变量

确保 `.env` 文件已正确配置：

```bash
cat .env
```

应该看到：
```
OA_URL=https://sales.antiy.cn/seeyon/main.do?method=index
OA_USERNAME=daping1
OA_PASSWORD=seeyon!@#123
REQUEST_DELAY=2.0
```

### 5. 测试运行

```bash
# 运行脚本（headless模式，不显示浏览器）
python3 click_dashboard_final.py
```

脚本会自动在headless模式下运行，无需图形界面。

### 6. 查看结果

```bash
# 查看截图
ls -lh screenshots/

# 查看日志
tail -f oa_scraper.log

# 下载截图到本地（在本地机器上执行）
scp user@server:/path/to/screenshots/*.png ./
```

## 定时任务设置

### 方式1: 使用crontab

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天早上9点执行）
0 9 * * * cd /path/to/project && /usr/bin/python3 click_dashboard_final.py >> /path/to/project/cron.log 2>&1

# 或者每小时执行一次
0 * * * * cd /path/to/project && /usr/bin/python3 click_dashboard_final.py >> /path/to/project/cron.log 2>&1
```

### 方式2: 使用systemd定时器

创建服务文件 `/etc/systemd/system/oa-scraper.service`：

```ini
[Unit]
Description=OA Dashboard Scraper
After=network.target

[Service]
Type=oneshot
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/click_dashboard_final.py
StandardOutput=append:/path/to/project/service.log
StandardError=append:/path/to/project/service.log

[Install]
WantedBy=multi-user.target
```

创建定时器文件 `/etc/systemd/system/oa-scraper.timer`：

```ini
[Unit]
Description=Run OA Scraper daily

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用定时器：
```bash
sudo systemctl daemon-reload
sudo systemctl enable oa-scraper.timer
sudo systemctl start oa-scraper.timer

# 查看状态
sudo systemctl status oa-scraper.timer
```

## 常见问题

### 1. 缺少系统依赖

如果遇到类似错误：
```
Error: Host system is missing dependencies
```

解决方法：
```bash
# Ubuntu/Debian
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# CentOS/RHEL
sudo yum install -y \
    nss \
    nspr \
    atk \
    at-spi2-atk \
    cups-libs \
    libdrm \
    libxkbcommon \
    libXcomposite \
    libXdamage \
    libXfixes \
    libXrandr \
    mesa-libgbm \
    alsa-lib
```

### 2. 权限问题

```bash
# 确保脚本有执行权限
chmod +x click_dashboard_final.py

# 确保screenshots目录可写
mkdir -p screenshots
chmod 755 screenshots
```

### 3. 字体问题（中文显示）

如果截图中中文显示为方块：

```bash
# Ubuntu/Debian
sudo apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei

# CentOS/RHEL
sudo yum install -y wqy-zenhei-fonts wqy-microhei-fonts
```

### 4. 内存不足

如果服务器内存较小（<2GB），可以限制浏览器资源：

修改 `oa_scraper.py` 中的浏览器启动参数：
```python
self.browser = playwright.chromium.launch(
    headless=headless,
    args=[
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-gpu'
    ]
)
```

## 监控和维护

### 查看日志

```bash
# 实时查看日志
tail -f oa_scraper.log

# 查看最近的错误
grep ERROR oa_scraper.log | tail -20

# 查看今天的日志
grep "$(date +%Y-%m-%d)" oa_scraper.log
```

### 清理旧截图

```bash
# 删除7天前的截图
find screenshots/ -name "*.png" -mtime +7 -delete

# 或者添加到crontab每周清理
0 0 * * 0 find /path/to/project/screenshots/ -name "*.png" -mtime +7 -delete
```

### 磁盘空间监控

```bash
# 检查截图目录大小
du -sh screenshots/

# 检查磁盘使用情况
df -h
```

## 性能优化

### 1. 减少等待时间

如果网络稳定，可以减少 `.env` 中的延迟：
```
REQUEST_DELAY=1.0
```

### 2. 禁用图片加载（可选）

如果只需要文本数据，可以禁用图片加载以提高速度。

### 3. 使用代理（如果需要）

在 `oa_scraper.py` 中添加代理配置：
```python
self.context = self.browser.new_context(
    proxy={
        "server": "http://proxy-server:port",
        "username": "user",
        "password": "pass"
    }
)
```

## 安全建议

1. **保护.env文件**：
```bash
chmod 600 .env
```

2. **使用专用用户运行**：
```bash
sudo useradd -m -s /bin/bash oascraper
sudo su - oascraper
```

3. **定期更新密码**：
定期更新 `.env` 中的密码

4. **限制网络访问**：
只允许访问OA系统的IP

## 备份方案

```bash
# 备份截图
tar -czf screenshots_backup_$(date +%Y%m%d).tar.gz screenshots/

# 备份到远程服务器
rsync -avz screenshots/ backup-server:/backup/oa-screenshots/
```

## 故障排查

如果脚本运行失败：

1. 检查日志：`cat oa_scraper.log`
2. 检查网络：`ping sales.antiy.cn`
3. 手动测试：`python3 -c "from playwright.sync_api import sync_playwright; print('OK')"`
4. 检查浏览器：`python3 -m playwright install --dry-run chromium`

## 联系支持

如果遇到问题，请提供：
- 错误日志
- 系统信息：`uname -a`
- Python版本：`python3 --version`
- Playwright版本：`pip3 show playwright`
