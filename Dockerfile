# 使用官方 Python 3.12 镜像作为基础镜像
FROM python:3.12-slim
LABEL authors="sjsun"
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN python init.py
EXPOSE 5000
CMD ["python", "Program (group 19).py"]
