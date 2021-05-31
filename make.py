import os

index = 0

for i in [21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 37, 38,
          39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
          52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91,
          92, 93, 94, 95, 96, 97, 98]:
# for i in range(59):
    path = 'main' + str(index) + '.py'
    f = open(path, 'w')
    f.write("""from define import act
a = [""" + str(i) + """]
for i in a:
    act(i, 0, 700)
    print("A")
""")  # 何も書き込まなくてファイルは作成されました
    f.close()

    path = 'mainb' + str(index) + '.py'
    f = open(path, 'w')
    f.write("""from define import act
a = [""" + str(i) + """]
for i in a:
    act(i, 700, 1400)
    print("A")
 """)  # 何も書き込まなくてファイルは作成されました
    f.close()



#     print("""
#
# builded"""+str(i)+""":
#     runs-on: ubuntu-latest
#     needs: buildedb"""+str(i - 1)+"""
#     steps:
#       - uses: actions/checkout@v2
#         with:
#           token: ${{ secrets.YOUR_SELF_MADE_TOKEN }}
#       - name: Setup python # ワークフローのセクションごとに設定する名前。特に設定する必要はないが、どこでエラーが起きているかを把握する為にも設定しておいた方が良い。
#         uses: actions/setup-python@v2 # Pythonのセットアップ
#         with:
#           python-version: "3.x" # Pythonのバージョン指定
#
#       - name: Install dependencies # Pythonの依存環境のインストール
#         run: | #このような書き方で複数行を一気に実行することができる。
#             python -m pip install --upgrade pip
#             pip install Flask
#             pip install chromedriver-binary
#             pip install selenium
#
#       - name: Run main.py # Pythonファイルの実行
#         run: |
#           python main""" + str(index) + """.py
#
#       - name: git setting
#         run: |
#           git config --local user.email "keito.12.10@icloud.com"
#           git config --local user.name "Tanesan"
#
#       - name: Commit and Push # 実行した結果をプッシュして変更をレポジトリに反映
#         run: |
#           git add .
#           git commit -m "Commit Message" -a
#           git config pull.rebase false
#           git pull
#           git push origin main
#           """)
#
#     print("""
#
# buildedb"""+str(i)+""":
#     runs-on: ubuntu-latest
#     needs: buildeda"""+str(i)+"""
#     steps:
#       - uses: actions/checkout@v2
#         with:
#           token: ${{ secrets.YOUR_SELF_MADE_TOKEN }}
#       - name: Setup python # ワークフローのセクションごとに設定する名前。特に設定する必要はないが、どこでエラーが起きているかを把握する為にも設定しておいた方が良い。
#         uses: actions/setup-python@v2 # Pythonのセットアップ
#         with:
#           python-version: "3.x" # Pythonのバージョン指定
#
#       - name: Install dependencies # Pythonの依存環境のインストール
#         run: | #このような書き方で複数行を一気に実行することができる。
#             python -m pip install --upgrade pip
#             pip install Flask
#             pip install chromedriver-binary
#             pip install selenium
#
#       - name: Run main.py # Pythonファイルの実行
#         run: |
#           python mainb""" + str(index) + """.py
#
#       - name: git setting
#         run: |
#           git config --local user.email "keito.12.10@icloud.com"
#           git config --local user.name "Tanesan"
#
#       - name: Commit and Push # 実行した結果をプッシュして変更をレポジトリに反映
#         run: |
#           git add .
#           git commit -m "Commit Message" -a
#           git config pull.rebase false
#           git pull
#           git push origin main
#           """)

    index += 1
