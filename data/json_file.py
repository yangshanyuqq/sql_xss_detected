import json
import os


# 读json文件
def get_json(file_name, level="low"):
    path = ""
    file_name = os.path.join(path, file_name)
    with open(file_name,'r') as load_f:
        load_dict = json.load(load_f)
    return load_dict[level]

# 写json文件
def write_json(file_name, dict_data):
    with open(file_name,"w") as f:
        json.dump(dict_data,f,indent=1)
        return True

