"""
文件传输工具
支持多种方式将截图发送到远程主机
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class FileTransfer:
    """文件传输类"""
    
    def __init__(self):
        """初始化配置"""
        self.remote_host = os.getenv('REMOTE_HOST')
        self.remote_user = os.getenv('REMOTE_USER')
        self.remote_path = os.getenv('REMOTE_PATH')
        self.remote_port = os.getenv('REMOTE_PORT', '22')
        self.ssh_key = os.getenv('SSH_KEY_PATH')
        
    def send_via_scp(self, local_file):
        """使用SCP发送文件"""
        import subprocess
        
        if not all([self.remote_host, self.remote_user, self.remote_path]):
            logger.error("缺少远程主机配置")
            return False
        
        try:
            cmd = [
                'scp',
                '-P', self.remote_port,
            ]
            
            if self.ssh_key:
                cmd.extend(['-i', self.ssh_key])
            
            cmd.extend([
                local_file,
                f'{self.remote_user}@{self.remote_host}:{self.remote_path}'
            ])
            
            logger.info(f"发送文件: {local_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"文件发送成功: {local_file}")
                return True
            else:
                logger.error(f"发送失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"SCP发送失败: {e}")
            return False

    def send_via_rsync(self, local_file):
        """使用rsync发送文件（更高效）"""
        import subprocess
        
        if not all([self.remote_host, self.remote_user, self.remote_path]):
            logger.error("缺少远程主机配置")
            return False
        
        try:
            cmd = [
                'rsync',
                '-avz',
                '-e', f'ssh -p {self.remote_port}',
            ]
            
            if self.ssh_key:
                cmd[2] = f'ssh -p {self.remote_port} -i {self.ssh_key}'
            
            cmd.extend([
                local_file,
                f'{self.remote_user}@{self.remote_host}:{self.remote_path}'
            ])
            
            logger.info(f"使用rsync发送: {local_file}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"文件发送成功: {local_file}")
                return True
            else:
                logger.error(f"发送失败: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"rsync发送失败: {e}")
            return False
    
    def send_via_sftp(self, local_file):
        """使用SFTP发送文件"""
        try:
            import paramiko
            
            if not all([self.remote_host, self.remote_user, self.remote_path]):
                logger.error("缺少远程主机配置")
                return False
            
            # 创建SSH客户端
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 连接
            connect_kwargs = {
                'hostname': self.remote_host,
                'port': int(self.remote_port),
                'username': self.remote_user,
            }
            
            if self.ssh_key:
                connect_kwargs['key_filename'] = self.ssh_key
            else:
                password = os.getenv('REMOTE_PASSWORD')
                if password:
                    connect_kwargs['password'] = password
            
            ssh.connect(**connect_kwargs)
            
            # 使用SFTP传输
            sftp = ssh.open_sftp()
            
            remote_file = os.path.join(self.remote_path, os.path.basename(local_file))
            logger.info(f"使用SFTP发送: {local_file} -> {remote_file}")
            
            sftp.put(local_file, remote_file)
            sftp.close()
            ssh.close()
            
            logger.info(f"文件发送成功: {local_file}")
            return True
            
        except ImportError:
            logger.error("paramiko未安装，请运行: pip install paramiko")
            return False
        except Exception as e:
            logger.error(f"SFTP发送失败: {e}")
            return False

    def send_via_http(self, local_file):
        """使用HTTP POST发送文件"""
        try:
            import requests
            
            upload_url = os.getenv('UPLOAD_URL')
            if not upload_url:
                logger.error("缺少UPLOAD_URL配置")
                return False
            
            with open(local_file, 'rb') as f:
                files = {'file': f}
                
                # 可选的认证
                auth_token = os.getenv('UPLOAD_TOKEN')
                headers = {}
                if auth_token:
                    headers['Authorization'] = f'Bearer {auth_token}'
                
                logger.info(f"使用HTTP POST发送: {local_file}")
                response = requests.post(upload_url, files=files, headers=headers)
                
                if response.status_code == 200:
                    logger.info(f"文件上传成功: {local_file}")
                    return True
                else:
                    logger.error(f"上传失败: {response.status_code} - {response.text}")
                    return False
                    
        except ImportError:
            logger.error("requests未安装，请运行: pip install requests")
            return False
        except Exception as e:
            logger.error(f"HTTP上传失败: {e}")
            return False
    
    def send_file(self, local_file, method='scp'):
        """
        发送文件到远程主机
        
        Args:
            local_file: 本地文件路径
            method: 传输方式 ('scp', 'rsync', 'sftp', 'http')
        
        Returns:
            bool: 是否成功
        """
        if not os.path.exists(local_file):
            logger.error(f"文件不存在: {local_file}")
            return False
        
        if method == 'scp':
            return self.send_via_scp(local_file)
        elif method == 'rsync':
            return self.send_via_rsync(local_file)
        elif method == 'sftp':
            return self.send_via_sftp(local_file)
        elif method == 'http':
            return self.send_via_http(local_file)
        else:
            logger.error(f"不支持的传输方式: {method}")
            return False
    
    def send_directory(self, local_dir, method='rsync'):
        """
        发送整个目录
        
        Args:
            local_dir: 本地目录路径
            method: 传输方式
        """
        if method == 'rsync':
            return self.send_via_rsync(local_dir + '/')
        else:
            # 逐个发送文件
            success_count = 0
            for file in Path(local_dir).glob('*'):
                if file.is_file():
                    if self.send_file(str(file), method):
                        success_count += 1
            
            logger.info(f"成功发送 {success_count} 个文件")
            return success_count > 0


def main():
    """测试文件传输"""
    logging.basicConfig(level=logging.INFO)
    
    transfer = FileTransfer()
    
    # 测试发送最新的截图
    screenshots_dir = Path('screenshots')
    if screenshots_dir.exists():
        files = sorted(screenshots_dir.glob('*.png'), key=os.path.getmtime, reverse=True)
        if files:
            latest_file = files[0]
            print(f"发送最新截图: {latest_file}")
            transfer.send_file(str(latest_file))
        else:
            print("没有找到截图文件")
    else:
        print("screenshots目录不存在")


if __name__ == '__main__':
    main()
