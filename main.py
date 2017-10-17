#Copyright 2007-2009 WebDriver committers
#Copyright 2007-2009 Google Inc.
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


import sys, os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import feedparser
import urllib.request as req
import urllib.request
import re
import datetime
import json;  import csv
from datetime import date,timedelta; import time;
from sys import platform

#windows hidpi support
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
 
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

#facebook crawling
# access_token deleted for security purpose
app_id = ""
app_secret = ""
access_token = app_id + "|" + app_secret
page_id_korea = "206910909512230"
page_id_yonsei = "180446095498086"
page_id_snu = "560898400668463"
since = str(date.today()-timedelta(1))
until = str(date.today())


# advaced information
def getFacebookPageFeedData(page_id, access_token, since, unitl):
    # construct the URL string
    # print("get Facebook Page Feed Data() is called")
    base = "https://graph.facebook.com"
    node = "/" + page_id + "/feed"
    parameters1 = "/?fields=message,created_time,likes.limit(1).summary(true),"
    # -b - cf -  comments.fields(message,parent).summary(true) (- cannot see replies)
    # -b - changed if you add parent in  filter(stream){message,id,"parent"}, you can see parent
    parameters2 = "comments.summary(true).filter(stream){message,like_count}"
    time = "&since=%s&until=%s" % (since, until)
    access = "&access_token=%s" % access_token
    url = base + node + parameters1 + parameters2 + time + access
    # print(url)  ###DEL

    # retrieve data
    data = json.loads(request_until_suceed(url))

    return data


def request_until_suceed(url):
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try:
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            # print(e)  # wnat to know what error it is
            time.sleep(5)
            # print("Error for url %s : %s" % (url, datetime.datetime.now()))

    return response.read().decode(response.headers.get_content_charset())


def fetch_comments(status, status_message):
    # print("fetch comments is called")
    com = status_message
    page = ' ' if 'comments' not in status.keys() else status['comments']
    # print json.dumps(page, indent=4, sort_keys=True) ###DELETE
    j = 0  ################DELETE
    while True:  # until no more next
        try:

            comments = ' ' if 'comments' not in status.keys() else page['data']
            ##########until no more comment in page
            i = 0
            while True:

                try:
                    # append message and comments using :]
                    # http://me2.do/5ZryZrRd(not considering codec error

                    like_count = comments[i]['like_count']

                    if like_count > 10:
                        com = com + ' :] ' + comments[i]['message'].encode('cp949', errors='replace').decode('cp949')
                        # print("like_count : %s"%like_count)
                    i = i+1
                except:
                    break
                    ############

            # get next page comment json
            nex = json.loads(request_until_suceed(page['paging']['next']))
            page = nex
            j = j + 1;
            #print("   %d th comment in one status" % j)
            # print json.dumps(page, indent=4, sort_keys=True)###DELETE

        except KeyError:  # no more next
            break

    return com


def processFacebookPageFeedStatus(status):
    # key is the name of the list
    status_message = ' ' if 'message' not in status.keys() else status['message'].encode('cp949',
                                                                                         errors='replace').decode(
        'cp949')
    # time(http://devanix.tistory.com/306)
    status_published = datetime.datetime.strptime(status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=+9)
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')

    num_likes = 0 if 'likes' not in status.keys() else status['likes']['summary']['total_count']
    num_comments = 0 if 'comments' not in status.keys() else status['comments']['summary']['total_count']
    com = fetch_comments(status, status_message)

    return (status_message, status_published, num_likes, com)


def fetch_feed(page_id):
    # print("I am string")
    print("대나무 숲은 데이터를 긁어오는데 시간이 걸립니다. 조금만 기다려주세요\n 컴퓨터성능에 따라 1~5분정도 걸립니다.")
    one_json = getFacebookPageFeedData(page_id, access_token, since, until)
    wan_data = ""
    j = 0
    i = 0
    num = 0
    while True:
        try:
            test_status = one_json["data"][i]
            num_likes = test_status["likes"]["summary"]["total_count"]

            if num_likes > 200 :
                processed_test_status = processFacebookPageFeedStatus(test_status)
                # wan_data.append(list(processed_test_status))
                wan_data+=str(processed_test_status)
                # print("%d th status in %d" % (i, num))
                num = num + 1
            i = i + 1
        except Exception as e:
            # print(e)
            try:
                next_url = one_json["paging"]["next"]  # next url
                print(next_url)
                j = j + 1
                print("----")
                # print j #FOR CHECK
                one_json = json.loads(request_until_suceed(next_url))
                i = 0
                continue
            except KeyError:
                # print('End of Document')
                break
        # print(wan_data)
    # print("get out")
    return str(wan_data)

# 뉴스 전문 파싱
def get_text(URL):
  source_code_from_URL = req.urlopen(URL)
  soup = BeautifulSoup(source_code_from_URL, 'lxml', from_encoding='utf-8')
  text = ''
  for item in soup.find_all('div', itemprop='articleBody'):
    text = text + str(item.find_all(text=True))
  return text

def mainnews():
    news=""
    RSS_URL = "http://fs.jtbc.joins.com//RSS/newsrank.xml"
    news_link = feedparser.parse(RSS_URL)

    for i in range(0, len(news_link)):
        URL = news_link.entries[i].link
        TITLE = news_link.entries[i].title
        result_text = TITLE + '\n' + get_text(URL) + '\n\n'

        result_text = re.sub('[a-zA-Z]', '', result_text)
        result_text = re.sub('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]', '', result_text)

        news+=result_text

    return news


def writecontent(type):

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

    elif type == 7:
        news=mainnews()

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
    
    #민족고대
    elif type ==8:
        news=fetch_feed(page_id_korea)
        # print("before")
    #통일연세
    elif type==9:
        news=fetch_feed(page_id_yonsei)
#         print(news)
    
    #자주관악
    elif type==10:
        news=fetch_feed(page_id_snu)
#         print(news)

    for a in news:
        if type == 4 or type ==7 or type ==8 or type==9 or type==10:
            b = a
        else:
            b = a.string

        if (b != None):

            if (totalcharacter + len(b) > 730):
                contents[numberofpages]+="@@ https://minjunkwak.github.io/ @@"
                numberofpages += 1
                totalcharacter = 0
                contents.append("")

            if type == 4 or type ==7 or type==8 or type==9 or type==10:

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
    print("자동화된 크롬창을 건들면 프로시져가 취소됩니다.")
    print("휴대폰 인증이 뜨면 인증을 해주세요")

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
    driver.find_element_by_css_selector("#childInfo").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector("#letterBtn").click()

    # 휴대폰 인증
    # driver.find_element_by_css_selector("#childInfo").click()
    # driver.find_element_by_css_selector("#letterBtn").click()
    driver.find_element_by_css_selector("#jwxe_main_content > div > div > div.btn_wrap > form > a").click()

    driver.implicitly_wait(3000)


    for type in types:
        # 제목은 오늘날짜
        today = str(datetime.date.today())
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
        elif type==9:
            today+=" 연세대학교 대나무숲"
        elif type==10:
            today+=" 서울대학교 대나무숲"
        title = today

        writecontent(type)

        # 크롬창 알림 제거
        alert = driver.switch_to_alert()
        print("편지 작성이 시작됩니다. 크롬창을 가만히 두세요")
        # 편지작성(글자수에 따른 분할)
        for i in range(0, numberofpages + 1):
            driver.find_element_by_css_selector("#article_title").send_keys(title + str(i + 1))
            driver.find_element_by_css_selector("#article_text").send_keys(contents[i])
            driver.find_element_by_css_selector("#writer_password").send_keys("1234")
            driver.find_element_by_css_selector(
                "#jwxe_main_content > div > div > form > fieldset > div > div > input").click()
            alert.accept()
            # print("waitbefore")
            # driver.implicitly_wait(80)
            # print("waitafter")

            driver.find_element_by_css_selector("#letterBtn").click()

    driver.quit()


# 보내는 편지의 장수
numberofpages = 0
# 보내는 편지의 문장들
contents = ["@@ https://minjunkwak.github.io/ @@"]

enrollmentdate = "20170904"
name = "이인준"
birthday = "940228"
types = [7,0,4,3,8,9,10]


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 400, 360, 360)

        # Label
        soldiername = QLabel("훈련병 이름", self)
        soldiername.move(20, 25)

        enlistmentdate = QLabel("입대일", self)
        enlistmentdate.move(20, 60)

        soldierbirthdate = QLabel("훈련병 생일", self)
        soldierbirthdate.move(20, 95)

        soldiername = QLabel("(예: 이인준)", self)
        soldiername.move(200, 25)

        enlistmentdate = QLabel("(예: 20170908)", self)
        enlistmentdate.move(200, 60)

        soldierbirthdate = QLabel("(예: 940228)", self)
        soldierbirthdate.move(200, 95)



        # LineEdit
        self.lineEditName = QLineEdit("", self)
        self.lineEditName.move(90, 25)
        self.lineEditName.textChanged.connect(self.lineEditChanged)

        self.lineEditEnlistmentDate = QLineEdit("", self)
        self.lineEditEnlistmentDate.move(90, 60)
        self.lineEditEnlistmentDate.textChanged.connect(self.lineEditChanged)

        self.lineEditSoldierBirthDate = QLineEdit("", self)
        self.lineEditSoldierBirthDate.move(90, 95)
        self.lineEditSoldierBirthDate.textChanged.connect(self.lineEditChanged)



        global inputName,inputBirth,inputEnroll


        # StatusBar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.checkbox1 = QCheckBox("JTBC Top 10 전문", self)
        self.checkbox1.move(20, 125)
        # self.checkbox1.setChecked(True)
        self.checkbox1.stateChanged.connect(self.checkBoxState)
        # self.radio1.clicked.connect(self.radioButtonClicked)
        self.checkbox1.resize(200,30)

        self.checkbox2 = QCheckBox("중앙일보 기본, 연예, 스포츠 요약", self)
        self.checkbox2.move(20, 145)
        # self.checkbox2.clicked.connect(self.radioButtonClicked)
        self.checkbox2.stateChanged.connect(self.checkBoxState)
        self.checkbox2.resize(200, 30)

        self.checkbox3 = QCheckBox("텍스트 파일", self)
        self.checkbox3.move(20, 165)
        self.checkbox3.stateChanged.connect(self.checkBoxState)
        # self.checkbox3.clicked.connect(self.radioButtonClicked)

        self.checkbox4 = QCheckBox("CNN 요약", self)
        self.checkbox4.move(20, 185)
        self.checkbox4.stateChanged.connect(self.checkBoxState)
        # self.radio4.clicked.connect(self.radioButtonClicked)

        self.checkbox5 = QCheckBox("고대 대나무숲", self)
        self.checkbox5.move(20, 205)
        self.checkbox5.stateChanged.connect(self.checkBoxState)
        # self.radio5.clicked.connect(self.radioButtonClicked)

        self.checkbox6 = QCheckBox("연대 대나무숲", self)
        self.checkbox6.move(20, 225)
        self.checkbox6.stateChanged.connect(self.checkBoxState)

        self.checkbox7 = QCheckBox("서울대 대나무숲", self)
        self.checkbox7.move(20, 245)
        self.checkbox7.resize(300, 30)
        self.checkbox7.stateChanged.connect(self.checkBoxState)


        textLabel = QLabel("Message:  ", self)
        textLabel.move(20, 265)

        self.label = QLabel("", self)
        self.label.move(80, 265)
        self.label.resize(300, 30)

        btn1 = QPushButton("보내기", self)
        btn1.move(200, 305)
        btn1.clicked.connect(self.btn1_clicked)


        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def lineEditChanged(self):

        global name,enrollmentdate,birthday
        name=self.lineEditName.text()
        enrollmentdate=self.lineEditEnlistmentDate.text()
        birthday=self.lineEditSoldierBirthDate.text()


    def checkBoxState(self):

        msg = ""
        global types
        types=[]
        # print(types)
        if self.checkbox1.isChecked() == True:
            msg += "JTBC 뉴스 Top 10 전문 "
            types.append(7)
            # print(types)
        elif self.checkbox1.isChecked() != True:
            for i in range(0,types.count(7)):
                types.remove(7)
            # print(types)

        if self.checkbox2.isChecked() == True:
            msg += "중앙일보 기본, 연예, 스포츠 요약 "
            types.append(0)
            # print(types)
        elif self.checkbox2.isChecked() !=True:
            for i in range(0,types.count(0)):
                types.remove(0)

        if self.checkbox3.isChecked() == True:
            msg += "텍스트 파일 "
            types.append(4)
            # print(types)
        elif self.checkbox3.isChecked() != True:
            for i in range(0,types.count(4)):
                types.remove(4)

        if self.checkbox4.isChecked() == True:
            msg += "CNN 요약 "
            types.append(3)
            # print(types)
        elif self.checkbox4.isChecked() != True:
            for i in range(0,types.count(3)):
                types.remove(3)

        if self.checkbox5.isChecked() == True:
            msg += "고대 대나무숲 "
            types.append(8)
            # print(types)
        elif self.checkbox5.isChecked() != True:
            for i in range(0,types.count(8)):
                types.remove(8)

        if self.checkbox6.isChecked() == True:
            msg += "연대 대나무숲 "
            types.append(9)
            # print(types)
        elif self.checkbox6.isChecked() != True:
            for i in range(0, types.count(9)):
                types.remove(9)
                
        if self.checkbox7.isChecked() == True:
            msg += "서울대 대나무숲 "
            types.append(10)
            # print(types)
        elif self.checkbox7.isChecked() != True:
            for i in range(0, types.count(10)):
                types.remove(10)

        self.statusBar.showMessage(msg)

    def btn1_clicked(self):

        # regexp
        regexName = r'[가-힣]'
        regexEnroll = r'(?<!\d)(?:(?:20\d{2})(?:(?:(?:0[13578]|1[02])31)|(?:(?:0[1,3-9]|1[0-2])(?:29|30)))|(?:(?:20(?:0[48]|[2468][048]|[13579][26]))0229)|(?:20\d{2})(?:(?:0?[1-9])|(?:1[0-2]))(?:0?[1-9]|1\d|2[0-8]))(?!\d)'
        regexBirth = r'^((\d{2}((0[13578]|1[02])(0[1-9]|[12]\d|3[01])|(0[13456789]|1[012])(0[1-9]|[12]\d|30)|02(0[1-9]|1\d|2[0-8])))|([02468][048]|[13579][26])0229)$'

        global inputName, inputEnroll,inputBirth

        self.label.setText(" 핸드폰 인증이 뜰때까지 아무것도 건드리지마세요")

        inputName = re.findall(regexName, self.lineEditName.text())
        inputEnroll = re.findall(regexEnroll, self.lineEditEnlistmentDate.text())
        inputBirth = re.findall(regexBirth, self.lineEditSoldierBirthDate.text())

        # print(inputName, inputEnroll,inputBirth)
        if inputName==[]:
            self.label.setText(" 이름이 형식에 맞지 않습니다")
            print("이름이 형식에 맞지 않습니다 다시 입력해주세요")
            return
        if inputEnroll==[]:
            self.label.setText(" 입대일이 형식에 맞지 않습니다")
            print("입대일이 형식에 맞지 않습니다 다시 입력해주세요")
            return
        if inputBirth==[]:
            self.label.setText(" 훈련병 생일이 형식에 맞지 않습니다")
            print("훈련병 생일이 형식에 맞지 않습니다 다시 입력해주세요")
            return

        global name,birthday,enrollmentdate, types

        self.label.setText(" 핸드폰 인증이 뜰때까지 아무것도 건드리지마세요")

        print(types)
        sendletter(name,birthday,enrollmentdate, types)
        self.label.setText(" 편지작성이 모두 완료되었습니다.")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
    
    
#내가 훈련소에 있었을때 매일밤 이 모든 작업을 수작으로 하였던 내 아버지에게 바칩니다.
