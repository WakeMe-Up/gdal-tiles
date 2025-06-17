FROM osgeo/gdal:alpine-small-3.6.3

# 安装 Python 和 pip
RUN apk add --no-cache python3 py3-pip

# 安装依赖
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt

# 拷贝主文件
COPY main.py /app/

CMD ["python3", "main.py"]