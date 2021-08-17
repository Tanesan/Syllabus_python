import xml.etree.ElementTree as ET

import pandas
import datetime

dt_now = datetime.datetime.now()
json_open_all = open("docs/all.json", 'r')

df = pandas.read_json(json_open_all)

urls = []

for i in df.columns.values.tolist():
    urls.append("https://univ-syllabus.web.app/subject/" + i)

urlset = ET.Element('urlset')
urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
tree = ET.ElementTree(element=urlset)

url_element = ET.SubElement(urlset, 'url')
loc = ET.SubElement(url_element, 'loc')
loc.text = "https://univ-syllabus.web.app/"
lastmod = ET.SubElement(url_element, 'lastmod')
lastmod.text = dt_now.isoformat()
priority = ET.SubElement(url_element, 'priority')
priority.text = "1.00"

for url in urls:
    url_element = ET.SubElement(urlset, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = url
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = dt_now.isoformat()
    priority = ET.SubElement(url_element, 'priority')
    priority.text = "0.80"

tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)