

my_dict = open("docs/all.json", 'r')
seen = []
result = dict()
for key, val in my_dict.items():
    if val not in seen:
        seen.append(val)
        result[key] = val

print(f'Dict after removal: {result}')