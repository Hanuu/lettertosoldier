import sys, os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import feedparser
import urllib.request as req
import re
import datetime
import json
from datetime import date, timedelta
import time
from sys import platform
import requests

def get_dccontent(articlenumber):
    url="http://gall.dcinside.com/board/view/?id=bitcoins&no="+articlenumber+"&page=1&exception_mode=recommend"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Mactinosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0"
    }
    r = requests.get(url, headers=headers)
    html=r.text
    soup=BeautifulSoup(str(html),"lxml")
    result_text=str(soup.find_all(class_="s_write"))

    result_text = re.sub('[a-zA-Z]', '', result_text)
    result_text = re.sub('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', result_text)
    return result_text

def get_dchtml():
    url="http://gall.dcinside.com/board/lists/?id=bitcoins&page=1&exception_mode=recommend"

    # 페이지 이름
    # payload = {"id": "bitcoins","page":"1"}
    # 디씨인사이드는 현재 파이썬을 이용한 파싱을 막고있다.
    headers={
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent":"Mozilla/5.0 (Mactinosh; Intel Mac OS X 10.12; rv:57.0) Gecko/20100101 Firefox/57.0"
    }
    r=requests.get(url,headers=headers)
    return r.text

def dcwrite():

    ret=""
    raw_html = get_dchtml()

    soup = BeautifulSoup(str(raw_html), "lxml")
    tr_data = soup.find_all("tr", class_="tb")

    # print(dt1)

    # 게시글번호
    soup = BeautifulSoup(str(tr_data), "lxml")
    articlenumbers = soup.find_all("td", class_="t_notice")

    # 게시글 제목
    soup = BeautifulSoup(str(tr_data), "lxml")
    articletitles = soup.find_all("td", class_="t_subject")

    # 게시글 작성자 + ip
    soup = BeautifulSoup(str(tr_data), "lxml")
    articlewriters = soup.find_all("td", class_="t_writer")

    soup = BeautifulSoup(str(tr_data), "lxml")
    articletime = soup.find_all("td", class_="t_date")

    # string = str(articletime[6])

    datetoday = str(datetime.date.today()-datetime.timedelta(1)).split("-")

    for i in range(0, len(articlenumbers)):
        # dc_ip=articlewriters[i].get("ip")
        # dc_user=articlewriters[i].get("user_name")
        dc_num = articlenumbers[i].get_text()
        dc_title = articletitles[i].get_text()
        string = str(articletime[i])
        dc_time = string[26:45]

        dc_date = []
        dc_date.append(dc_time[0:4])
        dc_date.append(dc_time[5:7])
        dc_date.append(dc_time[8:10])

        if dc_date == datetoday:
            # print(dc_ip)
            # print(dc_user)
            ret+=dc_num+"/"
            ret+="제목: "+dc_title+"/"
            # ret+="시간: "+dc_time+"/"
            # print(dc_date)
            ret+="내용: "+get_dccontent(dc_num)+"/"
            ret+="---------------------"
    return ret

def writecontent(type,length):
    totalcharacter = 0
    global numberofpages, contents
    numberofpages = 0
    contents = [""]
    url = "http://www.google.com"

    if type == 1:
        url = "http://fs.jtbc.joins.com//RSS/newsroom.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("title,description")

    elif type == 2:
        url = "http://rss.joins.com/joins_homenews_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("title,description")

    elif type == 3:
        url = "http://rss.cnn.com/rss/edition.rss"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("*")

    elif type == 4:
        f = open('text.txt', 'rt', encoding='UTF8')
        news = f.read()

    elif type == 5:
        url = "http://rss.joins.com/sonagi/joins_sonagi_star_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("title,description")

    elif type == 6:
        url = "http://rss.joins.com/sonagi/joins_sonagi_sports_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("title,description")

    elif type==11:
        news=dcwrite()

    elif type == 0:

        url = "http://rss.joins.com/joins_homenews_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news = soup.select("title,description")

        url = "http://rss.joins.com/sonagi/joins_sonagi_sports_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news += soup.select("title,description")

        url = "http://rss.joins.com/sonagi/joins_sonagi_star_list.xml"
        res = req.urlopen(url)
        soup = BeautifulSoup(res, "html.parser")
        news += soup.select("title,description")

    for a in news:
        if type == 4 or type == 7 or type == 8 or type == 9 or type == 10 or type==11:
            b = a
        else:
            b = a.string

        if (b != None):

            if (totalcharacter + len(b) > length-70):
                contents[numberofpages] += "@@ https://minjunkwak.github.io/ @@"
                numberofpages += 1
                totalcharacter = 0
                contents.append("")

            if type == 4 or type == 7 or type == 8 or type == 9 or type == 10 or type==11:

                # 육군훈련소의 인터넷 편지는 줄바꿈이 인식이 되지않는다.
                if (b == "\n"):
                    b = "/"
                contents[numberofpages] += b
                totalcharacter += len(b)
            else:

                contents[numberofpages] += b + " / "
                totalcharacter += len(b) + 3

    numberofpages += 1
    totalcharacter = 0
    contents.append("")
    contents[numberofpages] += "@@ https://minjunkwak.github.io/ @@"


uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])


def sendletter(name, birthday, enrollmentdate, types):
    # print("자동화된 크롬창을 건들면 프로시져가 취소됩니다.")
    # print("휴대폰 인증이 뜨면 인증을 해주세요")


    if platform == "darwin":
        driver = webdriver.Chrome("./chromedriver")
    elif platform == "win32":
        driver = webdriver.Chrome()

    # 크롬 창 최대화를 통해 에러제거
    driver.maximize_window()

    # 육군훈련소 주소
    driver.get("http://www.katc.mil.kr/katc/community/children.jsp")

    # 훈련병 신상
    select = Select(driver.find_element_by_id("search_val1"))
    select.select_by_visible_text(enrollmentdate)
    driver.find_element_by_css_selector("#birthDay").send_keys(birthday)
    driver.find_element_by_css_selector("#search_val3").send_keys(name)

    driver.find_element_by_css_selector(
        "#item_body > div.sub_wrap > div > div > div.lo_765_left > div:nth-child(3) > div > div > div.child_search_wrap > form > fieldset > input.btn_05").click()
    driver.find_element_by_css_selector("#childInfo1").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector("#letterBtn").click()

    # 휴대폰 인증
    # driver.find_element_by_css_selector("#childInfo").click()
    # driver.find_element_by_css_selector("#letterBtn").click()
    driver.find_element_by_css_selector("#jwxe_main_content > div > div > div.btn_wrap > form > a").click()

    driver.implicitly_wait(3000)

    for type in types:
        # 제목은 오늘날짜
        today = str(datetime.date.today()-datetime.timedelta(1))
        if type == 1:
            today += " JTBC 뉴스"
        elif type == 2:
            today += " 중앙일보 뉴스"
        elif type == 3:
            today += " CNN 뉴스"
        elif type == 4:
            today += "텍스트파일.txt"
        elif type == 5:
            today += " 중앙일보 연예 뉴스"
        elif type == 6:
            today += " 중앙일보 스포츠 뉴스"
        elif type == 7:
            today += " JTBC 탑텐 뉴스 전문"
        elif type == 0:
            today += " 중앙일보 기본, 연예, 스포츠 뉴스"
        elif type == 8:
            today += " 고려대학교 대나무숲"
        elif type == 9:
            today += " 연세대학교 대나무숲"
        elif type == 10:
            today += " 서울대학교 대나무숲"
        elif type == 11:
            today+="비트코인 갤러리 개념글"
        title = today

        writecontent(type,800)

        # 크롬창 알림 제거



        # print("편지 작성이 시작됩니다. 크롬창을 가만히 두세요")
        # 편지작성(글자수에 따른 분할)
        for i in range(0, numberofpages + 1):
            driver.find_element_by_css_selector("#article_title").send_keys(title + str(i + 1))
            driver.find_element_by_css_selector("#article_text").send_keys(contents[i])
            driver.find_element_by_css_selector("#writer_password").send_keys("1234")
            driver.find_element_by_css_selector(
                "#jwxe_main_content > div > div > form > fieldset > div > div > input").click()

            driver.implicitly_wait(3)
            alert = driver.switch_to.alert
            try:
                alert.accept()
            except:
                pass
            # print("waitbefore")
            # driver.implicitly_wait(80)
            # print("waitafter")

            driver.find_element_by_css_selector("#letterBtn").click()


# 보내는 편지의 장수
numberofpages = 0
# 보내는 편지의 문장들
contents = ["@@ https://minjunkwak.github.io/ @@"]


sendletter("정재훈",940915,"20180201",[11])
# print(dcwrite())