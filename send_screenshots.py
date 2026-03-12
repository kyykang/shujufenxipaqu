#!/usr/bin/env python3
"""
独立的截图发送脚本
可以单独运行，将screenshots目录中的文件发送到远程主机
"""
import os
import sys
import logging
from pathlib import Path
from file_transfer import FileTransfer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_latest_screenshot():
    """发送最新的截图"""
    transfer = FileTransfer()
    
    if not transfer.remote_host:
        logger.error("未配置远程主机，请检查.env文件")
        return False
    
    screenshots_dir = Path('screenshots')
    if not screenshots_dir.exists():
        logger.error("screenshots目录不存在")
        return False
    
    # 获取最新的截图
    files = sorted(screenshots_dir.glob('*.png'), key=os.path.getmtime, reverse=True)
    
    if not files:
        logger.error("没有找到截图文件")
        return False
    
    latest_file = files[0]
    logger.info(f"发送最新截图: {latest_file}")
    
    method = os.getenv('TRANSFER_METHOD', 'scp')
    return transfer.send_file(str(latest_file), method=method)


def send_all_screenshots():
    """发送所有截图"""
    transfer = FileTransfer()
    
    if not transfer.remote_host:
        logger.error("未配置远程主机，请检查.env文件")
        return False
    
    screenshots_dir = Path('screenshots')
    if not screenshots_dir.exists():
        logger.error("screenshots目录不存在")
        return False
    
    files = list(screenshots_dir.glob('*.png'))
    
    if not files:
        logger.error("没有找到截图文件")
        return False
    
    logger.info(f"准备发送 {len(files)} 个截图文件")
    
    method = os.getenv('TRANSFER_METHOD', 'scp')
    success_count = 0
    
    for file in files:
        logger.info(f"发送: {file.name}")
        if transfer.send_file(str(file), method=method):
            success_count += 1
    
    logger.info(f"成功发送 {success_count}/{len(files)} 个文件")
    return success_count > 0


def send_directory():
    """使用rsync发送整个目录（最高效）"""
    transfer = FileTransfer()
    
    if not transfer.remote_host:
        logger.error("未配置远程主机，请检查.env文件")
        return False
    
    screenshots_dir = Path('screenshots')
    if not screenshots_dir.exists():
        logger.error("screenshots目录不存在")
        return False
    
    logger.info("使用rsync发送整个screenshots目录")
    return transfer.send_directory(str(screenshots_dir), method='rsync')


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 send_screenshots.py latest    # 发送最新的截图")
        print("  python3 send_screenshots.py all        # 发送所有截图")
        print("  python3 send_screenshots.py dir        # 使用rsync发送整个目录")
        print("  python3 send_screenshots.py <file>     # 发送指定文件")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'latest':
        success = send_latest_screenshot()
    elif command == 'all':
        success = send_all_screenshots()
    elif command == 'dir':
        success = send_directory()
    else:
        # 发送指定文件
        if os.path.exists(command):
            transfer = FileTransfer()
            method = os.getenv('TRANSFER_METHOD', 'scp')
            success = transfer.send_file(command, method=method)
        else:
            logger.error(f"文件不存在: {command}")
            success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
