from flask import Flask, render_template, request
from bs4 import BeautifulSoup as bs
from pprint import pprint
import requests
import datetime
import tweepy
import os
import sys
import urllib.request
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def test():
    return render_template('post.html')


#네이버 영화 크롤링: 해당 제목을 포함한 영화 리스트 중 제작년도가 가장 높은(첫번쨰) 영화를 return
#검색 결과가 없을 경우 return 0
def naverCrawling(n_keyword):
    client_id = "Kw_PMevdgZUJD9ambF8M"
    client_secret = "qanriQHPfu"

    encText = urllib.parse.quote(n_keyword)
    url = "https://openapi.naver.com/v1/search/movie?query=" + encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        data = json.loads(response_body)

        if (data['total'] == 0):
            return 0
        else:
            return data['items'][0]
    else:
        print("Error Code:" + rescode)
        return 0


#네이버 영화 크롤링을 통해 선택된 첫번째 영화 제목과 개봉일을 매개변수로 트위터 크롤링
def twitCrawling(mv_title, mv_date):
    result = []

    # API 인증요청
    consumer_key = "8sguu5nvZiFXYswLBnK3NVZet"
    consumer_secret = "ElK12VDlXkFtNhAVhg8YjKYQGYvT1ismnMYK1F0bFe0wJlPBqU"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

    # access 토큰 요청
    access_token = "2937765217-b4OZAWAFwyCIbm58y00QZVNx3voBj8DYBnlDgQY"
    access_token_secret = "I3wQHTDVluA498nVaE9oNuXRvXouLIJXn3lT4EANR59U2"
    auth.set_access_token(access_token, access_token_secret)

    # twitter API 생성
    api = tweepy.API(auth, wait_on_rate_limit=True)

    location = "%s,%s,%s" % ("35.95", "128.25", "1000km")

    cursor = tweepy.Cursor(api.search,
                           q=mv_title,
                           count=100,
                           since="2019-11-15",
                           until="2019-11-27",
                           geocode=location,
                           include_entities=True)

    file = open('movie.txt', 'w', encoding="utf-8")

    j = 0
    for i, tweet in enumerate(cursor.items()):
        if (not tweet.retweeted) and ('RT @' not in tweet.text):
            tweet_text = [tweet.text]
            tweet_list = [line.strip('\n') for line in tweet_text]
            print("{}: {}".format(j, tweet_list))
            result.append("{}: {}".format(j, tweet_list))
            file.write("{}: {}".format(j, tweet_list) + '\n')
            j = j + 1;

    file.close()

    return result

#영화 개봉일 크롤링
def dateCrawling(mv_title):
    html = requests.get('https://search.naver.com/search.naver?query=' + mv_title)
    soup = bs(html.text, 'html.parser')

    print('https://search.naver.com/search.naver?query=' + mv_title);
    mv_date = soup.find('div', {'class': 'info_group'})
    mv_date = mv_date.find('dd')
    print(mv_date);
    mv_date = mv_date.findAll('span')
    mv_date_len = len(mv_date)

    if(mv_date_len < 3):
        return "0"
    else:
        if(len(mv_date[2].text)>5):
            mv_date = mv_date[2].text
            mv_date = mv_date[0:10]
            mv_date = mv_date.replace(" ", "")
            mv_date = mv_date.replace(".", "-")

            return mv_date  #검색용 날짜
        else:
            return "0"


@app.route('/post', methods=['POST'])
def post():
    n_keyword = request.form['keyword']
    moviedata = naverCrawling(n_keyword)

    if(moviedata == 0): #네이버 영화 크롤링 결과가 없을 경우 "결과 없음" 출력
        return render_template(
            'result.html',
            title="크롤링 결과 페이지",
            mv_title="결과 없음"
        )
    else: #네이버 영화 크롤링 결과가 있을 경우, 필요한 영화 정보 크롤링 후 트위터 크롤링 함수 실행
        mv_title = moviedata['title']
        mv_title = mv_title.replace("<b>", "")
        mv_title = mv_title.replace("</b>", "")         #영화 제목
        print(mv_title)

        mv_subtitle = moviedata['subtitle']
        mv_subtitle = mv_subtitle.replace("<b>", "")
        mv_subtitle = mv_subtitle.replace("</b>", "")   #영화 영문 제목
        print(mv_subtitle)
        mv_userRating = moviedata['userRating']         #유저 평점
        print(mv_userRating)
        mv_year = moviedata['pubDate']                  #영화 제작년도
        print(mv_year)

        #영화 상세 페이지 이동 후 크롤링
        url = moviedata['link']
        html = requests.get(url)
        soup = bs(html.text, 'html.parser')

        mv_info_area = soup.find('div', {'class': 'mv_info_area'})

        mv_info_spec = mv_info_area.find('dl', {'class': 'info_spec'})
        mv_info_spec = mv_info_spec.findAll('dd')

        mv_info = mv_info_spec[0].text              #영화 정보(장르, 국가, 러닝타임, 개봉일, 재개봉일..)

        mv_director = moviedata['director']         #감독
        mv_actor = moviedata['actor']               #배우
        print(mv_actor)

        mv_poster = mv_info_area.find('div', {'class': 'poster'})
        mv_poster = mv_poster.find('img')
        mv_poster = mv_poster['src']                #포스터 이미지 주소

        #영화 제목으로 개봉일 네이버 검색 크롤링
        mv_date = dateCrawling(mv_title)            #트위터 크롤링용 검색 날짜
        mv_release = mv_date                        #영화 개봉일
        now = datetime.now()

        if (mv_date == "0"):  #영화 개봉일이 없을 경우 개봉년도로 대체
            mv_date = mv_year
            mv_release = mv_year

        if (int(mv_year) < 2006):  #영화 개봉년도가 트위터 생성년도보다 이전일 경우 현재 날짜로 대체
            mv_date = '%s-%s-%s' % (now.year, now.month, now.day)
            mv_release = mv_year

        print(mv_date)
        #영화 제목과 날짜로 트윗 크롤링
        twit_result = twitCrawling(mv_title, mv_date)

        return render_template(
            'result.html',
            title="크롤링 결과 페이지",
            mv_title=mv_title,
            mv_subtitle=mv_subtitle,
            mv_release=mv_release,
            mv_date=mv_date,
            mv_userRating=mv_userRating,
            mv_info = mv_info,
            mv_director = mv_director,
            mv_actor = mv_actor,
            mv_poster=mv_poster,
            twit_result=twit_result
        )


@app.route('/team')
def team():
   return render_template('team.html', title='TEAM')


@app.route('/project')
def project():
   return render_template('project.html', title='PROJECT')


if __name__ == '__main__':
    app.run()

