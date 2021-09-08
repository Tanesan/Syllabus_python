import json


def first():
    id_json_list = open("docs/id.json", 'r')
    id_json_list = json.load(id_json_list)
    id_json_c_list = id_json_list.copy()
    r_all = open("docs/all.json", 'r')
    json_r_all = json.load(r_all)
    json_c_all = json_r_all.copy()
    for key in json_r_all:
        if not key in id_json_c_list:
            del json_c_all[key]
    with open("docs/all.json", 'w') as f:
        json.dump(json_c_all, f, ensure_ascii=False)
    return
first()