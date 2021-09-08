import json
from time import sleep
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
# import firebase_admin
# from firebase_admin import credentials
# import pandas as pandas
# from firebase_admin import db

searchingADEn = {}
searchingADJa = {}

# cred = credentials.Certificate("univ-syllabus-firebase-adminsdk-nfe0l-f0a68c4baa.json")
# # firebase_admin.initialize_app(cred)
#
# # Initialize the app with a service account, granting admin privileges
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://univ-syllabus-default-rtdb.firebaseio.com/'
# })



def act(m, a, b):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    #driver = webdriver.Chrome(executable_path='/Users/keitotanemura/Downloads/chromedriver2', options=options)
    # print("A")

    # for m in [21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    #           52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91,
    #           92, 93, 94, 95, 96, 97, 98]:
    #     data = {}

    data = {}

    for i in range(a, b):
        subject = {}
        fin = 0
        driver.get('https://syllabus.kwansei.ac.jp/uniasv2/UnSSOLoginControlFree')
        select_element = driver.find_element(By.ID, 'selLsnMngPostCd')
        select_object = Select(select_element)
        select_object.select_by_index(1)
        select_object.select_by_value(str(m))
        # driver.implicitly_wait(2)
        driver.find_element_by_name('ESearch').click()
        for a in range(int(i / 100)):
            if len(driver.find_elements_by_name('ENext')) == 0:
                if fin == 1:
                    break
                fin = 1
            else:
                driver.find_element_by_name('ENext').click()
        if len(driver.find_elements_by_name('ERefer')) != 0:
            if int(driver.find_element_by_name('lstSlbinftJ016RList_st[' + str(len(driver.find_elements_by_name('ERefer')) - 1) +'].lblNo').get_attribute('value')) <= i:
                break
        else:
            sleep(0.1)
        if len(driver.find_elements_by_name('ERefer')) == 0:
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

        if len(driver.find_elements_by_name('lblVolCd2')) != 0:
            subject.setdefault('授業形態', driver.find_element_by_name('lblVolCd2').get_attribute('value'))
        if len(driver.find_elements_by_name('lblVolCd3')) != 0:
            subject.setdefault('緊急授業形態', driver.find_element_by_name('lblVolCd3').get_attribute('value'))
        if len(driver.find_elements_by_name('lblVolCd4')) != 0:
            subject.setdefault('オンライン授業形態', driver.find_element_by_name('lblVolCd4').get_attribute('value'))

        # list
        topic = {}
        for x in range(40):
            if len(driver.find_elements_by_name('lblVolItm' + str(x + 6))) > 0:
                topic.setdefault('第' + str(x + 1) + '回',
                                 [driver.find_element_by_name('lblVolItm' + str(x + 6)).get_attribute('value'),
                                  driver.find_element_by_name('lblVolItm' + str(46 + x)).get_attribute('value')])
            elif len(driver.find_elements_by_name('lblVolItm38')) > 0:
                topic.setdefault('授業計画1', driver.find_element_by_name('lblVolItm38').get_attribute('value'))
                break
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
                    if driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('th') is None\
                            or len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('th')) == 0:
                        i = 0
                    # print(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                    #     'tbody').find_elements_by_tag_name('tr')[i].find_elements_by_tag_name('th')[0].text)
                    grading.setdefault(
                        ((driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[i].find_elements_by_tag_name('th')[
                              0].text) + str(x)).replace("\n", ""),
                        driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('td')[
                            0].text)
                else:
                    num = []
                    for y in range(len(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name('td'))):
                        num.append(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[x].find_elements_by_tag_name(
                            'td')[y].text)
                    grading.setdefault(
                        (driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                            'tbody').find_elements_by_tag_name('tr')[0].find_elements_by_tag_name('th')[
                             0].text + str(
                            x)).replace("\n", ""),
                        num)
        # 教室情報
        # school_leassons = {}
        # school_leassons.setdefault('項番',
        #                            driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblNo').get_attribute(
        #                                'value'))
        # school_leassons.setdefault('履修年度',
        #                            driver.find_element_by_name(
        #                                'lstSlbtchinftJ002List_st[0].lblTacFcy').get_attribute(
        #                                'value'))
        # school_leassons.setdefault('開講期', driver.find_element_by_name(
        #     'lstSlbtchinftJ002List_st[0].lblAc201ScrDispNm_02').get_attribute('value'))
        # school_leassons.setdefault('曜時',
        #                            driver.find_element_by_name(
        #                                'lstSlbtchinftJ002List_st[0].lblTmtxCd').get_attribute(
        #                                'value'))
        # school_leassons.setdefault('使用開講期', driver.find_element_by_name(
        #     'lstSlbtchinftJ002List_st[0].lblAc201ScrDispNm_03').get_attribute('value'))
        # if len(driver.find_elements_by_name('lblVolCd2')) != 0:
        #     school_leassons.setdefault('授業形態', driver.find_element_by_name('lblVolCd2').get_attribute('value'))
        # if len(driver.find_elements_by_name('lblVolCd3')) != 0:
        #     school_leassons.setdefault('緊急授業形態', driver.find_element_by_name('lblVolCd3').get_attribute('value'))
        # if len(driver.find_elements_by_name('lblVolCd4')) != 0:
        #     school_leassons.setdefault('オンライン授業形態', driver.find_element_by_name('lblVolCd4').get_attribute('value'))

        othersJa = {}
        risyuuki = driver.find_element_by_name('lblAc201ScrDispNm_01').get_attribute('value')
        othersJa.setdefault('履修期', risyuuki[0: risyuuki.find('／')])
        if len(driver.find_elements_by_name('lblVolCd1')) != 0:
            language = driver.find_element_by_name('lblVolCd1').get_attribute('value')
            othersJa.setdefault('主な教授言語', language[0: language.find('／')])
        othersJa.setdefault('授業目的', driver.find_element_by_name('lblVolItm2').get_attribute('value'))
        othersJa.setdefault('到達目標', driver.find_element_by_name('lblVolItm3').get_attribute('value'))
        othersJa.setdefault('授業方法', driver.find_element_by_name('lblVolItm43').get_attribute('value'))
        othersJa.setdefault('トピック', topic)
        othersJa.setdefault('評価', grading)
        i = 1
        while "項番No." + str(i) in grading:
            subject.setdefault('時限' + str(i), grading["項番No." + str(i)][2])
            i += 1
        subject.setdefault('開講期', grading["項番No.1"][1])
        data.setdefault(name, subject)
        searchingADJa = {**othersJa, **subject}
        with open('docs/all/' + str(name) + '.json', 'w') as f:
            json.dump(searchingADJa, f, ensure_ascii=False)
        sleep(1)
        data_all = {}
        data_all.update(data)
        json_open_all = open("docs/all.json", 'r')
        # if name not in list(json_open_all.keys()):
        #     db.reference('rate').set({
        #         name: {
        #             'average': '0',
        #             'review': '',
        #             'people': '0',
        #             'userid': ''
        #         }
        #     })
        json_load_all = json.load(json_open_all)
        json_load_all.update(data_all)
        with open("docs/all.json", 'w') as f:
            json.dump(json_load_all, f, ensure_ascii=False)
        id_json_list = open("docs/id.json", 'r')
        id_json_list = json.load(id_json_list)
        id_json_list.update({name: 0})
        with open("docs/id.json", 'w') as f:
            json.dump(id_json_list, f, ensure_ascii=False)
    # if os.path.isfile("docs/" + str(m) + '.json') and os.stat("docs/" + str(m) + '.json').st_size > 0:
    #     json_open = open("docs/" + str(m) + '.json', 'r')
    #     json_load = json.load(json_open)
    #     data.update(json_load)
    driver.quit()
    return