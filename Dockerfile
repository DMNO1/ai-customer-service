# 使用Python 3.10官方镜像作为基础
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如果需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "backend/app.py"]