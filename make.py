

index = 0
#
# for i in [21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 37, 38,
#           39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
#           52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91,
#           92, 93, 94, 95, 96, 97, 98]:
for i in range(16, 59):
#         path = 'main' + str(index) + '.py'
#         f = open(path, 'w')
#         f.write("""from define import act
# 
# a = [""" + str(i) + """]
# if os.path.isfile("docs/" + str(a[0]) + '.json'):
#     os.remove("docs/" + str(a[0]) + '.json')
# for i in a:
#     act(i, 0, 1500)
# """)  # ファイルは作成されました
#         f.close()
#
#
#         path = 'mainb' + str(index) + '.py'
#         f = open(path, 'w')
#         f.write("""from define import act
# a = [""" + str(i) + """]
# for i in a:
#         act(i, 550, 950)
# print("A")
# """)  # 何も書き込まなくてファイルは作成されました
#         f.close()
#
#         path = 'mainc' + str(index) + '.py'
#         f = open(path, 'w')
#         f.write("""from define import act
# a = [""" + str(i) + """]
# for i in a:
#         act(i, 950, 1300)
#         print("A")
# """)  # 何も書き込まなくてファイルは作成されました
#         f.close()

    subjects = [
    "共通教育センター","Center for Common Educational Programs",
    "キャリアセンター","Center for Career Planning and Placement",
    "共通教育センター（情報科学科目）","Center for Common Educational Programs (Information Science Courses)",
    "言語教育研究センター","Language Center",
    "国際教育・協力センター（CIEC　JEASP）","Center for International Education and Cooperation (JEASP)",
    "教職教育研究センター（資格）","Research Center for Teacher Development (for Certifications)",
    "教職教育研究センター（教職専門）","Research Center for Teacher Development (for Special Studies)",
    "国際教育・協力センター/CIEC","Center for International Education and Cooperation",
    "キリスト教と文化研究センター","Research Center for Christianity and Culture",
    "日本語教育センター","Center for Japanese Language Education",
    "ハンズオン・ラーニングセンター","Center for Hands-on Learning Programs",
    "国連・外交統括センター","Integrated Center for UN and Foreign Affairs Studies",
    "神学研究科前期","Graduate School of Theology Master's Course",
    "文学研究科前期","Graduate School of Humanities Master's Course",
    "社会学研究科前期","Graduate School of Sociology Master's Course",
    "法学研究科前期","Graduate School of Law and Politics Master's Course",
    "経済学研究科前期","Graduate School of Economics Master's Course",
    "商学研究科前期","Graduate School of Business Administration Master's Course",
    "理工学研究科前期","Graduate School of Science and Technology Master's Course",
    "総合政策研究科前期","Graduate School of Policy Studies Master's Course",
    "言語コミュニケーション前期","Graduate School of Language, Communication, and Culture Master's Course",
    "人間福祉研究科前期","Graduate School of Human Welfare Studies Master's Course",
    "教育学研究科前期","Graduate School of Education Master's Course",
    "理工学研究科修士","Graduate School of Science and Technology Master's Course",
    "国際学研究科前期","Graduate School of International Studies Master's Course",
    "大学院共通科目・認定科目前期","Graduate School of Master's Course (Certified)",
    "神学研究科後期","Graduate School of Theology Doctoral Course",
    "文学研究科後期","Graduate School of Humanities Doctoral Course",
    "社会学研究科後期","Graduate School of Sociology Doctoral Course",
    "法学研究科後期","Graduate School of Law and Politics Doctoral Course",
    "経済学研究科後期","Graduate School of Economics Doctoral Course",
    "商学研究科後期","Graduate School of Business Administration Doctoral Course",
    "理工学研究科後期","Graduate School of Science and Technology Doctoral Course",
    "総合政策研究科後期","Graduate School of Policy Studies Doctoral Course",
    "言語コミュニケーション後期","Graduate School of Language, Communication, and Culture Doctoral Course",
    "人間福祉研究科後期","Graduate School of Human Welfare Studies Doctoral Course",
    "教育学研究科後期","Graduate School of Education Doctoral Course",
    "経営戦略研究科後期","Graduate School of Institute of Business and Accounting Doctoral Course",
    "国際学研究科後期","Graduate School of International Studies Doctoral Course",
    "大学院共通科目・認定科目後期","Graduate School of Doctoral Course (Certified)",
    "司法研究科","Law School",
    "経営戦略研究科/IBA","Institute of Business and Accounting",
    "使用しない（カリキュラム設定用　非正規　大学院）","free2"]
    print("""

""" + subjects[2*(i -16) +1].replace(" ", "-") + """:
    runs-on: ubuntu-latest
    needs: """ + subjects[2*(i -17) +1].replace(" ", "-") + """
    steps:
      - uses: actions/checkout@v2
        with:
          token: ${{ secrets.YOUR_SELF_MADE_TOKEN }}
      - name: Setup python
        uses: actions/setup-python@v2
        with:
          python-version: "3.x"

      - name: Install dependencies
        run: |
            python -m pip install --upgrade pip
            pip install Flask
            pip install chromedriver-binary
            pip install selenium

      - name: Run main.py
        run: |
          python main""" + str(i) + """.py

      - name: git setting
        run: |
          git config --local user.email "keito.12.10@icloud.com"
          git config --local user.name "Tanesan"

      - name: Commit and Push
        run: |
          git fetch
          git add .
          git commit -m """ + '"' + subjects[2*(i -16)] + '"' + """ && git push
          """)

#     print("""
#
# buildedb""" + str(i) + """:
#     runs-on: ubuntu-latest
#     needs: builded""" + str(i) + """
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
#            git add .
#            git commit -m "Commit Message" &&git push || true
#
# buildedc""" + str(i) + """:
#     runs-on: ubuntu-latest
#     needs: buildedb""" + str(i) + """
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
#           python mainc""" + str(index) + """.py
#
#       - name: git setting
#         run: |
#           git config --local user.email "keito.12.10@icloud.com"
#           git config --local user.name "Tanesan"
#
#       - name: Commit and Push # 実行した結果をプッシュして変更をレポジトリに反映
#         run: |
#           git add .
#           git commit -m "Commit Message" git push || true
#           """)
#     index += 1
