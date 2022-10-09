import json
json_open_all = open("docs/all.json", 'r')
json_load_all = json.load(json_open_all)

result = []
for key, val in json_load_all.items():
    subject = dict()
    val["id"] = key
    subject = val
    result.append(subject)

with open("docs/fuse.json", 'w') as f:
    json.dump({"data": result}, f, ensure_ascii=False)