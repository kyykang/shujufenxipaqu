#!/bin/bash
# Linux服务器一键部署脚本

set -e  # 遇到错误立即退出

echo "==================================="
echo "OA数据抓取工具 - Linux部署脚本"
echo "==================================="
echo ""

# 检查Python版本
echo "1. 检查Python版本..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Python版本: $PYTHON_VERSION"

# 安装Python依赖
echo ""
echo "2. 安装Python依赖..."
pip3 install -r requirements.txt --user

# 安装Playwright浏览器
echo ""
echo "3. 安装Playwright浏览器..."
python3 -m playwright install chromium

# 安装系统依赖
echo ""
echo "4. 安装系统依赖..."
echo "   需要sudo权限来安装系统依赖"
if command -v sudo &> /dev/null; then
    sudo python3 -m playwright install-deps chromium
else
    echo "   警告: 未找到sudo命令，请手动运行: python3 -m playwright install-deps chromium"
fi

# 创建必要的目录
echo ""
echo "5. 创建目录..."
mkdir -p screenshots
mkdir -p output
chmod 755 screenshots output

# 检查配置文件
echo ""
echo "6. 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "   警告: 未找到.env文件"
    if [ -f ".env.example" ]; then
        echo "   正在从.env.example创建.env..."
        cp .env.example .env
        echo "   请编辑.env文件，填入正确的账号密码"
    else
        echo "   错误: 未找到.env.example文件"
        exit 1
    fi
else
    echo "   .env文件已存在"
fi

# 设置文件权限
echo ""
echo "7. 设置文件权限..."
chmod 600 .env
chmod +x click_dashboard_final.py

# 测试运行
echo ""
echo "8. 测试运行..."
echo "   即将运行测试，按Ctrl+C取消"
sleep 2

python3 click_dashboard_final.py

# 检查结果
echo ""
echo "==================================="
echo "部署完成！"
echo "==================================="
echo ""
echo "截图保存在: $(pwd)/screenshots/"
echo "日志文件: $(pwd)/oa_scraper.log"
echo ""
echo "查看截图: ls -lh screenshots/"
echo "查看日志: tail -f oa_scraper.log"
echo ""
echo "设置定时任务:"
echo "  crontab -e"
echo "  添加: 0 9 * * * cd $(pwd) && python3 click_dashboard_final.py"
echo ""
