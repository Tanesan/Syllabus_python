from define import act
import os
a = [92]
if os.path.isfile("docs/" + str(a[0]) + '.json'):
    os.remove("docs/" + str(a[0]) + '.json')
for i in a:
    act(i, 0, 500)
