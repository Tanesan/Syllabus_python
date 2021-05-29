from time import sleep
from selenium import webdriver
import chromedriver_binary
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from flask import Flask, request, abort, jsonify
import os
# from fastapi import FastAPI

app = Flask(__name__)
# app = FastAPI()
app.config["JSON_AS_ASCII"] = False
data = {}
searchingADJa = {}
searchingADEn = {}


def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # options.add_argument('disable-gpu')
    # options.add_argument('--no-sandbox')
    # options.add_argument("start-maximized")
    # options.add_argument("--single-process")
    # options.add_argument("enable-automation")
    # options.add_argument("--disable-infobars")
    # options.add_argument('--disable-extensions')
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--disable-browser-side-navigation")
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # prefs = {"profile.default_content_setting_values.notifications": 2}
    # options.add_experimental_option("prefs", prefs)
    # driver = webdriver.Chrome(executable_path='/Users/keitotanemura/Downloads/chromedriver', options=options)
    driver = webdriver.Chrome(options=options)
    for m in [21, 22, 23,24, 25, 26, 28, 29, 31, 32, 34, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]:
        for i in range(1):
            subject = {}
            fin = 0
            driver.get('https://syllabus.kwansei.ac.jp/uniasv2/UnSSOLoginControlFree')
            select_element = driver.find_element(By.ID, 'selLsnMngPostCd')
            select_object = Select(select_element)
            select_object.select_by_index(1)
            select_object.select_by_value(str(m))
            driver.find_element_by_name('ESearch').click()
            for a in range(int(i / 100)):
                # if driver.find_element_by_name('ENext').is_enabled():
                driver.find_element_by_name('ENext').click()
            if len(driver.find_elements_by_name('ERefer')) <= i % 100:
                break
            if fin == 1:
                break
            driver.find_elements_by_name('ERefer')[i % 100].click()
            # あとで
            name = driver.find_element_by_name('lblLsnCd').get_attribute('value')
            subject.setdefault('開講キャンパス', driver.find_element_by_name('lblCc019ScrDispNm').get_attribute('value'))
            subject.setdefault('【科目ナンバー/Course Number】授業名称',
                               driver.find_element_by_name('lblRepSbjKnjNm').get_attribute('value'))
            subject.setdefault('管理部署', driver.find_element_by_name('lblAc119ScrDispNm').get_attribute('value'))
            subject.setdefault('単位数', driver.find_element_by_name('lblSbjCrnum').get_attribute('value'))
            subject.setdefault('担当者', driver.find_element_by_name('lstChagTch_st[0].lblTchName').get_attribute('value'))
            subject.setdefault('履修基準年度', driver.find_element_by_name('lblCc004ScrDispNm').get_attribute('value'))
            # list
            topic = {}
            for x in range(40):
                if len(driver.find_elements_by_name('lblVolItm' + str(x + 6))) > 0:
                    topic.setdefault('第' + str(x + 1) + '回',
                                     [driver.find_element_by_name('lblVolItm' + str(x + 6)).get_attribute('value'),
                                      driver.find_element_by_name('lblVolItm' + str(46 + x)).get_attribute('value')])
                else:
                    break
            if len(driver.find_elements_by_name('lblVolItm5')) > 0:
                topic.setdefault('授業外学習2', driver.find_element_by_name('lblVolItm5').get_attribute('value'))
            grading = {}
            for z in range(len(driver.find_elements_by_class_name('output')) - 2):
                # grading
                for x in range(len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                        'tbody').find_elements_by_tag_name('tr'))):
                    if len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('td')) == 1:
                        i = x
                        # print(x, len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')))
                        if len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('th')) == 0:
                            i = 0
                        # print(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                        #     'tbody').find_elements_by_tag_name('tr')[i].find_elements_by_tag_name('th')[0].text)
                        grading.setdefault(((driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[i].find_elements_by_tag_name('th')[0].text)+str(x)).replace("\n", ""),
                                           driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                                               'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('td')[
                                               0].text)
                    else:
                        num = []
                        # print(str(x) +"A")
                        for y in range(len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                                'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('td'))):
                            num.append(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                                'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name(
                                'td')[y].text)
                        grading.setdefault((driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[0].find_elements_by_tag_name('th')[0].text + str(
                            x)).replace("\n", ""),
                                           num)
            # 教室情報
            school_leassons = {}
            school_leassons.setdefault('項番', driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblNo').get_attribute(
                'value'))
            school_leassons.setdefault('履修年度',
                                       driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblTacFcy').get_attribute(
                                           'value'))
            school_leassons.setdefault('開講期', driver.find_element_by_name(
                'lstSlbtchinftJ002List_st[0].lblAc201ScrDispNm_02').get_attribute('value'))
            school_leassons.setdefault('曜時',
                                       driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblTmtxCd').get_attribute(
                                           'value'))
            school_leassons.setdefault('使用開講期', driver.find_element_by_name(
                'lstSlbtchinftJ002List_st[0].lblAc201ScrDispNm_03').get_attribute('value'))
            # school_leassons.setdefault('教室情報',
            #                            driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblClrNm').get_attribute(
            #                                'value'))
            othersJa = {}
            othersEn = {}
            risyuuki = driver.find_element_by_name('lblAc201ScrDispNm_01').get_attribute('value')
            othersJa.setdefault('履修期', risyuuki[0: risyuuki.find('／')])
            othersEn.setdefault('履修期', risyuuki[risyuuki.find('／') + 1:len(risyuuki) + 1])
            language = driver.find_element_by_name('lblVolCd1').get_attribute('value')
            othersJa.setdefault('主な教授言語', language[0: language.find('／')])
            othersEn.setdefault('主な教授言語', language[language.find('／') + 1:len(risyuuki) + 1])
            othersJa.setdefault('授業目的', driver.find_element_by_name('lblVolItm2').get_attribute('value'))
            othersEn.setdefault('授業目的(英文)', driver.find_element_by_name('lblVolItm78').get_attribute('value'))
            othersJa.setdefault('到達目標', driver.find_element_by_name('lblVolItm3').get_attribute('value'))
            othersEn.setdefault('到達目標(英文)', driver.find_element_by_name('lblVolItm79').get_attribute('value'))
            othersJa.setdefault('授業方法', driver.find_element_by_name('lblVolItm43').get_attribute('value'))
            # othersJa.setdefault('教室情報', school_leassons)
            othersJa.setdefault('トピック', topic)
            othersEn.setdefault('トピック', topic)
            othersJa.setdefault('評価', grading)
            i = 1
            while "項番No." + str(i) in grading:
                subject.setdefault('時限'+str(i), grading["項番No." + str(i)][2])
                i += 1
            subject.setdefault('開講期', grading["項番No.1"][1])
            oneset = {}
            oneset.setdefault(name, subject)
            data.setdefault(str(m), oneset)
            searchingADJa.setdefault(name, {**othersJa, **subject})
            searchingADEn.setdefault(name, {**othersEn, **subject})
            # print(searchingADJa)
            sleep(5)
            print(data)
    driver.quit()
    return

# @app.get("/api/subject/<id>")
@app.route("/api/subject/<id>", methods=['GET'])
def callback(id):
    return jsonify(data[id])

# @app.get('/ja/api/<id>')
@app.route('/ja/api/<id>', methods=['GET'])
def check__subject_ja(id):
    # print(searchingADJa)
    return jsonify(searchingADJa[id])

# @app.get('/en/api/<id>')
@app.route('/en/api/<id>', methods=['GET'])
def check__subject_en(id):
    # print(searchingADEn)
    return jsonify(searchingADEn[id])

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')

if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), threaded=True)
