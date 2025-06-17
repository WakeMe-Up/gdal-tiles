import os
import oss2
import subprocess

# 读取环境变量
OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT')        # eg: https://oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET = os.environ.get('OSS_BUCKET_NAME')       # eg: my-bucket
OSS_ACCESS_KEY = os.environ.get('ACCESS_KEY_ID')
OSS_SECRET_KEY = os.environ.get('ACCESS_KEY_SECRET')

def handler(event, context):
    print("事件内容：", event)

    # 阿里云事件中包含对象 key，通常格式是 JSON
    import json
    evt = json.loads(event)
    oss_info = evt['events'][0]['oss']
    object_key = oss_info['object']['key']   # 上传的 OSS 文件路径，例如 upload/sample.tif

    file_name = object_key.split("/")[-1]
    local_tif_path = f"/tmp/{file_name}"
    local_tile_dir = "/tmp/tiles"

    # 初始化 OSS 客户端
    auth = oss2.Auth(OSS_ACCESS_KEY, OSS_SECRET_KEY)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET)

    # 下载 TIF 文件
    bucket.get_object_to_file(object_key, local_tif_path)
    print("文件下载完成:", local_tif_path)

    # 创建输出目录
    os.makedirs(local_tile_dir, exist_ok=True)

    # 切片
    subprocess.run([
        "gdal2tiles.py", "-z", "0-5", local_tif_path, local_tile_dir
    ], check=True)

    print("切片完成，开始上传")

    # 递归上传切片目录
    for root, dirs, files in os.walk(local_tile_dir):
        for file in files:
            local_file = os.path.join(root, file)
            oss_key = os.path.relpath(local_file, local_tile_dir)
            oss_key = f"tiles/{file_name.replace('.tif', '')}/{oss_key}"  # 可自定义路径
            bucket.put_object_from_file(oss_key, local_file)

    print("切片上传完成！")
