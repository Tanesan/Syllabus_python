import json
import os
from time import sleep

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
ad_data = [
    "神学部／School of Theology",
    "文学部／School of Humanities",
    "社会学部／School of Sociology",
    "法学部／School of Law and Politics",
    "経済学部／School of Economics",
    "商学部／School of Business Administration",
    "理工学部／School of Science and Technology",
    "総合政策学部／School of Policy Studies",
    "人間福祉学部／School of Human Welfare Studies",
    "教育学部／School of Education",
    "国際学部/International Studies／School of International Studies",
    "理学部／School of Science",
    "工学部／School of Engineering",
    "生命環境学部／School of Biological and Environmental Sciences",
    "建築学部／School of Architecture",
    "使用しない（カリキュラム設定用　非正規　大学",
    "スポーツ科学・健康科学教育プログラム室／Sports and Health Sciences Program Office",
    "共通教育センター／Center for Common Educational Programs",
    "キャリアセンター／Center for Career Planning and Placement",
    "共通教育センター（情報科学科目）／Center for Common Educational Programs (Information Science Courses)",
    "言語教育研究センター／Language Center",
    "国際教育・協力センター（CIEC　JEASP）／Center for International Education and Cooperation (JEASP)",
    "教職教育研究センター（資格）／Research Center for Teacher Development (for Certifications)",
    "教職教育研究センター（教職専門）／Research Center for Teacher Development (for Special Studies)",
    "国際教育・協力センター/CIEC／Center for International Education and Cooperation",
    "キリスト教と文化研究センター／Research Center for Christianity and Culture",
    "日本語教育センター／Center for Japanese Language Education",
    "ハンズオン・ラーニングセンター／Center for Hands-on Learning Programs",
    "国連・外交統括センター／Integrated Center for UN and Foreign Affairs Studies",
    "神学研究科前期／Graduate School of Theology Master's Course",
    "文学研究科前期／Graduate School of Humanities Master's Course",
    "社会学研究科前期／Graduate School of Sociology Master's Course",
    "法学研究科前期／Graduate School of Law and Politics Master's Course",
    "経済学研究科前期／Graduate School of Economics Master's Course",
    "商学研究科前期／Graduate School of Business Administration Master's Course",
    "理工学研究科前期／Graduate School of Science and Technology Master's Course",
    "総合政策研究科前期／Graduate School of Policy Studies Master's Course",
    "言語コミュニケーション前期／Graduate School of Language, Communication, and Culture Master's Course",
    "人間福祉研究科前期／Graduate School of Human Welfare Studies Master's Course",
    "教育学研究科前期／Graduate School of Education Master's Course",
    "理工学研究科修士／Graduate School of Science and Technology Master's Course",
    "国際学研究科前期／Graduate School of International Studies Master's Course",
    "大学院共通科目・認定科目前期／Graduate School of Master's Course (Certified)",
    "神学研究科後期／Graduate School of Theology Doctoral Course",
    "文学研究科後期／Graduate School of Humanities Doctoral Course",
    "社会学研究科後期／Graduate School of Sociology Doctoral Course",
    "法学研究科後期／Graduate School of Law and Politics Doctoral Course",
    "経済学研究科後期／Graduate School of Economics Doctoral Course",
    "商学研究科後期／Graduate School of Business Administration Doctoral Course",
    "理工学研究科後期／Graduate School of Science and Technology Doctoral Course",
    "総合政策研究科後期／Graduate School of Policy Studies Doctoral Course",
    "言語コミュニケーション後期／Graduate School of Language, Communication, and Culture Doctoral Course",
    "人間福祉研究科後期／Graduate School of Human Welfare Studies Doctoral Course",
    "教育学研究科後期／Graduate School of Education Doctoral Course",
    "経営戦略研究科後期／Graduate School of Institute of Business and Accounting Doctoral Course",
    "国際学研究科後期／Graduate School of International Studies Doctoral Course",
    "大学院共通科目・認定科目後期／Graduate School of Doctoral Course (Certified)",
    "司法研究科／Law School",
    "経営戦略研究科/IBA／Institute of Business and Accounting",
    "使用しない（カリキュラム設定用　非正規　大学院）",
]
study = [
    "対面授業/Face to face format",
    "同時双方向型オンライン授業/Online format: Simultaneous and two-way",
    "オンデマンドＡ型オンライン授業(時間割あり)/On-demand A(with timetable)",
    "オンデマンドＢ型オンライン授業(時間割なし)/On-demand B(w/o timetable)",
    "オンライン受講不可/Online attendance is NOT permitted.",
]
campas_data = [
    "西宮上ケ原キャンパス／Nishinomiya Uegahara Campus",
    "神戸三田キャンパス／Kobe Sanda Campus",
    "大阪梅田キャンパス／Osaka Umeda Campus",
    "西宮市大学交流センター／Nishinomiya City Intercollegiate Center",
    "西宮聖和キャンパス／Nishinomiya Seiwa Campus",
    "オンライン／Online",
    "東京丸の内キャンパス／Tokyo Marunouchi Campus",
    "西宮北口キャンパス／Nishinomiya Kitaguchi Campus",
]
day_data = [
    "月曜１時限／Monday 1",
    "月曜２時限／Monday 2",
    "月曜３時限／Monday 3",
    "月曜４時限／Monday 4",
    "月曜５時限／Monday 5",
    "月曜６時限／Monday 6",
    "月曜７時限／Monday 7",
    "火曜１時限／Tuesday 1",
    "火曜２時限／Tuesday 2",
    "火曜３時限／Tuesday 3",
    "火曜４時限／Tuesday 4",
    "火曜５時限／Tuesday 5",
    "火曜６時限／Tuesday 6",
    "火曜７時限／Tuesday 7",
    "水曜１時限／Wednesday 1",
    "水曜２時限／Wednesday 2",
    "水曜３時限／Wednesday 3",
    "水曜４時限／Wednesday 4",
    "水曜５時限／Wednesday 5",
    "水曜６時限／Wednesday 6",
    "水曜７時限／Wednesday 7",
    "木曜１時限／Thursday 1",
    "木曜２時限／Thursday 2",
    "木曜３時限／Thursday 3",
    "木曜４時限／Thursday 4",
    "木曜５時限／Thursday 5",
    "木曜６時限／Thursday 6",
    "木曜７時限／Thursday 7",
    "金曜１時限／Friday 1",
    "金曜２時限／Friday 2",
    "金曜３時限／Friday 3",
    "金曜４時限／Friday 4",
    "金曜５時限／Friday 5",
    "金曜６時限／Friday 6",
    "金曜７時限／Friday 7",
    "土曜１時限／Saturday 1",
    "土曜２時限／Saturday 2",
    "土曜３時限／Saturday 3",
    "土曜４時限／Saturday 4",
    "土曜５時限／Saturday 5",
    "土曜６時限／Saturday 6",
    "土曜７時限／Saturday 7",
    "日曜１時限／Sunday 1",
    "日曜２時限／Sunday 2",
    "日曜３時限／Sunday 3",
    "日曜４時限／Sunday 4",
    "日曜５時限／Sunday 5",
    "日曜６時限／Sunday 6",
    "‐／-",
    "集中・その他／Concentration/Other",
]
term_data = [
    "通年／Year Round",
    "春学期／Spring",
    "秋学期／Fall",
    "春学期前半／Spring (1st Half)",
    "春学期後半／Spring (2nd Half)",
    "秋学期前半／Fall (1st Half)",
    "秋学期後半／Fall (2nd Half)",
    "通年集中／Intensive (Year Round)",
    "春学期集中／Intensive (Spring)",
    "秋学期集中／Intensive (Fall)",
    "春学期前半集中／Intensive (Spring 1st Half)",
    "春学期後半集中／Intensive (Spring 2nd Half)",
    "秋学期前半集中／Intensive (Fall 1st Half)",
    "秋学期後半集中／Intensive (Fall 2nd Half)",
]
score = [
    "定期試験／Final Examination (01)",
    "定期試験に代わるリポート／Term paper to replace the final examination (02)",
    "授業中試験／In-class examination (03)",
    "平常リポート／Individual reports (04)",
    "その他／Others (99)",
]


def act(m, a, b):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    # print("A")

    # for m in [21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    #           52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91,
    #           92, 93, 94, 95, 96, 97, 98]:
    #     data = {}

    data = {}

    for i in range(a, b):
        subject = {}
        fin = 0
        driver.get("https://syllabus.kwansei.ac.jp/uniasv2/UnSSOLoginControlFree")
        select_element = driver.find_element(By.ID, "selLsnMngPostCd")
        select_object = Select(select_element)
        select_object.select_by_index(1)
        select_object.select_by_value(str(m))
        # driver.implicitly_wait(2)
        # 年度設定
        year_2022 = driver.find_element_by_id("txtLsnOpcFcy")
        year_2022.clear()
        year_2022.send_keys("2022")

        driver.find_element_by_name("ESearch").click()
        for a in range(int(i / 100)):
            if len(driver.find_elements_by_name("ENext")) == 0:
                if fin == 1:
                    break
                fin = 1
            else:
                driver.find_element_by_name("ENext").click()
        if len(driver.find_elements_by_name("ERefer")) != 0:
            if (
                int(
                    driver.find_element_by_name(
                        "lstSlbinftJ016RList_st["
                        + str(len(driver.find_elements_by_name("ERefer")) - 1)
                        + "].lblNo"
                    ).get_attribute("value")
                )
                <= i
            ):
                break
        else:
            sleep(0.1)
        if len(driver.find_elements_by_name("ERefer")) == 0:
            break
        if fin == 1:
            break
        driver.find_elements_by_name("ERefer")[i % 100].click()
        # あとで
        name = driver.find_element_by_name("lblLsnCd").get_attribute("value")
        subject.setdefault(
            "campas",
            campas_data.index(
                driver.find_element_by_name("lblCc019ScrDispNm").get_attribute("value")
            ),
        )
        subject.setdefault(
            "name", driver.find_element_by_name("lblRepSbjKnjNm").get_attribute("value")
        )
        subject.setdefault(
            "管理部署",
            ad_data.index(
                driver.find_element_by_name("lblAc119ScrDispNm").get_attribute("value")
            ),
        )
        subject.setdefault(
            "単位数",
            int(driver.find_element_by_name("lblSbjCrnum").get_attribute("value")),
        )
        subject.setdefault(
            "担当者",
            driver.find_element_by_name("lstChagTch_st[0].lblTchName").get_attribute(
                "value"
            ),
        )
        subject.setdefault(
            "履修基準年度",
            driver.find_element_by_name("lblCc004ScrDispNm").get_attribute("value"),
        )

        if len(driver.find_elements_by_name("lblVolCd2")) != 0:
            subject.setdefault(
                "授業形態",
                study.index(
                    driver.find_element_by_name("lblVolCd2").get_attribute("value")
                ),
            )
        if len(driver.find_elements_by_name("lblVolCd3")) != 0:
            subject.setdefault(
                "緊急授業形態",
                study.index(
                    driver.find_element_by_name("lblVolCd3").get_attribute("value")
                ),
            )
        if len(driver.find_elements_by_name("lblVolCd4")) != 0:
            subject.setdefault(
                "オンライン授業形態",
                study.index(
                    driver.find_element_by_name("lblVolCd4").get_attribute("value")
                ),
            )

        # list
        topic = {}
        for x in range(40):
            if len(driver.find_elements_by_name("lblVolItm" + str(x + 6))) > 0:
                topic.setdefault(
                    "第" + str(x + 1) + "回",
                    [
                        driver.find_element_by_name(
                            "lblVolItm" + str(x + 6)
                        ).get_attribute("value"),
                        driver.find_element_by_name(
                            "lblVolItm" + str(46 + x)
                        ).get_attribute("value"),
                    ],
                )
            elif len(driver.find_elements_by_name("lblVolItm38")) > 0:
                topic.setdefault(
                    "授業計画1",
                    driver.find_element_by_name("lblVolItm38").get_attribute("value"),
                )
                break
            else:
                break
        if len(driver.find_elements_by_name("lblVolItm5")) > 0:
            topic.setdefault(
                "授業外学習2",
                driver.find_element_by_name("lblVolItm5").get_attribute("value"),
            )
        grading = {}
        for z in range(len(driver.find_elements_by_class_name("output")) - 2):
            # grading
            for x in range(
                len(
                    driver.find_elements_by_class_name("output")[z + 2]
                    .find_element_by_tag_name("tbody")
                    .find_elements_by_tag_name("tr")
                )
            ):
                if (
                    len(
                        driver.find_elements_by_class_name("output")[z + 2]
                        .find_element_by_tag_name("tbody")
                        .find_elements_by_tag_name("tr")[x]
                        .find_elements_by_tag_name("td")
                    )
                    == 1
                ):
                    i = x
                    if (
                        driver.find_elements_by_class_name("output")[z + 2]
                        .find_element_by_tag_name("tbody")
                        .find_elements_by_tag_name("tr")[x]
                        .find_elements_by_tag_name("th")
                        is None
                        or len(
                            driver.find_elements_by_class_name("output")[z + 2]
                            .find_element_by_tag_name("tbody")
                            .find_elements_by_tag_name("tr")[x]
                            .find_elements_by_tag_name("th")
                        )
                        == 0
                    ):
                        i = 0
                    # print(driver.find_elements_by_class_name('output')[z + 2].find_element_by_tag_name(
                    #     'tbody').find_elements_by_tag_name('tr')[i].find_elements_by_tag_name('th')[0].text)
                    grading.setdefault(
                        (
                            (
                                driver.find_elements_by_class_name("output")[z + 2]
                                .find_element_by_tag_name("tbody")
                                .find_elements_by_tag_name("tr")[i]
                                .find_elements_by_tag_name("th")[0]
                                .text
                            )
                            + str(x)
                        ).replace("\n", ""),
                        driver.find_elements_by_class_name("output")[z + 2]
                        .find_element_by_tag_name("tbody")
                        .find_elements_by_tag_name("tr")[x]
                        .find_elements_by_tag_name("td")[0]
                        .text,
                    )
                else:
                    num = []
                    for y in range(
                        len(
                            driver.find_elements_by_class_name("output")[z + 2]
                            .find_element_by_tag_name("tbody")
                            .find_elements_by_tag_name("tr")[x]
                            .find_elements_by_tag_name("td")
                        )
                    ):
                        num.append(
                            driver.find_elements_by_class_name("output")[z + 2]
                            .find_element_by_tag_name("tbody")
                            .find_elements_by_tag_name("tr")[x]
                            .find_elements_by_tag_name("td")[y]
                            .text
                        )
                    grading.setdefault(
                        (
                            driver.find_elements_by_class_name("output")[z + 2]
                            .find_element_by_tag_name("tbody")
                            .find_elements_by_tag_name("tr")[0]
                            .find_elements_by_tag_name("th")[0]
                            .text
                            + str(x)
                        ).replace("\n", ""),
                        num,
                    )
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
        risyuuki = driver.find_element_by_name("lblAc201ScrDispNm_01").get_attribute(
            "value"
        )
        othersJa.setdefault("履修期", risyuuki[0 : risyuuki.find("／")])
        if len(driver.find_elements_by_name("lblVolCd1")) != 0:
            language = driver.find_element_by_name("lblVolCd1").get_attribute("value")
            othersJa.setdefault("主な教授言語", language[0 : language.find("／")])
        othersJa.setdefault(
            "授業目的", driver.find_element_by_name("lblVolItm2").get_attribute("value")
        )
        othersJa.setdefault(
            "到達目標", driver.find_element_by_name("lblVolItm3").get_attribute("value")
        )

        othersJa.setdefault(
            "特記事項", driver.find_element_by_name("lblVolItm1").get_attribute("value")
        )
        othersJa.setdefault(
            "関連科目", driver.find_element_by_name("lblVolItm4").get_attribute("value")
        )

        othersJa.setdefault(
            "授業方法", driver.find_element_by_name("lblVolItm43").get_attribute("value")
        )
        othersJa.setdefault("トピック", topic)
        othersJa.setdefault("評価", grading)
        i = 1
        while "項番No." + str(i) in grading:
            subject.setdefault(
                "時限" + str(i), day_data.index(grading["項番No." + str(i)][2])
            )
            i += 1
        i = 1
        while "成績評価Grading" + str(i) in grading:
            if grading["成績評価Grading" + str(i)][0] == "備":
                break
            subject.setdefault(
                "評価" + str(i), score.index(grading["成績評価Grading" + str(i)][0])
            )
            i += 1
        subject.setdefault("開講期", term_data.index(grading["項番No.1"][1]))
        data.setdefault(name, subject)
        searchingADJa = {**othersJa, **subject}
        with open("docs/all/" + str(name) + ".json", "w") as f:
            json.dump(searchingADJa, f, ensure_ascii=False)
        sleep(1)
        data_all = {}
        data_all.update(data)
        json_open_all = open("docs/all.json", "r")
        json_load_all_files = json.load(json_open_all)
        json_load_all_files.update(data_all)
        with open("docs/all.json", "w") as f:
            json.dump(json_load_all_files, f, ensure_ascii=False)
        id_json_list = open("docs/id.json", "r")
        id_json_list = json.load(id_json_list)
        id_json_list.update({name: 0})
        with open("docs/id.json", "w") as f:
            json.dump(id_json_list, f, ensure_ascii=False)
    # if os.path.isfile("docs/" + str(m) + '.json') and os.stat("docs/" + str(m) + '.json').st_size > 0:
    #     json_open = open("docs/" + str(m) + '.json', 'r')
    #     json_load = json.load(json_open)
    #     data.update(json_load)
    driver.quit()
    return
