from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import urllib.request as req
import datetime


def writeletter(type):
    totalcharacter=0
    global numberofpages
    url="http://www.google.com"

    if type ==1:
        url="http://fs.jtbc.joins.com//RSS/newsroom.xml"
        res=req.urlopen(url)
        soup=BeautifulSoup(res,"html.parser")
        news=soup.select("title,description")

    elif type==2:
        url="http://rss.joins.com/joins_homenews_list.xml"
        res =req.urlopen(url)
        soup=BeautifulSoup(res,"html.parser")
        news=soup.select("title,description")

    elif type ==3:
        url="http://rss.cnn.com/rss/edition.rss"
        res=req.urlopen(url)
        soup=BeautifulSoup(res,"html.parser")
        news=soup.select("*")

    elif type==4:
        f=open('text.txt','rt',encoding='UTF8')
        news=f.read()

    for a in news:
        if type !=4:
            b=a.string
        else:
            b=a
        if(b!=None):

            if(totalcharacter+len(b)>750):
                numberofpages+=1
                totalcharacter=0
                contents.append("")
                
            if type !=4:
                contents[numberofpages]+=b+" / "
                totalcharacter+=len(b)+3
            if type ==4:
                contents[numberofpages] += b
                totalcharacter+=len(b)

def sendletter(name,birthday,enrollmentdate,type):

    writeletter(type)
    driver = webdriver.Chrome()
    #크롬 창 최대화를 통해 에러제거
    driver.maximize_window()

    #육군훈련소 주소
    driver.get("http://www.katc.mil.kr/katc/community/children.jsp")

    #훈련병 신상
    select=Select(driver.find_element_by_id("search_val1"))
    select.select_by_visible_text(enrollmentdate)
    driver.find_element_by_css_selector("#birthDay").send_keys(birthday)
    driver.find_element_by_css_selector("#search_val3").send_keys(name)

    driver.find_element_by_css_selector("#item_body > div.sub_wrap > div > div > div.lo_765_left > div:nth-child(3) > div > div > div.child_search_wrap > form > fieldset > input.btn_05").click()
    driver.find_element_by_css_selector("#childInfo").click()
    driver.implicitly_wait(1)
    driver.find_element_by_css_selector("#letterBtn").click()

    #휴대폰 인증
    #driver.find_element_by_css_selector("#childInfo").click()
    #driver.find_element_by_css_selector("#letterBtn").click()
    driver.find_element_by_css_selector("#jwxe_main_content > div > div > div.btn_wrap > form > a").click()

    driver.implicitly_wait(80)

    #제목은 오늘날짜
    today=str(datetime.date.today())
    if type ==1:
        today+=" JTBC 뉴스"
    elif type == 2:
        today+= " 중앙일보 뉴스"
    elif type == 3:
        today+=" CNN 뉴스"
    elif type==4:
        today+="다시만났을때 나는 고대생이였고 그녀는 연대생이였다."
    title=today

    #크롬창 알림 제거
    alert=driver.switch_to_alert()

    #편지작성(글자수에 따른 분할)
    for i in range(0,numberofpages+1):
        driver.find_element_by_css_selector("#article_title").send_keys(title+str(i+1))
        driver.find_element_by_css_selector("#article_text").send_keys(contents[i])
        driver.find_element_by_css_selector("#writer_password").send_keys("1234")
        driver.find_element_by_css_selector("#jwxe_main_content > div > div > form > fieldset > div > div > input").click()
        alert.accept()
        #print("waitbefore")
        #driver.implicitly_wait(80)
        #print("waitafter")

        driver.find_element_by_css_selector("#letterBtn").click()



#보내는 편지의 장수
numberofpages=0
#보내는 편지의 문장들
contents=[""]

enrollmentdate = "20170904"
name="이인석"
birthday="940223"
type=2

enrollmentdate=input("입대일을 입력하세요 (ex:20170904)\n입대일: ")
name=input("훈련병의 이름을 입력하세요 (ex:이인석)\n이름: ")
birthday=input("훈련병의 생일을 입력하세요 (ex: 940223)\n생일: ")
type=int(input("보내실 편지의 내용을 정해주세요(1:JTBC 뉴스, 2:중앙일보 뉴스, 3: CNN, 4:텍스트파일) 숫자만 입력해주세요\n숫자:"))
print("핸드폰 인증이 나올때까지 아무것도 건드리지 말아주세요ㅠㅜ")

sendletter(name,birthday,enrollmentdate,type)
    
#내가 훈련소에 있었을때 매일밤 이 모든 작업을 수작으로 하였던 내 아버지에게 바칩니다.
