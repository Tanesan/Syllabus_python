import xml.etree.ElementTree as ET

import pandas

json_open_all = open("docs/all.json", 'r')

df = pandas.read_json(json_open_all)

urls = [
    "https://univ-syllabus.web.app/",
]

for i in df.columns.values.tolist():
    urls.append("https://univ-syllabus.web.app/subject/" + i)

urlset = ET.Element('urlset')
urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
tree = ET.ElementTree(element=urlset)

for url in urls:
    url_element = ET.SubElement(urlset, 'url')
    loc = ET.SubElement(url_element, 'loc')
    loc.text = url
    lastmod = ET.SubElement(url_element, 'lastmod')
    lastmod.text = "2021-08-17T09:34:48+00:00"
    priority = ET.SubElement(url_element, 'priority')
    lastmod.text = "1.00"

tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)