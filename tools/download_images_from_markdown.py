import re
import os
import sys
import hashlib
import requests

def download_and_replace_image_links(md_file_path, cookie_dict):
    save_folder_suffix = "image"
    save_folder = os.path.join(os.path.dirname(md_file_path), save_folder_suffix)
    print(save_folder)

    # 确保保存图片的文件夹存在
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 读取.md文件
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 正则表达式匹配Markdown中的图片链接
    pattern = r'!\[.*?\]\((https?://.*?\.(awebp|webp|jpg|png|gif)\?.*?)\)'
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

            print(f"Successfully download {url}")
        except requests.RequestException as e:
            print(f"Failed to download {url}: {e}")

    # 将更新后的内容写回.md文件
    with open(md_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def convert_cookie_to_dict(cookies):
    result = dict()
    for record in cookies.split('; '):
        key, value = record.split('=')
        result[key] = value
    return result

# 此处替换成正常访问图片URL可能需要的cookie字符串
cookie_dict = convert_cookie_to_dict("sid_guard=a2889cf48eba4adca0658f0683dcd8e8%7C1722182808%7C31536000%7CMon%2C+28-Jul-2025+16%3A06%3A48+GMT; uid_tt=21537489a3b39e8fb98b96686deecd0e; uid_tt_ss=21537489a3b39e8fb98b96686deecd0e; sid_tt=a2889cf48eba4adca0658f0683dcd8e8; sessionid=a2889cf48eba4adca0658f0683dcd8e8; sessionid_ss=a2889cf48eba4adca0658f0683dcd8e8; sid_ucp_v1=1.0.0-KDgzZDAwZmZlNjk1YWRjZmQ3ZTA3NDlkYzc4NzIxOWVmYmM4YzNiMGMKFwiotqDA_fWlBhCY2Zm1BhiwFDgCQO8HGgJsZiIgYTI4ODljZjQ4ZWJhNGFkY2EwNjU4ZjA2ODNkY2Q4ZTg; ssid_ucp_v1=1.0.0-KDgzZDAwZmZlNjk1YWRjZmQ3ZTA3NDlkYzc4NzIxOWVmYmM4YzNiMGMKFwiotqDA_fWlBhCY2Zm1BhiwFDgCQO8HGgJsZiIgYTI4ODljZjQ4ZWJhNGFkY2EwNjU4ZjA2ODNkY2Q4ZTg; store-region=cn-zj; store-region-src=uid; __tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227401029162754000395%2522%252C%2522user_unique_id%2522%253A%25227401029162754000395%2522%252C%2522timestamp%2522%253A1723186404834%257D; _tea_utm_cache_2608={%22utm_source%22:%22web_profile%22}; _tea_utm_cache_2018={%22utm_source%22:%22web_profile%22}");

if __name__ == "__main__":
    args = sys.argv
    if len(args) <= 1:
        print("You must offer the path of your markdown file");

    download_and_replace_image_links(args[1], cookie_dict)

