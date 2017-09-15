
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request as req
import datetime



#보내고자 글이 있는 URL
url="https://m.blog.naver.com/koreanewsq/221097284746"
#url="http://blog.naver.com/koreanewsq"
res=req.urlopen(url)
soup=BeautifulSoup(res,"html.parser")

#보내고자 하는 글의 HTML selector
news=soup.select_one("#SEDOC-1505431590361-1492354682 > div.se_component_wrap.sect_dsc.__se_component_area > div > div > div > div > div > div > p")

#글자수입력제한
totalcharacter=0
contents=["","","","","","","","","","","","","","","","","","","","","","","","",""]
k=0
for a in news:
    b=a.string
    
    if(b!=None):
        if(totalcharacter>650):
            k+=1
            totalcharacter=0
        contents[k]+=b
        totalcharacter+=len(b)


driver = webdriver.Chrome()

#크롬 창 최대화를 통해 에러제거
driver.maximize_window()

#육군훈련소 주소
driver.get("http://www.katc.mil.kr/katc/community/children.jsp")

#훈련병 신상
#driver.find_element_by_css_selector("#search_val1").send_keys("201709") #고쳐야함
driver.find_element_by_css_selector("#birthDay").send_keys("940223")
driver.find_element_by_css_selector("#search_val3").send_keys("이인석")

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
title=today+"뉴스"

#크롬창 알림 제거
alert=driver.switch_to_alert()

#편지작성(글자수에 따른 분할)
for i in range(0,k+1):
    driver.find_element_by_css_selector("#article_title").send_keys(title+str(i+1))
    driver.find_element_by_css_selector("#article_text").send_keys(contents[i])
    driver.find_element_by_css_selector("#writer_password").send_keys("1234")
    driver.find_element_by_css_selector("#jwxe_main_content > div > div > form > fieldset > div > div > input").click()
    alert.accept()
    #print("waitbefore")
    #driver.implicitly_wait(80)
    #print("waitafter")

    driver.find_element_by_css_selector("#letterBtn").click()
    
    #내가 훈련소에 있었을때 매일밤 이 모든 작업을 수작으로 하였던 내 아버지에게 바칩니다.