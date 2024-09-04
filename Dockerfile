# 选择基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 设置PYTHONPATH环境变量
ENV PYTHONPATH=/app

# 复制Python依赖文件并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . /app


# 暴露端口
EXPOSE 9000


# 运行应用
CMD ["python", "api_router/api_router.py", "--host", "0.0.0.0", "--port", "9000"]
