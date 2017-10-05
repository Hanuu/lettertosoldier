
import json
import csv
import datetime
import time
import urllib.request

app_id = " "
app_secret = " "
access_token = app_id + "|" + app_secret
page_id = " "
since = " "
until = " "

# advaced information
def getFacebookPageFeedData(page_id, access_token, since, unitl):
    # construct the URL string
    base = "https://graph.facebook.com"
    node = "/" + page_id + "/feed"
    parameters1 = "/?fields=message,created_time,likes.limit(1).summary(true),"
    # -b - cf -  comments.fields(message,parent).summary(true) (- cannot see replies)
    # -b - changed if you add parent in  filter(stream){message,id,"parent"}, you can see parent
    parameters2 = "comments.summary(true).filter(stream){message,like_count}"
    time = "&since=%s&until=%s" % (since, until)
    access = "&access_token=%s" % access_token
    url = base + node + parameters1 + parameters2 + time + access
    print(url)  ###DEL

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
            print(e)  # wnat to know what error it is
            time.sleep(5)
            print("Error for url %s : %s" % (url, datetime.datetime.now()))

    return response.read().decode(response.headers.get_content_charset())


def fetch_comments(status, status_message):
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
                    # http://me2.do/5ZryZrRd(not considering codec error)
                    
                    like_count = comments[i]['like_count']

                    if like_count > 10 :
                        com = com + ' :] ' + comments[i]['message'].encode('cp949', errors= 'replace').decode('cp949')
                        i = i + 1
                except:
                    break
                    ############

            # get next page comment json
            nex = json.loads(request_until_suceed(page['paging']['next']))
            page = nex
            j = j + 1;
            print("   %d th comment in one status" % j)
            # print json.dumps(page, indent=4, sort_keys=True)###DELETE

        except KeyError:  # no more next
            break

    return com


def processFacebookPageFeedStatus(status):
    # key is the name of the list
    status_message = ' ' if 'message' not in status.keys() else status['message'].encode('cp949', errors= 'replace').decode('cp949')
    # time(http://devanix.tistory.com/306)
    status_published = datetime.datetime.strptime(status['created_time'], '%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=+9)
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')

    num_likes = 0 if 'likes' not in status.keys() else status['likes']['summary']['total_count']
    num_comments = 0 if 'comments' not in status.keys() else status['comments']['summary']['total_count']
    com = fetch_comments(status, status_message)

    return (status_message, status_published, num_likes, com)


def fetch_feed():
    one_json = getFacebookPageFeedData(page_id, access_token, since, until)
    wan_data = []
    j = 0
    i = 0
    num = 0
    while True:
        try:
            test_status = one_json["data"][i]
            processed_test_status = processFacebookPageFeedStatus(test_status)

            if processed_test_status[2] > 200 :
                wan_data.append(list(processed_test_status))
                print("%d th status in %d" % (i, num))
                num = num + 1
            i = i + 1
        except Exception as e:
            print(e)
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
                print('End of Document')
                break

    return wan_data, num


#######CSV######
def write_csv(wan_data, num):
    with open('data %s %s.csv' % (since, until), 'wt', encoding = 'cp949') as file:  #, encoding='utf8'
        w = csv.writer(file)
        w.writerow(['content_names', 'content_dates', 'content_hits', 'content_coms'])
        for i in range(num):
            w.writerow([i, wan_data[i][1], wan_data[i][2], wan_data[i][3]])
            # w.writerow([wan_data[6][0],wan_data[6][1],wan_data[6][2],wan_data[6][3]])

#####JSON######
def save_json(data,fname):
    import json
    with open(fname, 'w') as f:
         json.dump(data, f)


######################
wan_data, num = fetch_feed()
write_csv(wan_data, num)
#save_json(wan_data,'facebook_my_feed.json')


