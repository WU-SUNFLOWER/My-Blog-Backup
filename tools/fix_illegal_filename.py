import os
import argparse

def fix_illegal_filename(directory):
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory, topdown=False):
        # 处理文件夹
        for name in dirs:
            new_name = name.replace(' ', '-')
            if new_name != name:
                old_dir = os.path.join(root, name)
                new_dir = os.path.join(root, new_name)
                os.rename(old_dir, new_dir)
                print(f"Renamed folder: {old_dir} -> {new_dir}")
        
        # 处理文件
        for name in files:
            new_name = name.replace(' ', '-')
            if new_name != name:
                old_file = os.path.join(root, name)
                new_file = os.path.join(root, new_name)
                os.rename(old_file, new_file)
                print(f"Renamed file: {old_file} -> {new_file}")

def main():
    parser = argparse.ArgumentParser(description="Fix illegal filenames by replacing spaces with dashes.")
    parser.add_argument('-d', '--directory', type=str, required=True, help="Directory to start fixing filenames")
    args = parser.parse_args()

    # 运行修复文件名的函数
    fix_illegal_filename(args.directory)

if __name__ == '__main__':
    main()