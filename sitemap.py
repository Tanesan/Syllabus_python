import xml.etree.ElementTree as ET

import pandas
import datetime
import requests
import os

def access_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードが200系以外は例外を発生させる
        return response.text  # レスポンスの内容をテキスト形式で返す
    except requests.exceptions.RequestException as e:
        return f'エラーが発生しました: {e}'

dt_now = datetime.datetime.now()
nt = dt_now.isoformat()
json_open_all = open("docs/all.json", 'r')

df = pandas.read_json(json_open_all)

urls = []

for i in df.columns.values.tolist():
    urls.append("https://kgu-syllabus.com/subject/" + i)

urlset = ET.Element('urlset')
urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
tree = ET.ElementTree(element=urlset)

url_element = ET.SubElement(urlset, 'url')
loc = ET.SubElement(url_element, 'loc')
loc.text = "https://kgu-syllabus.com/"
lastmod = ET.SubElement(url_element, 'lastmod')
lastmod.text = "2024-03-20"
priority = ET.SubElement(url_element, 'priority')
priority.text = "1.00"

url_element = ET.SubElement(urlset, 'url')
loc = ET.SubElement(url_element, 'loc')
loc.text = "https://kgu-syllabus.com/search"
lastmod = ET.SubElement(url_element, 'lastmod')
lastmod.text = "2024-03-20"
priority = ET.SubElement(url_element, 'priority')
priority.text = "0.80"

for url in urls:
    url_element = ET.SubElement(urlset, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = url
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = "2024-03-20"
    priority = ET.SubElement(url_element, 'priority')
    priority.text = "0.80"

tree.write('docs/sitemap.xml', encoding='utf-8', xml_declaration=True)
url = os.getenv('TARGET_URL')
result = access_url(url)
