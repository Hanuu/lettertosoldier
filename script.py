import re
import feedparser
import urllib.request as req
from bs4 import BeautifulSoup



def get_text(URL):
    source_code_from_URL = req.urlopen(URL)
    soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
    text = ''
    for item in soup.find_all('div', itemprop='articleBody'):
        text = text + str(item.find_all(text=True))
    return text
    
def mainnews():
    news = ""
    RSS_URL = "http://fs.jtbc.joins.com//RSS/newsrank.xml"
    news_link = feedparser.parse(RSS_URL)

    for i in range(0, len(news_link)):
        URL = news_link.entries[i].link
        TITLE = news_link.entries[i].title
        result_text = TITLE + '\n' + get_text(URL) + '\n\n'

        result_text = re.sub('[a-zA-Z]', '', result_text)
        result_text = re.sub('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', result_text)

        news += result_text
    # print(news)
    return news
    
if __name__ == "__main__":
    print(mainnews())