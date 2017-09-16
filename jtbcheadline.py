from bs4 import BeautifulSoup
import urllib.request as req

url="http://fs.jtbc.joins.com//RSS/newsroom.xml"
res=req.urlopen(url)
soup=BeautifulSoup(res, "html.parser")

title_list=soup.select("title")

#print(str(soup))
for a in title_list:
    title=a.string
    print(title)
