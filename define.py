import json
from time import sleep
import os
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time

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
    "ハンズオン・ラーニングセンター／Hands-on Learning Center",
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
    'オンライン受講不可/Online attendance is NOT permitted.',
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
    "プレゼンテーション・発表／Presentation (07)",
    "授業への参加度（自発性、積極性、主体性、等）／In-class participation,contribution (09)",
    "その他／Others (99)",
    "授業外学修課題／Assignment, homework required outside class (06)",
    "論文／Thesis, paper (05)",
    "実技、実験／Practical skill / Lab work (08)"
]

def _normalize_label(value):
    if value is None:
        return None
    return " ".join(value.replace("／", "/").replace("\u3000", " ").split())

def _build_index_map(values):
    return {_normalize_label(value): idx for idx, value in enumerate(values)}

def _primary_label(value):
    normalized = _normalize_label(value)
    if not normalized:
        return None
    if "/" in normalized:
        return normalized.split("/", 1)[0].strip()
    return normalized

def _build_alias_map(values):
    alias_map = {}
    collisions = set()
    for idx, value in enumerate(values):
        key = _primary_label(value)
        if not key:
            continue
        if key in alias_map and alias_map[key] != idx:
            collisions.add(key)
        else:
            alias_map[key] = idx
    for key in collisions:
        alias_map.pop(key, None)
    return alias_map

def safe_index(values, value, index_map=None, alias_map=None):
    if value is None:
        return None
    if index_map is None:
        index_map = _build_index_map(values)
    normalized = _normalize_label(value)
    idx = index_map.get(normalized)
    if idx is not None:
        return idx
    if alias_map is None:
        alias_map = _build_alias_map(values)
    return alias_map.get(_primary_label(value))

ad_data_index = _build_index_map(ad_data)
study_index = _build_index_map(study)
campas_data_index = _build_index_map(campas_data)
day_data_index = _build_index_map(day_data)
term_data_index = _build_index_map(term_data)
ad_data_alias_index = _build_alias_map(ad_data)
study_alias_index = _build_alias_map(study)
campas_data_alias_index = _build_alias_map(campas_data)
day_data_alias_index = _build_alias_map(day_data)
term_data_alias_index = _build_alias_map(term_data)

def process_td(td):
    """
    td 要素内の innerHTML を取得し、<br> タグを改行に置換、
    その他の HTML タグを除去してテキストとして返す関数。
    """
    try:
        inner_html = td.get_attribute("innerHTML")
        # <br> タグを改行に変換
        text_with_newlines = re.sub(r'<br\s*/?>', '\n', inner_html)
        # 残りの HTML タグを除去
        text = re.sub(r'<[^>]+>', '', text_with_newlines)
        text = text.replace("                                "," ")
        return text.strip()
    except Exception:
        return td.text.strip()

def safe_click(driver, by_method, selector, max_retries=3, timeout=10):
    """
    安全にクリック操作を行うヘルパー関数
    
    Args:
        driver: WebDriverインスタンス
        by_method: 要素の検索方法（By.ID, By.NAME など）
        selector: 要素のセレクタ
        max_retries: クリック操作の最大再試行回数
        timeout: 要素を待つ最大秒数
        
    Returns:
        bool: クリックが成功した場合はTrue、そうでない場合はFalse
    """
    for attempt in range(max_retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by_method, selector))
            )
            element.click()
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
    
    return False

def handle_alert(driver, timeout=3, max_retries=3):
    """
    アラートが表示されている場合に処理するヘルパー関数
    
    Args:
        driver: WebDriverインスタンス
        timeout: アラートを待つ最大秒数
        max_retries: アラート処理の最大再試行回数
        
    Returns:
        bool: アラートが処理された場合はTrue、そうでない場合はFalse
    """
    for attempt in range(max_retries):
        try:
            WebDriverWait(driver, timeout).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            
            if "同一画面で一定時間が経過しました" in alert_text:
                print("Timeout alert detected. Accepting and refreshing...")
                alert.accept()
                time.sleep(1)  # アラート処理後の安定化待機
                driver.refresh()
                return True
            
            alert.accept()
            time.sleep(1)  # アラート処理後の安定化待機
            return True
        except Exception as e:
            print(f"Alert handling failed (attempt {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(1)  # 1秒待って再試行
    
    return False


def act(m, a, b):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-ssl-errors')
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    options.add_experimental_option("prefs",prefs)
    # "/home/c0665544/work_local/chromedriver",
    # driver = webdriver.Chrome("/Users/keitotanemura/Downloads/chromedriver", options=options)
    driver = webdriver.Chrome(options=options)

    # for m in [21, 22, 23, 24, 25, 26, 28, 29, 31, 32, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
    #           52, 53, 61, 62, 63, 64, 65, 66, 68, 69, 70, 71, 72, 73, 74, 75, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91,
    #           92, 93, 94, 95, 96, 97, 98]:
    #     data = {}

    data = {}
    max_session_time = 180  # 3 minutes
    session_start = time.time()

    def get_lblLsnCd_value(index):
        name_value = f"lstSlbinftJ016RList_st[{index}].lblLsnCd"
        try:
            element = driver.find_element(By.NAME, name_value)
            # input 要素の場合は value 属性、それ以外は text を取得
            value_str = element.get_attribute("value")
            if not value_str:
                value_str = element.text
            return int(value_str.strip())
        except Exception as e:
            # 指定のインデックスの要素が見つからなかった場合は None を返す
            return None

    for i in range(a, b):
        if time.time() - session_start > max_session_time:
            driver.delete_all_cookies()
            driver.refresh()
            session_start = time.time()
        subject = {}
        fin = 0
        driver.get('https://syllabus.kwansei.ac.jp/uniasv2/UnSSOLoginControlFree')
        try:
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'selLsnMngPostCd'))
            )
            select_object = Select(select_element)
            select_object.select_by_index(1)
            select_object.select_by_value(str(m))
            
            # 年度設定
            year_2022 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'txtLsnOpcFcy'))
            )
            year_2022.clear()
            year_2022.send_keys("2025")

            if not safe_click(driver, By.NAME, 'ESearch', timeout=10):
                return False
        except UnexpectedAlertPresentException:
            if not handle_alert(driver):
                return False
                
            if not safe_click(driver, By.NAME, 'ESearch', timeout=10):
                return False
        except Exception as e:
            return False
            
        try:
            WebDriverWait(driver, 20).until(
            lambda d: d.find_element_by_name('EDispNumberSet')
        )
        except:
            print("No data found, breaking the loop.")
            break
        checked = 0
        for a in range(int(i / 100)):
            max_retry = 3
            for attempt in range(max_retry):
                try:
                    if i >= 10000:
                        threshold = get_lblLsnCd_value(99)
                        if threshold is not None:
                            if i <= threshold:
                                for idx in range(99):
                                    val = get_lblLsnCd_value(idx)
                                    if val == i:
                                        i = val
                                        checked = 1
                                        break
                        else:
                            for idx in range(99):
                                val = get_lblLsnCd_value(idx)
                                if val == i:
                                    i = val
                                    break

                    # ENextが存在しない場合の処理
                    WebDriverWait(driver, 20).until(
                        lambda d: d.find_element_by_name('ENext')
                    )
                        # 要素があればクリック
                    driver.find_element_by_name('ENext').click()
                    # クリック成功 or 存在しない場合の処理が終わったらリトライは不要
                    break
    
                except StaleElementReferenceException:
                    # StaleElementReferenceExceptionが出たら再取得のため少し待ってリトライ
                    if attempt < max_retry - 1:
                        sleep(1)  # 1秒待って再度クリックを試みる
                    else:
                        # 指定回数リトライしても失敗したら例外を再度投げて終了
                        raise
            if checked == 1:
                break

        sleep(2)
        # if len(driver.find_elements_by_name('ERefer')) != 0:
        #     if int(driver.find_element_by_name('lstSlbinftJ016RList_st[' + str(len(driver.find_elements_by_name('ERefer')) - 1) +'].lblNo').get_attribute('value')) <= i:
        #         break
        # else:
        #     sleep(0.1)
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element_by_name('ERefer')
        )
        if len(driver.find_elements_by_name('ERefer')) == 0:
            print("No data found, breaking the loop.")
            break
        try:
            elements = driver.find_elements_by_name('ERefer')
            if len(elements) == 0:
                break
            
            if i % 100 >= len(elements):
                break
            
            if not safe_click(driver, By.NAME, 'ERefer', timeout=5):
                try:
                    element = elements[i % 100]
                    driver.get(element.get_attribute("href") or driver.current_url)
                except Exception as js_e:
                    break
        except UnexpectedAlertPresentException:
            handle_alert(driver)
            try:
                elements = driver.find_elements_by_name('ERefer')
                if len(elements) > 0 and i % 100 < len(elements):
                    if not safe_click(driver, By.NAME, 'ERefer', timeout=5):
                        element = elements[i % 100]
                        driver.get(element.get_attribute("href") or driver.current_url)
                else:
                    break
            except Exception as e:
                break
        except IndexError:
            break
        except Exception as e:
            break
        # あとで
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element_by_name('lblLsnCd')
        )
        name = driver.find_element_by_name('lblLsnCd').get_attribute('value')
        campas_value = driver.find_element_by_name('lblCc019ScrDispNm').get_attribute('value')
        campas_idx = safe_index(campas_data, campas_value, campas_data_index, campas_data_alias_index)
        if campas_idx is not None:
            subject.setdefault('campas', campas_idx)
        else:
            safe_value = str(campas_value).replace('<', '&lt;').replace('>', '&gt;')
            print(f"Warning: Unknown campas value: {safe_value}")
        subject.setdefault('name', driver.find_element_by_name('lblRepSbjKnjNm').get_attribute('value'))
        ad_value = driver.find_element_by_name('lblAc119ScrDispNm').get_attribute('value')
        ad_idx = safe_index(ad_data, ad_value, ad_data_index, ad_data_alias_index)
        if ad_idx is not None:
            subject.setdefault('管理部署', ad_idx)
        else:
            safe_value = str(ad_value).replace('<', '&lt;').replace('>', '&gt;')
            print(f"Warning: Unknown 管理部署 value: {safe_value}")
        subject.setdefault('単位数', int(driver.find_element_by_name('lblSbjCrnum').get_attribute('value')))
        subject.setdefault('担当者', driver.find_element_by_name('lstChagTch_st[0].lblTchName').get_attribute('value'))
        subject.setdefault('履修基準年度', driver.find_element_by_name('lblCc004ScrDispNm').get_attribute('value'))
        subject.setdefault('履修登録方法', driver.find_element_by_name('lblTacRgMthCd').get_attribute('value'))

        if len(driver.find_elements_by_name('lblVolCd2')) != 0:
            study_value = driver.find_element_by_name('lblVolCd2').get_attribute('value')
            study_idx = safe_index(study, study_value, study_index, study_alias_index)
            if study_idx is not None:
                subject.setdefault('授業形態', study_idx)
            else:
                safe_value = str(study_value).replace('<', '&lt;').replace('>', '&gt;')
                print(f"Warning: Unknown 授業形態 value: {safe_value}")
        if len(driver.find_elements_by_name('lblVolCd3')) != 0:
            study_value = driver.find_element_by_name('lblVolCd3').get_attribute('value')
            study_idx = safe_index(study, study_value, study_index, study_alias_index)
            if study_idx is not None:
                subject.setdefault('緊急授業形態', study_idx)
            else:
                safe_value = str(study_value).replace('<', '&lt;').replace('>', '&gt;')
                print(f"Warning: Unknown 緊急授業形態 value: {safe_value}")
        if len(driver.find_elements_by_name('lblVolCd4')) != 0:
            study_value = driver.find_element_by_name('lblVolCd4').get_attribute('value')
            study_idx = safe_index(study, study_value, study_index, study_alias_index)
            if study_idx is not None:
                subject.setdefault('オンライン授業形態', study_idx)
            else:
                safe_value = str(study_value).replace('<', '&lt;').replace('>', '&gt;')
                print(f"Warning: Unknown オンライン授業形態 value: {safe_value}")
        
        driver.execute_script('document.querySelector("#slideBox3").style.display="block";')
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
        # ページ内のすべての output クラスの要素を取得（先頭2件は除く）
        tables = driver.find_elements_by_class_name('output')
        for table in tables[3:]:
            # キャプション要素があれば取得（なければ空文字）
            caption_text = ""
            try:
                caption_elem = table.find_element_by_tag_name('caption')
                caption_text = caption_elem.text.strip()
            except Exception:
                pass

            # キャプションに「教室情報」または "Classroom" が含まれている場合は教室情報テーブルとして処理
            if caption_text and ("教室情報" in caption_text or "Classroom" in caption_text):
                try:
                    tbody = table.find_element_by_tag_name('tbody')
                    rows = tbody.find_elements_by_tag_name('tr')
                except Exception:
                    rows = []
                # 行番号（0: ヘッダー行 → 空配列、以降: 各データ行の<td>セル）
                for idx, row in enumerate(rows):
                    if idx == 0:
                        grading[f"項番No.{idx}"] = []
                    else:
                        # データ行の場合、<th>（項番）は除き<td>セルのみ取得
                        td_elements = row.find_elements_by_tag_name('td')
                        # 各セルのテキストをstripして配列に
                        cell_texts = [td.text.strip() for td in td_elements if td.text.strip() != ""]
                        grading[f"項番No.{idx}"] = cell_texts

            else:
                # キャプションがないテーブル（例：成績評価や教科書テーブル）の処理
                try:
                    tbody = table.find_element_by_tag_name('tbody')
                    rows = tbody.find_elements_by_tag_name('tr')
                except Exception:
                    rows = []
                if not rows:
                    continue

                # 最初の行に th が存在する場合はヘッダー行として扱う
                header_ths = rows[0].find_elements_by_tag_name('th')
                if header_ths:
                    if "教科書" in header_ths[0].text or "更新日時" in header_ths[0].text or "参考文献" in header_ths[0].text:
                        base_key = header_ths[0].text.replace("\n", "/").strip()
                    else:
                        base_key = header_ths[0].text.replace("\n", "").strip()
                    header_tds = rows[0].find_elements_by_tag_name('td')
                    if header_tds:
                        header_values = [process_td(td) for td in header_tds]
                        grading[f"{base_key}0"] = header_values
                    for idx, row in enumerate(rows[1:], start=1):
                        tds = row.find_elements_by_tag_name('td')
                        if tds:
                            values = [process_td(td).replace("\n", "") for td in tds]
                            if len(values) == 1:
                                grading[f"{base_key}{idx}"] = values[0]
                            grading[f"{base_key}{idx}"] = values
                else:
                    for row in rows:
                        th_elements = row.find_elements_by_tag_name('th')
                        td_elements = row.find_elements_by_tag_name('td')
                        if th_elements and td_elements:
                            key_base = th_elements[0].text.replace("\n", "/")
                            value = process_td(td_elements[0].replace("\n", ""))
                            suffix = 0
                            key = f"{key_base}{suffix}"
                            while key in grading:
                                suffix += 1
                                key = f"{key_base}{suffix}"
                            grading[key] = value
        othersJa = {}
        risyuuki = driver.find_element_by_name('lblAc201ScrDispNm_01').get_attribute('value')
        othersJa.setdefault('履修期', risyuuki[0: risyuuki.find('／')])
        if len(driver.find_elements_by_name('lblVolCd1')) != 0:
            language = driver.find_element_by_name('lblVolCd1').get_attribute('value')
            othersJa.setdefault('主な教授言語', language[0: language.find('／')])
        raw_html = driver.find_element_by_name('lblVolItm2').get_attribute('value')
        clean_text = re.sub(r'<[^>]*>', '', raw_html).strip()
        othersJa.setdefault('授業目的', clean_text)
        raw_html = driver.find_element_by_name('lblVolItm3').get_attribute('value')
        clean_text = re.sub(r'<[^>]*>', '', raw_html).strip()
        othersJa.setdefault('到達目標', clean_text)
        othersJa.setdefault('特記事項', driver.find_element_by_name('lblVolItm1').get_attribute('value'))
        othersJa.setdefault('関連科目', driver.find_element_by_name('lblVolItm4').get_attribute('value'))
        if len(driver.find_elements_by_name('lblVolItm80')) != 0:
            othersJa.setdefault('授業の概要・背景', driver.find_element_by_name('lblVolItm80').get_attribute('value'))
        raw_html = driver.find_element_by_name('lblVolItm43').get_attribute('value')
        clean_text = re.sub(r'<[^>]*>', '', raw_html).strip()
        othersJa.setdefault('授業方法', clean_text)
        othersJa.setdefault('トピック', topic)
        term_value = driver.find_element_by_name('lstSlbtchinftJ002List_st[0].lblAc201ScrDispNm_03').get_attribute(
            'value')
        term_index = safe_index(term_data, term_value, term_data_index, term_data_alias_index)
        subject['開講期'] = term_index
        othersJa.setdefault('評価', grading)
        for i in range(0, 8):
            try:
                element_name = f"lstSlbtchinftJ002List_st[{i}].lblTmtxCd"
                element = driver.find_element_by_name(element_name)
                value = element.get_attribute("value")
                term_index = safe_index(day_data, value, day_data_index, day_data_alias_index)
                subject[f'時限{i+1}'] = term_index

            except NoSuchElementException:
                break
        i = 1
        has_grading_field = False
        while "成績評価Grading" + str(i) in grading:
            has_grading_field = True
            if grading["成績評価Grading" + str(i)][0] == "備":
                break
            if grading["成績評価Grading" + str(i)][0] in score:
                subject.setdefault('評価' + str(i), score.index(grading["成績評価Grading" + str(i)][0]))
            i += 1
        
        if not has_grading_field:
            safe_name = str(name).replace('<', '&lt;').replace('>', '&gt;')
            print(f"Warning: No 成績評価Grading field found for {safe_name}. Need to re-scrape.")
            return False
        remark_sections = driver.find_elements(By.XPATH, "//th[contains(text(), '成績評価')]/ancestor::tbody//tr[td[@colspan='4']]")

        if remark_sections and len(remark_sections) > 0:
            subject.setdefault('成績評価備考',remark_sections[0].text)
        data.setdefault(name, subject)
        searchingADJa = {**othersJa, **subject}
        with open('docs/all/' + str(name) + '.json', 'w+') as f:
            json.dump(searchingADJa, f, ensure_ascii=False)
        data_all = {}
        data_all.update(data)
        json_open_all = open("docs/all.json", 'r')
        json_load_all_files = json.load(json_open_all)
        json_load_all_files.update(data_all)
        with open("docs/all.json", 'w') as f:
            json.dump(json_load_all_files, f, ensure_ascii=False)
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
