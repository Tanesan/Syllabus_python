import json
json_open_all = open("docs/all.json", 'r')
json_load_all = json.load(json_open_all)

seen = []
result = dict()
for key, val in json_load_all.items():
    if val not in seen:
        seen.append(val)
        result[key] = val

with open("docs/all.json", 'w') as f:
    json.dump(result, f, ensure_ascii=False)