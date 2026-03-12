# 快速部署指南

## 方式1: 直接部署（推荐）

### 上传文件到Linux服务器

```bash
# 在本地打包
tar -czf oa-scraper.tar.gz \
    oa_scraper.py \
    click_dashboard_final.py \
    requirements.txt \
    .env \
    deploy.sh

# 上传到服务器
scp oa-scraper.tar.gz user@your-server:/home/user/

# 在服务器上解压
ssh user@your-server
cd /home/user/
tar -xzf oa-scraper.tar.gz
```

### 一键部署

```bash
# 运行部署脚本
bash deploy.sh
```

脚本会自动：
- 检查Python版本
- 安装依赖
- 安装Playwright浏览器
- 安装系统依赖
- 创建必要目录
- 测试运行

### 手动部署

如果自动脚本失败，可以手动执行：

```bash
# 1. 安装Python依赖
pip3 install -r requirements.txt --user

# 2. 安装Playwright浏览器
python3 -m playwright install chromium

# 3. 安装系统依赖（需要sudo）
sudo python3 -m playwright install-deps chromium

# 4. 创建目录
mkdir -p screenshots output

# 5. 运行测试
python3 click_dashboard_final.py
```

## 方式2: Docker部署（最简单）

### 使用docker-compose（推荐）

```bash
# 1. 确保已安装Docker和docker-compose
docker --version
docker-compose --version

# 2. 运行
docker-compose up

# 3. 查看截图
ls -lh screenshots/
```

### 使用Dockerfile

```bash
# 1. 构建镜像
docker build -t oa-scraper .

# 2. 运行容器
docker run --rm \
    -v $(pwd)/screenshots:/app/screenshots \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/.env:/app/.env \
    oa-scraper

# 3. 查看结果
ls -lh screenshots/
```

## 方式3: 定时任务

### 使用crontab

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天早上9点）
0 9 * * * cd /path/to/project && /usr/bin/python3 click_dashboard_final.py >> /path/to/project/cron.log 2>&1
```

### 使用Docker定时任务

```bash
# 添加到crontab
0 9 * * * docker-compose -f /path/to/docker-compose.yml up >> /path/to/cron.log 2>&1
```

## 验证部署

### 检查截图

```bash
ls -lh screenshots/
```

应该看到类似：
```
marketing_dashboard_20260312_105253.png
```

### 检查日志

```bash
tail -f oa_scraper.log
```

应该看到：
```
✓ 任务完成！截图已保存: screenshots/marketing_dashboard_xxx.png
```

## 常见问题

### 1. 没有sudo权限

如果无法使用sudo安装系统依赖，联系系统管理员安装以下包：

Ubuntu/Debian:
```bash
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2
```

CentOS/RHEL:
```bash
sudo yum install -y nss nspr atk at-spi2-atk cups-libs libdrm \
    libxkbcommon libXcomposite libXdamage libXfixes libXrandr \
    mesa-libgbm alsa-lib
```

### 2. 内存不足

如果服务器内存<2GB，使用Docker方式并限制内存：

```bash
docker run --rm --memory=1g \
    -v $(pwd)/screenshots:/app/screenshots \
    oa-scraper
```

### 3. 网络问题

如果无法访问OA系统，检查：

```bash
# 测试网络连接
ping sales.antiy.cn

# 测试端口
telnet sales.antiy.cn 443
```

### 4. 中文乱码

安装中文字体：

```bash
# Ubuntu/Debian
sudo apt-get install -y fonts-wqy-zenhei fonts-wqy-microhei

# CentOS/RHEL
sudo yum install -y wqy-zenhei-fonts
```

## 下载截图到本地

```bash
# 方式1: scp
scp user@server:/path/to/screenshots/*.png ./

# 方式2: rsync
rsync -avz user@server:/path/to/screenshots/ ./local-screenshots/

# 方式3: 如果使用Docker
docker cp container-name:/app/screenshots ./
```

## 性能优化

### 减少资源占用

在 `.env` 中调整：
```
REQUEST_DELAY=1.0  # 减少延迟
```

### 清理旧文件

```bash
# 删除7天前的截图
find screenshots/ -name "*.png" -mtime +7 -delete

# 添加到crontab自动清理
0 0 * * 0 find /path/to/screenshots/ -name "*.png" -mtime +7 -delete
```

## 监控

### 查看运行状态

```bash
# 查看最近的日志
tail -20 oa_scraper.log

# 查看错误
grep ERROR oa_scraper.log

# 查看今天的运行记录
grep "$(date +%Y-%m-%d)" oa_scraper.log
```

### 磁盘空间

```bash
# 检查截图目录大小
du -sh screenshots/

# 检查磁盘使用
df -h
```

## 安全建议

1. 保护配置文件：
```bash
chmod 600 .env
```

2. 定期更新密码

3. 限制文件访问权限：
```bash
chmod 700 screenshots/
```

4. 使用专用用户运行：
```bash
sudo useradd -m -s /bin/bash oascraper
sudo chown -R oascraper:oascraper /path/to/project
sudo su - oascraper
```

## 需要帮助？

查看详细文档：
- `LINUX_DEPLOY.md` - 完整的Linux部署指南
- `USAGE_GUIDE.md` - 使用指南
- `README.md` - 项目说明

或查看日志文件：
```bash
cat oa_scraper.log
```
