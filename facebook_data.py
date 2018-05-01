# Copyright 2007-2009 WebDriver committers
# Copyright 2007-2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
from datetime import date, timedelta;
import time;
from sys import platform
import requests

# facebook crawling
# access_token deleted for security purpose

app_id = "140635716554581"
app_secret = "a50fb37b7e5393ab023f6ba4917fc484"
access_token = app_id + "|" + app_secret
page_id_korea = "206910909512230"
page_id_yonsei = "180446095498086"
page_id_snu = "560898400668463"
since = str(date.today() - timedelta(1))
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
    req_url = req.Request(url)
    success = False
    while success is False:
        try:
            response = req.urlopen(req_url)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)  # wnat to know what error it is
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
                    i = i + 1
                except:
                    break
                    ############

            # get next page comment json
            nex = json.loads(request_until_suceed(page['paging']['next']))
            page = nex
            j = j + 1;
            # print("   %d th comment in one status" % j)
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
    # print("대나무 숲은 데이터를 긁어오는데 시간이 걸립니다. 조금만 기다려주세요\n 컴퓨터성능에 따라 1~5분정도 걸립니다.")
    one_json = getFacebookPageFeedData(page_id, access_token, since, until)
    wan_data = ""
    j = 0
    i = 0
    num = 0
    while True:
        try:
            test_status = one_json["data"][i]
            num_likes = test_status["likes"]["summary"]["total_count"]

            if num_likes > 200:
                processed_test_status = processFacebookPageFeedStatus(test_status)
                # wan_data.append(list(processed_test_status))
                wan_data += str(processed_test_status)
                # print("%d th status in %d" % (i, num))
                num = num + 1
            i = i + 1
        except Exception as e:
            # print(e)
            try:
                next_url = one_json["paging"]["next"]  # next url
                # print(next_url)
                j = j + 1
                # print("----")
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
    # elif type == 8:
    #     news = fetch_feed(page_id_korea)
    # # 통일연세
    # elif type == 9:
    #     news = fetch_feed(page_id_yonsei)
    # # 자주관악
    # elif type == 10:
    #     news = fetch_feed(page_id_snu)

print(fetch_feed(page_id_korea))