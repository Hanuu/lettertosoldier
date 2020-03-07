import re
import feedparser
import urllib.request as req
from bs4 import BeautifulSoup
from selenium import webdriver
import time



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
def split_content_by_pages(content, word_limit):
    numberofpages = -1
    splited_contents_list = []

    for char_index in range(0,len(content)):
        if char_index%word_limit == 0:
            numberofpages += 1
            splited_contents_list.append("")
            splited_contents_list[numberofpages] += "@@by minjun kwak@@"

        splited_contents_list[numberofpages] +=content[char_index]
    return splited_contents_list


def send_to_airforce(link):
    driver = webdriver.Chrome()

    driver.maximize_window()
    driver.get(link)


    writable_contents = split_content_by_pages(mainnews(),1100)
    page_num = 0
    for writable_content in writable_contents:
        time.sleep(0.5)
        driver.find_element_by_css_selector('#emailPic-container > div.UIbtn > span > input[type=button]').click()
        time.sleep(0.5)
        driver.find_element_by_css_selector(
            '#emailPic-container > form > div.UIview > table > tbody > tr:nth-child(3) > td > div:nth-child(1) > span > input').click()
        driver.switch_to_window(driver.window_handles[1])
        driver.find_element_by_css_selector('#keyword').send_keys("테헤란로 152")
        driver.find_element_by_css_selector(
            '#searchContentBox > fieldset > span > input[type=button]:nth-child(2)').click()
        driver.find_element_by_css_selector('#roadAddrDiv1').click()
        driver.find_element_by_css_selector('#rtAddrDetail').send_keys('22층 구글 코리아')
        driver.find_element_by_css_selector('#resultData > div > a').click()
        driver.switch_to_window(driver.window_handles[0])
        driver.find_element_by_css_selector('#senderName').send_keys('곽민준')
        driver.find_element_by_css_selector('#relationship').send_keys('친구')
        driver.find_element_by_css_selector('#title').send_keys('lettertosoldier page ' + str(page_num))
        page_num+=1
        driver.find_element_by_css_selector('#contents').send_keys(writable_content)
        driver.find_element_by_css_selector('#password').send_keys('1234')
        driver.find_element_by_css_selector('#emailPic-container > form > div.UIbtn > span.wizBtn.large.Ngray.submit > input').click()
        time.sleep(0.5)
        driver.find_element_by_css_selector('#emailPic-container > div > div > div.messageBtn > span > input[type=button]').click()
if __name__ == "__main__":
    link = "http://atc.airforce.mil.kr:8081/user/indexSub.action?codyMenuSeq=156893223&siteId=last2&menuUIType=top&dum=dum&command2=getEmailList&searchName=%EB%B0%95%EA%B4%91%EC%9B%90&searchBirth=19940701&memberSeq=218767861"
    # print(split_content_by_pages(mainnews(),1100))
    send_to_airforce(link)