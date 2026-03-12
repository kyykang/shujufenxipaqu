# 使用.pem密钥文件连接SSH

## 什么是.pem文件？

.pem（Privacy Enhanced Mail）是一种常见的密钥文件格式，广泛用于：
- AWS EC2实例
- 阿里云ECS
- 腾讯云CVM
- 其他云服务提供商

## 快速配置

### 1. 准备.pem密钥文件

假设你有一个AWS EC2密钥文件：`my-ec2-key.pem`

```bash
# 设置正确的权限（重要！）
chmod 400 my-ec2-key.pem

# 或者
chmod 600 my-ec2-key.pem
```

### 2. 配置.env文件

```env
# 传输方式
TRANSFER_METHOD=scp

# 远程主机信息
REMOTE_HOST=ec2-xx-xx-xx-xx.compute.amazonaws.com
REMOTE_USER=ec2-user  # AWS EC2默认用户
REMOTE_PATH=/home/ec2-user/screenshots
REMOTE_PORT=22

# .pem密钥路径
SSH_KEY_PATH=/path/to/my-ec2-key.pem
```

### 3. 测试连接

```bash
# 测试SSH连接
ssh -i /path/to/my-ec2-key.pem ec2-user@your-host

# 测试SCP
scp -i /path/to/my-ec2-key.pem test.txt ec2-user@your-host:/tmp/
```

### 4. 运行脚本

```bash
# 自动发送截图
python3 click_dashboard_final.py

# 或手动发送
python3 send_screenshots.py latest
```

## 不同云服务商配置示例

### AWS EC2

```env
TRANSFER_METHOD=scp
REMOTE_HOST=ec2-54-123-45-67.compute-1.amazonaws.com
REMOTE_USER=ec2-user  # Amazon Linux
# REMOTE_USER=ubuntu  # Ubuntu系统
REMOTE_PATH=/home/ec2-user/screenshots
SSH_KEY_PATH=/Users/username/Downloads/my-aws-key.pem
```

### 阿里云ECS

```env
TRANSFER_METHOD=scp
REMOTE_HOST=47.xxx.xxx.xxx
REMOTE_USER=root  # 或其他用户
REMOTE_PATH=/data/screenshots
SSH_KEY_PATH=/path/to/aliyun-key.pem
```

### 腾讯云CVM

```env
TRANSFER_METHOD=scp
REMOTE_HOST=123.xxx.xxx.xxx
REMOTE_USER=ubuntu  # 或root
REMOTE_PATH=/home/ubuntu/screenshots
SSH_KEY_PATH=/path/to/tencent-key.pem
```

### 华为云ECS

```env
TRANSFER_METHOD=scp
REMOTE_HOST=119.xxx.xxx.xxx
REMOTE_USER=root
REMOTE_PATH=/data/screenshots
SSH_KEY_PATH=/path/to/huawei-key.pem
```

## 常见问题

### 1. Permission denied (publickey)

**原因**：密钥文件权限不正确

**解决**：
```bash
# 设置正确的权限
chmod 400 /path/to/key.pem

# 验证权限
ls -l /path/to/key.pem
# 应该显示: -r-------- 或 -rw-------
```

### 2. WARNING: UNPROTECTED PRIVATE KEY FILE!

**原因**：密钥文件权限过于宽松

**解决**：
```bash
chmod 400 /path/to/key.pem
```

### 3. Host key verification failed

**原因**：首次连接，SSH需要验证主机密钥

**解决**：
```bash
# 手动连接一次，接受主机密钥
ssh -i /path/to/key.pem user@host

# 或者禁用严格主机密钥检查（不推荐生产环境）
ssh -i /path/to/key.pem -o StrictHostKeyChecking=no user@host
```

### 4. Connection timed out

**原因**：
- 安全组/防火墙未开放22端口
- 主机地址错误
- 网络不通

**解决**：
```bash
# 检查网络连接
ping your-host

# 检查端口
telnet your-host 22

# 检查安全组规则（AWS/阿里云等）
# 确保入站规则允许22端口
```

### 5. No such file or directory

**原因**：远程路径不存在

**解决**：
```bash
# 先SSH登录创建目录
ssh -i /path/to/key.pem user@host "mkdir -p /path/to/destination"
```

## 密钥格式转换

### .pem转换为标准SSH密钥

如果需要转换格式：

```bash
# .pem转换为OpenSSH格式
ssh-keygen -p -m PEM -f key.pem

# 或者使用openssl
openssl rsa -in key.pem -out key_openssh
```

### 从.ppk转换为.pem（PuTTY格式）

```bash
# 安装puttygen
sudo apt-get install putty-tools

# 转换
puttygen key.ppk -O private-openssh -o key.pem
chmod 400 key.pem
```

## 安全最佳实践

### 1. 保护密钥文件

```bash
# 设置最严格的权限
chmod 400 key.pem

# 不要将密钥文件放在公共目录
mv key.pem ~/.ssh/
```

### 2. 使用密钥而非密码

```env
# 推荐：使用密钥
SSH_KEY_PATH=/path/to/key.pem

# 不推荐：使用密码
# REMOTE_PASSWORD=password
```

### 3. 限制密钥访问

在远程主机的 `~/.ssh/authorized_keys` 中限制密钥用途：

```bash
# 只允许从特定IP使用此密钥
from="192.168.1.100" ssh-rsa AAAAB3...

# 只允许执行特定命令
command="/usr/bin/rsync" ssh-rsa AAAAB3...
```

### 4. 定期轮换密钥

```bash
# 生成新密钥
ssh-keygen -t rsa -b 4096 -f new-key.pem

# 更新远程主机的authorized_keys
ssh-copy-id -i new-key.pem user@host

# 更新.env配置
# SSH_KEY_PATH=/path/to/new-key.pem
```

### 5. 备份密钥

```bash
# 加密备份
tar -czf keys-backup.tar.gz ~/.ssh/*.pem
gpg -c keys-backup.tar.gz

# 存储在安全位置
mv keys-backup.tar.gz.gpg /secure/location/
```

## 完整配置示例

### AWS EC2示例

```env
# OA系统配置
OA_URL=https://oa.company.com/seeyon/main.do?method=index
OA_USERNAME=user001
OA_PASSWORD=SecurePass123
REQUEST_DELAY=2.0

# 文件传输配置 - AWS EC2
TRANSFER_METHOD=scp
REMOTE_HOST=ec2-54-123-45-67.compute-1.amazonaws.com
REMOTE_USER=ec2-user
REMOTE_PATH=/home/ec2-user/oa-screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/Users/username/.ssh/aws-ec2-key.pem
```

### 阿里云ECS示例

```env
# OA系统配置
OA_URL=https://oa.company.com/seeyon/main.do?method=index
OA_USERNAME=user001
OA_PASSWORD=SecurePass123
REQUEST_DELAY=2.0

# 文件传输配置 - 阿里云ECS
TRANSFER_METHOD=rsync
REMOTE_HOST=47.xxx.xxx.xxx
REMOTE_USER=root
REMOTE_PATH=/data/oa-screenshots
REMOTE_PORT=22
SSH_KEY_PATH=/home/user/.ssh/aliyun-ecs-key.pem
```

## 测试脚本

创建测试脚本 `test_pem_connection.sh`：

```bash
#!/bin/bash

# 配置
PEM_KEY="/path/to/key.pem"
REMOTE_USER="ec2-user"
REMOTE_HOST="your-host.com"
REMOTE_PATH="/home/ec2-user/test"

echo "=== 测试.pem密钥连接 ==="
echo ""

# 1. 检查密钥文件
echo "1. 检查密钥文件..."
if [ ! -f "$PEM_KEY" ]; then
    echo "错误: 密钥文件不存在: $PEM_KEY"
    exit 1
fi

# 2. 检查权限
echo "2. 检查密钥权限..."
PERMS=$(stat -f "%A" "$PEM_KEY" 2>/dev/null || stat -c "%a" "$PEM_KEY" 2>/dev/null)
if [ "$PERMS" != "400" ] && [ "$PERMS" != "600" ]; then
    echo "警告: 密钥权限不正确 ($PERMS)，正在修复..."
    chmod 400 "$PEM_KEY"
fi

# 3. 测试SSH连接
echo "3. 测试SSH连接..."
ssh -i "$PEM_KEY" -o ConnectTimeout=10 "$REMOTE_USER@$REMOTE_HOST" "echo 'SSH连接成功'"
if [ $? -ne 0 ]; then
    echo "错误: SSH连接失败"
    exit 1
fi

# 4. 测试SCP
echo "4. 测试SCP传输..."
echo "test" > /tmp/test.txt
scp -i "$PEM_KEY" /tmp/test.txt "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"
if [ $? -eq 0 ]; then
    echo "SCP传输成功"
    rm /tmp/test.txt
else
    echo "错误: SCP传输失败"
    exit 1
fi

# 5. 清理
echo "5. 清理测试文件..."
ssh -i "$PEM_KEY" "$REMOTE_USER@$REMOTE_HOST" "rm -f $REMOTE_PATH/test.txt"

echo ""
echo "=== 所有测试通过！==="
```

运行测试：

```bash
chmod +x test_pem_connection.sh
./test_pem_connection.sh
```

## Python代码示例

直接在Python中使用.pem密钥：

```python
from file_transfer import FileTransfer
import os

# 设置环境变量
os.environ['TRANSFER_METHOD'] = 'scp'
os.environ['REMOTE_HOST'] = 'ec2-xx-xx-xx-xx.compute.amazonaws.com'
os.environ['REMOTE_USER'] = 'ec2-user'
os.environ['REMOTE_PATH'] = '/home/ec2-user/screenshots'
os.environ['SSH_KEY_PATH'] = '/path/to/my-key.pem'

# 发送文件
transfer = FileTransfer()
success = transfer.send_file('screenshot.png', method='scp')

if success:
    print("文件发送成功！")
else:
    print("文件发送失败")
```

## 故障排查清单

- [ ] 密钥文件存在且路径正确
- [ ] 密钥文件权限为400或600
- [ ] 远程主机地址正确
- [ ] 远程用户名正确
- [ ] 安全组/防火墙允许22端口
- [ ] 远程路径存在且有写权限
- [ ] 网络连接正常
- [ ] SSH服务运行正常

## 需要帮助？

如果遇到问题：

1. 查看日志：`tail -f oa_scraper.log`
2. 测试SSH连接：`ssh -i key.pem -v user@host`
3. 检查安全组规则
4. 验证密钥权限：`ls -l key.pem`
