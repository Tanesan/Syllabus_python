import os

index = 0
for i in range(59):
    # print("builded" + str(i) +",")
    print("""

builded"""+str(i)+""":
    runs-on: ubuntu-latest
    needs: builded"""+str(i - 1)+"""
    steps:
      - uses: actions/checkout@v2
        with:
          token: ${{ secrets.YOUR_SELF_MADE_TOKEN }}
      - name: Setup python # ワークフローのセクションごとに設定する名前。特に設定する必要はないが、どこでエラーが起きているかを把握する為にも設定しておいた方が良い。
        uses: actions/setup-python@v2 # Pythonのセットアップ
        with:
          python-version: "3.x" # Pythonのバージョン指定

      - name: Install dependencies # Pythonの依存環境のインストール
        run: | #このような書き方で複数行を一気に実行することができる。
            python -m pip install --upgrade pip
            pip install Flask
            pip install chromedriver-binary
            pip install selenium

      - name: Run main.py # Pythonファイルの実行
        run: |
          python main""" + str(index) + """.py
          
      - name: git setting
        run: |
          git config --local user.email "keito.12.10@icloud.com"
          git config --local user.name "Tanesan"

      - name: Commit and Push # 実行した結果をプッシュして変更をレポジトリに反映
        run: |
          git add .
          git commit -m "Commit Message" -a
          git config pull.rebase false
          git pull
          git push origin main          
          """)
    index += 1
