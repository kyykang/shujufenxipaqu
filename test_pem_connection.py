#!/usr/bin/env python3
"""
测试.pem密钥连接
快速验证SSH配置是否正确
"""
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def check_pem_file():
    """检查.pem文件"""
    pem_path = os.getenv('SSH_KEY_PATH')
    
    if not pem_path:
        print("❌ 未配置SSH_KEY_PATH")
        return False
    
    # 展开~
    pem_path = os.path.expanduser(pem_path)
    
    if not os.path.exists(pem_path):
        print(f"❌ 密钥文件不存在: {pem_path}")
        return False
    
    print(f"✓ 密钥文件存在: {pem_path}")
    
    # 检查权限
    stat_info = os.stat(pem_path)
    perms = oct(stat_info.st_mode)[-3:]
    
    if perms not in ['400', '600']:
        print(f"⚠️  密钥权限不正确: {perms}，应该是400或600")
        print(f"   运行: chmod 400 {pem_path}")
        return False
    
    print(f"✓ 密钥权限正确: {perms}")
    return True


def check_config():
    """检查配置"""
    required = ['REMOTE_HOST', 'REMOTE_USER', 'REMOTE_PATH']
    
    for key in required:
        value = os.getenv(key)
        if not value:
            print(f"❌ 未配置{key}")
            return False
        print(f"✓ {key}: {value}")
    
    return True


def test_ssh_connection():
    """测试SSH连接"""
    pem_path = os.path.expanduser(os.getenv('SSH_KEY_PATH'))
    host = os.getenv('REMOTE_HOST')
    user = os.getenv('REMOTE_USER')
    port = os.getenv('REMOTE_PORT', '22')
    
    print(f"\n测试SSH连接: {user}@{host}:{port}")
    
    cmd = [
        'ssh',
        '-i', pem_path,
        '-p', port,
        '-o', 'ConnectTimeout=10',
        '-o', 'StrictHostKeyChecking=no',
        f'{user}@{host}',
        'echo "SSH连接成功"'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✓ SSH连接成功")
            return True
        else:
            print(f"❌ SSH连接失败")
            print(f"错误: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ SSH连接超时")
        return False
    except Exception as e:
        print(f"❌ SSH连接出错: {e}")
        return False


def test_scp():
    """测试SCP传输"""
    pem_path = os.path.expanduser(os.getenv('SSH_KEY_PATH'))
    host = os.getenv('REMOTE_HOST')
    user = os.getenv('REMOTE_USER')
    remote_path = os.getenv('REMOTE_PATH')
    port = os.getenv('REMOTE_PORT', '22')
    
    print(f"\n测试SCP传输...")
    
    # 创建测试文件
    test_file = '/tmp/test_pem_connection.txt'
    with open(test_file, 'w') as f:
        f.write('Test file for PEM connection')
    
    cmd = [
        'scp',
        '-i', pem_path,
        '-P', port,
        '-o', 'StrictHostKeyChecking=no',
        test_file,
        f'{user}@{host}:{remote_path}/'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✓ SCP传输成功")
            
            # 清理远程文件
            cleanup_cmd = [
                'ssh',
                '-i', pem_path,
                '-p', port,
                f'{user}@{host}',
                f'rm -f {remote_path}/test_pem_connection.txt'
            ]
            subprocess.run(cleanup_cmd, capture_output=True)
            
            # 清理本地文件
            os.remove(test_file)
            
            return True
        else:
            print(f"❌ SCP传输失败")
            print(f"错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ SCP传输出错: {e}")
        return False


def test_python_transfer():
    """测试Python文件传输"""
    print(f"\n测试Python文件传输...")
    
    try:
        from file_transfer import FileTransfer
        
        # 创建测试文件
        test_file = '/tmp/test_python_transfer.txt'
        with open(test_file, 'w') as f:
            f.write('Test file for Python transfer')
        
        transfer = FileTransfer()
        method = os.getenv('TRANSFER_METHOD', 'scp')
        
        success = transfer.send_file(test_file, method=method)
        
        # 清理
        os.remove(test_file)
        
        if success:
            print(f"✓ Python {method}传输成功")
            return True
        else:
            print(f"❌ Python {method}传输失败")
            return False
            
    except Exception as e:
        print(f"❌ Python传输出错: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("测试.pem密钥SSH连接")
    print("="*60)
    print()
    
    # 1. 检查.pem文件
    print("1. 检查密钥文件...")
    if not check_pem_file():
        sys.exit(1)
    
    print()
    
    # 2. 检查配置
    print("2. 检查配置...")
    if not check_config():
        sys.exit(1)
    
    print()
    
    # 3. 测试SSH连接
    print("3. 测试SSH连接...")
    if not test_ssh_connection():
        print("\n提示:")
        print("- 检查安全组/防火墙是否开放22端口")
        print("- 检查主机地址是否正确")
        print("- 检查用户名是否正确")
        sys.exit(1)
    
    # 4. 测试SCP传输
    print("\n4. 测试SCP传输...")
    if not test_scp():
        print("\n提示:")
        print("- 检查远程路径是否存在")
        print("- 检查是否有写权限")
        sys.exit(1)
    
    # 5. 测试Python传输
    print("\n5. 测试Python文件传输...")
    if not test_python_transfer():
        sys.exit(1)
    
    print()
    print("="*60)
    print("✓ 所有测试通过！配置正确，可以正常使用")
    print("="*60)
    print()
    print("现在可以运行:")
    print("  python3 click_dashboard_final.py")
    print("  python3 send_screenshots.py latest")


if __name__ == '__main__':
    main()
