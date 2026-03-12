# 使用Playwright官方镜像（已包含浏览器）
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 设置工作目录
WORKDIR /app

# 安装中文字体
RUN apt-get update && apt-get install -y \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p screenshots output && chmod 755 screenshots output

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 运行脚本
CMD ["python3", "click_dashboard_final.py"]
