# 文件传输配置指南

## 概述

支持多种方式将截图自动发送到远程主机：
- **SCP** - 简单可靠，适合单文件传输
- **rsync** - 高效增量同步，适合批量传输
- **SFTP** - 基于SSH的文件传输协议
- **HTTP** - 通过HTTP API上传

## 配置方式

### 1. SCP方式（推荐）

最简单的方式，使用SSH协议传输文件。

#### 配置 .env 文件：

```env
TRANSFER_METHOD=scp
REMOTE_HOST=192.168.1.100
REMOTE_USER=username
REMOTE_PATH=/home/username/screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/home/username/.ssh/id_rsa  # 可选
```

#### 设置SSH密钥（推荐）：

```bash
# 1. 生成SSH密钥（如果还没有）
ssh-keygen -t rsa -b 4096

# 2. 复制公钥到远程主机
ssh-copy-id username@192.168.1.100

# 3. 测试连接
ssh username@192.168.1.100
```

#### 使用密码认证：

如果不使用SSH密钥，可以配置密码：

```env
REMOTE_PASSWORD=your_password
```

### 2. rsync方式（批量传输推荐）

更高效，支持增量同步，适合传输大量文件。

#### 配置 .env 文件：

```env
TRANSFER_METHOD=rsync
REMOTE_HOST=192.168.1.100
REMOTE_USER=username
REMOTE_PATH=/home/username/screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/home/username/.ssh/id_rsa
```

#### 安装rsync：

```bash
# Ubuntu/Debian
sudo apt-get install rsync

# CentOS/RHEL
sudo yum install rsync

# macOS (通常已安装)
brew install rsync
```

### 3. SFTP方式

使用Python的paramiko库，纯Python实现。

#### 配置 .env 文件：

```env
TRANSFER_METHOD=sftp
REMOTE_HOST=192.168.1.100
REMOTE_USER=username
REMOTE_PATH=/home/username/screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/home/username/.ssh/id_rsa  # 或使用密码
REMOTE_PASSWORD=your_password
```

#### 安装依赖：

```bash
pip install paramiko
```

### 4. HTTP方式

通过HTTP API上传文件。

#### 配置 .env 文件：

```env
TRANSFER_METHOD=http
UPLOAD_URL=http://your-server.com/api/upload
UPLOAD_TOKEN=your_auth_token  # 可选
```

#### 服务端示例（Flask）：

```python
from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # 验证token
    token = request.headers.get('Authorization')
    if token != 'Bearer your_auth_token':
        return {'error': 'Unauthorized'}, 401
    
    # 保存文件
    file = request.files['file']
    file.save(os.path.join('/path/to/save', file.filename))
    
    return {'success': True}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 使用方法

### 自动发送（集成在主脚本中）

运行主脚本时自动发送：

```bash
python3 click_dashboard_final.py
```

脚本会在截图后自动发送到配置的远程主机。

### 手动发送

使用独立的发送脚本：

```bash
# 发送最新的截图
python3 send_screenshots.py latest

# 发送所有截图
python3 send_screenshots.py all

# 使用rsync发送整个目录（最快）
python3 send_screenshots.py dir

# 发送指定文件
python3 send_screenshots.py screenshots/screenshot.png
```

### 在代码中使用

```python
from file_transfer import FileTransfer

transfer = FileTransfer()

# 发送单个文件
transfer.send_file('screenshots/screenshot.png', method='scp')

# 发送整个目录
transfer.send_directory('screenshots', method='rsync')
```

## 测试配置

### 测试SSH连接

```bash
# 测试SSH连接
ssh username@192.168.1.100

# 测试SCP
scp test.txt username@192.168.1.100:/tmp/

# 测试rsync
rsync -avz test.txt username@192.168.1.100:/tmp/
```

### 测试Python脚本

```bash
# 创建测试文件
echo "test" > test.txt

# 测试发送
python3 -c "
from file_transfer import FileTransfer
transfer = FileTransfer()
transfer.send_file('test.txt', method='scp')
"
```

## 常见问题

### 1. Permission denied (publickey)

SSH密钥认证失败。

解决方法：
```bash
# 检查SSH密钥
ls -la ~/.ssh/

# 重新复制公钥
ssh-copy-id username@remote-host

# 或者使用密码认证
# 在.env中添加: REMOTE_PASSWORD=your_password
```

### 2. Connection refused

远程主机SSH服务未启动或端口不对。

解决方法：
```bash
# 检查SSH服务
ssh -p 22 username@remote-host

# 如果端口不是22，修改.env中的REMOTE_PORT
```

### 3. No such file or directory

远程路径不存在。

解决方法：
```bash
# 在远程主机创建目录
ssh username@remote-host "mkdir -p /path/to/destination"
```

### 4. rsync: command not found

rsync未安装。

解决方法：
```bash
# Ubuntu/Debian
sudo apt-get install rsync

# CentOS/RHEL
sudo yum install rsync
```

### 5. paramiko not found

Python库未安装。

解决方法：
```bash
pip install paramiko
```

## 安全建议

1. **使用SSH密钥认证**：
   - 比密码更安全
   - 不需要在配置文件中存储密码

2. **限制SSH密钥权限**：
   ```bash
   chmod 600 ~/.ssh/id_rsa
   chmod 644 ~/.ssh/id_rsa.pub
   ```

3. **使用专用账号**：
   - 在远程主机创建专用账号用于接收文件
   - 限制该账号的权限

4. **配置防火墙**：
   ```bash
   # 只允许特定IP访问SSH
   sudo ufw allow from 192.168.1.0/24 to any port 22
   ```

5. **定期清理旧文件**：
   ```bash
   # 在远程主机设置定时清理
   0 0 * * 0 find /path/to/screenshots -mtime +30 -delete
   ```

## 性能优化

### 使用rsync增量同步

```bash
# 只传输新文件和修改的文件
rsync -avz --update screenshots/ user@host:/path/
```

### 压缩传输

```bash
# SCP使用压缩
scp -C file.png user@host:/path/

# rsync使用压缩（默认已启用-z）
rsync -avz file.png user@host:/path/
```

### 并行传输

```python
# 使用多线程并行发送多个文件
from concurrent.futures import ThreadPoolExecutor

def send_files_parallel(files):
    transfer = FileTransfer()
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(
            lambda f: transfer.send_file(f, method='scp'),
            files
        )
    return list(results)
```

## 监控和日志

### 查看传输日志

```bash
# 查看日志
tail -f oa_scraper.log | grep "发送"

# 查看传输成功的文件
grep "文件发送成功" oa_scraper.log
```

### 监控传输状态

```bash
# 实时监控rsync进度
rsync -avz --progress screenshots/ user@host:/path/
```

## 定时任务示例

### 每小时同步一次

```bash
crontab -e

# 添加：每小时同步screenshots目录
0 * * * * cd /path/to/project && python3 send_screenshots.py dir >> /path/to/sync.log 2>&1
```

### 截图后立即发送

主脚本已集成自动发送功能，无需额外配置。

## 故障排查

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试网络连接

```bash
# 测试主机可达性
ping remote-host

# 测试端口
telnet remote-host 22

# 测试SSH
ssh -vvv username@remote-host
```

### 检查磁盘空间

```bash
# 本地
df -h

# 远程
ssh username@remote-host "df -h"
```

## 示例配置

### 完整的 .env 配置示例

```env
# OA系统配置
OA_URL=https://oa.company.com/seeyon/main.do?method=index
OA_USERNAME=user001
OA_PASSWORD=SecurePass123

# 文件传输配置
TRANSFER_METHOD=rsync
REMOTE_HOST=backup.company.com
REMOTE_USER=backup
REMOTE_PATH=/data/oa-screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/home/user/.ssh/id_rsa
```

## 需要帮助？

如果遇到问题：
1. 查看日志文件：`oa_scraper.log`
2. 测试SSH连接
3. 检查防火墙设置
4. 验证远程路径权限
