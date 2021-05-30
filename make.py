import os

index = 11
for i in range(45):
    print("""      - name: Run main.py # Pythonファイルの実行
        run: |
          python main""" + str(index) + """.py""")
    index += 1
