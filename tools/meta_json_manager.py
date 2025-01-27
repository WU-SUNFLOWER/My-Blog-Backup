import os
import json
from pathlib import Path

from meta_json_fields import *

def create_empty_meta_dict(md_file_path):
    meta_dict = dict()

    filename_without_extension = Path(md_file_path).stem
    meta_dict[META_TITLE_FIELD] = filename_without_extension

    return meta_dict

def create_empty_meta_json(md_file_path):
    meta_dict = create_empty_meta_dict(md_file_path)
    meta_file_path = get_meta_json_path(md_file_path)

    with open(meta_file_path, 'w', encoding='utf-8') as file:
        json.dump(meta_dict, file, ensure_ascii=False, indent=4)

    return meta_dict

def get_meta_json_path(md_file_path):
    dirname = os.path.dirname(md_file_path)
    return os.path.join(dirname, META_JSON_FILENAME)

def meta_json_exists(md_file_path):
    return os.path.exists(get_meta_json_path(md_file_path))

def load_entire_meta_json(md_file_path):
    meta_file_path = get_meta_json_path(md_file_path)

    if not os.path.exists(meta_file_path):
        raise Exception("Can't find {meta_file_path}")
    
    with open(meta_file_path, 'r', encoding='utf-8') as file:
        meta_dict = json.load(file)

    return meta_dict

def read_from_meta_json(md_file_path, key, can_create_json = True):
    meta_dict = None
    meta_file_path = get_meta_json_path(md_file_path)

    if os.path.exists(meta_file_path):
        meta_dict = load_entire_meta_json(md_file_path)
    elif can_create_json:
        meta_dict = create_empty_meta_json(md_file_path);
    else:
        raise Exception("Can't find {filename}")
    
    return meta_dict.get(key, None)

def write_to_meta_json(md_file_path, key, value, can_create_json = True):
    meta_dict = None
    meta_file_path = get_meta_json_path(md_file_path);

    if os.path.exists(meta_file_path):
        meta_dict = load_entire_meta_json(md_file_path)
    elif can_create_json:
        meta_dict = create_empty_meta_json(md_file_path);
    else:
        raise Exception("Can't find {filename}")

    meta_dict[key] = value

    with open(meta_file_path, 'w', encoding='utf-8') as file:
        json.dump(meta_dict, file, ensure_ascii=False, indent=4)

