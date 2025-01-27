import os
import argparse

from meta_json_manager import *
from meta_json_fields import *

def process_markdown_file(md_file_path, directory):
    md_title = read_from_meta_json(md_file_path, META_TITLE_FIELD)
    relative_md_path = "blogs" + md_file_path.replace(directory, "").replace("\\", "/")
    result = f"[{md_title}]({relative_md_path})\n\n"
    return result

def generate_catalogue(directory):
    if not os.path.isdir(directory):
        print(f"Error: Directory {directory} does not exist.")
        return False
    
    catalogue = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_file = os.path.join(root, file)
                catalogue.append(process_markdown_file(md_file, directory))
    
    catalogue.sort()
    return "".join(catalogue)

def generate_readme_text(catalogue):
    text = f"""\
# My-Blog-Backup
这是我的技术博客备份，其中仅包括了从我的博客中**精选的部分文章**。
欢迎访问我的掘金主页，直接阅读我的全部博客：https://juejin.cn/user/3544481220008744/posts

## 目录
{catalogue}
"""
    return text

def main():
    # 配置命令行参数解析
    parser = argparse.ArgumentParser(description='README生成工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', help='需要扫描的目录路径')

    args = parser.parse_args()
    if not args.directory:
        raise Exception("Illegal")
    
    output_file_path = os.path.normpath(os.path.join(args.directory, "..", "README.md"))
    
    catalogue_text = generate_catalogue(args.directory)
    readme_text = generate_readme_text(catalogue_text)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(readme_text)

if __name__ == "__main__":
    main()