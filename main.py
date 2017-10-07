import sys
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

app_id = ""
app_secret = ""
access_token = app_id + "|" + app_secret
page_id = "206910909512230"
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


def fetch_feed():
    # print("I am string")
    print("대나무 숲은 데이터를 긁어오는데 시간이 걸립니다. 조금만 기다려주세요")
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

# 뉴스 전문 파싱 by 강재영
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


def writeletter(type):
    totalcharacter = 0
    global numberofpages
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

    elif type ==8:
        news=fetch_feed()
        print("before")


    for a in news:
        if type == 4 or type ==7 or type ==8 :
            b = a
        else:
            b = a.string
        if (b != None):

            if (totalcharacter + len(b) > 750):
                contents[numberofpages]+="@@https://minjunkwak.github.io/@@"
                numberofpages += 1
                totalcharacter = 0
                contents.append("")

            if type == 4 or type ==7 or type==8:

                # 육군훈련소의 인터넷 편지는 줄바꿈이 인식이 되지않는다.
                if (b == "\n"):
                    b = "/"
                contents[numberofpages] += b
                totalcharacter += len(b)
            else:

                contents[numberofpages] += b + " / "
                totalcharacter += len(b) + 3


def sendletter(name, birthday, enrollmentdate, type):
    print("자동화된 크롬창을 건들면 프로시져가 취소됩니다.")
    print("휴대폰 인증이 뜨면 인증을 해주세요")
    writeletter(type)
    if platform == "darwin":
        driver = webdriver.Chrome('./chromedriver')
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

    driver.implicitly_wait(80)

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
    elif type ==8:
        today+=" 고려대학교 대나무숲"
    title = today

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
contents = [""]

enrollmentdate = "20170904"
name = "이인석"
birthday = "940223"
type = 7


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setGeometry(800, 400, 350, 350)

        # Label
        soldiername = QLabel("훈련병 이름", self)
        soldiername.move(20, 25)

        enlistmentdate = QLabel("입대일", self)
        enlistmentdate.move(20, 60)

        soldierbirthdate = QLabel("훈련병 생일", self)
        soldierbirthdate.move(20, 95)

        soldiername = QLabel("(예: 이인석)", self)
        soldiername.move(200, 25)

        enlistmentdate = QLabel("(예: 20170904)", self)
        enlistmentdate.move(200, 60)

        soldierbirthdate = QLabel("(예: 940223)", self)
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

        # StatusBar
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        self.radio1 = QRadioButton("JTBC Top 10 전문", self)
        self.radio1.move(20, 125)
        self.radio1.setChecked(True)
        self.radio1.clicked.connect(self.radioButtonClicked)
        self.radio1.resize(200,30)

        self.radio2 = QRadioButton("중앙일보 기본, 연예, 스포츠 요약", self)
        self.radio2.move(20, 145)
        self.radio2.clicked.connect(self.radioButtonClicked)
        self.radio2.resize(200, 30)

        self.radio3 = QRadioButton("텍스트 파일", self)
        self.radio3.move(20, 165)
        self.radio3.clicked.connect(self.radioButtonClicked)

        self.radio4 = QRadioButton("CNN 요약", self)
        self.radio4.move(20, 185)
        self.radio4.clicked.connect(self.radioButtonClicked)

        self.radio5 = QRadioButton("고대 대나무숲", self)
        self.radio5.move(20, 205)
        self.radio5.clicked.connect(self.radioButtonClicked)

        textLabel = QLabel("Message:  ", self)
        textLabel.move(20, 225)

        self.label = QLabel("", self)
        self.label.move(80, 225)
        self.label.resize(300, 30)

        btn1 = QPushButton("보내기", self)
        btn1.move(200, 265)
        btn1.clicked.connect(self.btn1_clicked)


        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

    def lineEditChanged(self):
        global name,enrollmentdate,birthday
        name=self.lineEditName.text()
        enrollmentdate=self.lineEditEnlistmentDate.text()
        birthday=self.lineEditSoldierBirthDate.text()


    def radioButtonClicked(self):
        msg = ""
        global type
        if self.radio1.isChecked():
            msg = "JTBC 뉴스 Top 10 전문"
            type=7

        elif self.radio2.isChecked():
            msg = "중앙일보 기본, 연예, 스포츠 요약"
            type=0

        elif self.radio3.isChecked():
            msg="텍스트 파일"
            type=4

        elif self.radio4.isChecked():
            msg= "CNN 요약"
            type=3

        elif self.radio5.isChecked():
            msg = "고대 대나무숲"
            type=8

        self.statusBar.showMessage(msg + " 선택 됨")

    def btn1_clicked(self):
        self.label.setText("핸드폰 인증이 뜰때까지 아무것도 건드리지마세요")
        global name,birthday,enrollmentdate, type
        sendletter(name,birthday,enrollmentdate, type)

    def btn2_clicked(self):
        self.label.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
