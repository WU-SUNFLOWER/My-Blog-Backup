import re
import os
import argparse
import hashlib
import requests

from meta_json_manager import *
from meta_json_fields import *

cookie_str = "sid_guard=a2889cf48eba4adca0658f0683dcd8e8%7C1722182808%7C31536000%7CMon%2C+28-Jul-2025+16%3A06%3A48+GMT; uid_tt=21537489a3b39e8fb98b96686deecd0e; uid_tt_ss=21537489a3b39e8fb98b96686deecd0e; sid_tt=a2889cf48eba4adca0658f0683dcd8e8; sessionid=a2889cf48eba4adca0658f0683dcd8e8; sessionid_ss=a2889cf48eba4adca0658f0683dcd8e8; sid_ucp_v1=1.0.0-KDgzZDAwZmZlNjk1YWRjZmQ3ZTA3NDlkYzc4NzIxOWVmYmM4YzNiMGMKFwiotqDA_fWlBhCY2Zm1BhiwFDgCQO8HGgJsZiIgYTI4ODljZjQ4ZWJhNGFkY2EwNjU4ZjA2ODNkY2Q4ZTg; ssid_ucp_v1=1.0.0-KDgzZDAwZmZlNjk1YWRjZmQ3ZTA3NDlkYzc4NzIxOWVmYmM4YzNiMGMKFwiotqDA_fWlBhCY2Zm1BhiwFDgCQO8HGgJsZiIgYTI4ODljZjQ4ZWJhNGFkY2EwNjU4ZjA2ODNkY2Q4ZTg; store-region=cn-zj; store-region-src=uid; __tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227401029162754000395%2522%252C%2522user_unique_id%2522%253A%25227401029162754000395%2522%252C%2522timestamp%2522%253A1723186404834%257D; _tea_utm_cache_2608={%22utm_source%22:%22web_profile%22}; _tea_utm_cache_2018={%22utm_source%22:%22web_profile%22}";

def download_and_replace_image_links(md_file_path, cookie_dict):
    save_folder_suffix = "image"
    save_folder = os.path.join(os.path.dirname(md_file_path), save_folder_suffix)

    # 确保保存图片的文件夹存在
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 读取.md文件
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 正则表达式匹配Markdown中的图片链接
    pattern = r'!\[.*?\]\((https?://.*?\.(image#|awebp|webp|jpg|png|gif)\?.*?)\)'
    matches = re.findall(pattern, content)

    # 下载并保存图片，更新Markdown文件内容
    for match in matches:
        url, file_extension = match
        try:
            response = requests.get(url, cookies=cookie_dict)
            response.raise_for_status()  # 确保请求成功

            # 计算图片的哈希值作为文件名
            file_hash = hashlib.sha256(response.content).hexdigest()
            filename = f'{file_hash}.{file_extension}'
            file_path = os.path.join(save_folder, filename)

            # 保存图片到磁盘
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # 替换Markdown文件中的链接
            content = content.replace(url, f"{save_folder_suffix}/{filename}")

            #print(f"Successfully download {url}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")
            raise e

    # 将更新后的内容写回.md文件
    with open(md_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def convert_cookie_to_dict(cookies):
    result = dict()
    for record in cookies.split('; '):
        key, value = record.split('=')
        result[key] = value
    return result

def process_markdown_file(md_file_path, cookie_dict):
    """处理单个Markdown文件"""
    if not os.path.isfile(md_file_path):
        raise Exception(f"Error: File {md_file_path} does not exist.")
    if not md_file_path.endswith('.md'):
        raise Exception(f"Error: {md_file_path} is not a Markdown file.")
    
    # 检查md文件中的图片链接是否已经被替换过了
    if read_from_meta_json(md_file_path, META_REPLACED_FIELD):
        raise Exception(f"Error: The images of {md_file_path} has been replaced already.")

    # 下载图片并更话md文件中的链接
    try:
        download_and_replace_image_links(md_file_path, cookie_dict)
    except requests.RequestException as e:
        pass
    else:
        # 更新meta.json
        write_to_meta_json(md_file_path, META_REPLACED_FIELD, True)
        print(f"Successfully processed {md_file_path}")

    return True

def process_directory(directory, cookie_dict):
    """递归处理目录中的Markdown文件"""
    if not os.path.isdir(directory):
        print(f"Error: Directory {directory} does not exist.")
        return False
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_file = os.path.join(root, file)
                try:
                    process_markdown_file(md_file, cookie_dict)
                except:
                    pass
    return True

def main():
    cookie_dict = convert_cookie_to_dict(cookie_str)

    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description='Markdown图片下载处理工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', help='需要扫描的目录路径')
    group.add_argument('-f', '--file', help='需要处理的Markdown文件路径')
    
    args = parser.parse_args()
    
    # 根据参数执行对应操作
    if args.directory:
        process_directory(args.directory, cookie_dict)
    elif args.file:
        process_markdown_file(args.file, cookie_dict)

if __name__ == "__main__":
    main()
