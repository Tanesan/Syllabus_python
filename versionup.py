with open('docs/all_version.txt', 'r') as f:
    t = str(int(f.read()) + 1)
    f.close()
with open('docs/all_version.txt', 'w') as f:
    f.write(t)
    f.close()