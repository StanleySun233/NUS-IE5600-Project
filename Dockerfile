# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim
LABEL authors="sjsun"

# 设置工作目录为 /app
WORKDIR /app

# 复制当前目录下的 requirements.txt 到容器的 /app 目录
COPY requirements.txt /app/

# 安装 requirements.txt 中列出的 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录的所有文件到容器的 /app 目录
COPY . /app

# 暴露 Flask 应用程序的默认端口 5000
EXPOSE 5000

# 运行 Flask 应用程序，假设 app.py 是应用的入口
CMD ["python", "app.py"]
