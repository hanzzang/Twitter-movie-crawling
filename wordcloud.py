from konlpy.tag import Okt
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json

# 1. 크롤링한 파일을 읽기전용으로 호출
file = open('movietest.txt', 'r', encoding='utf-8')
lines = file.readlines()

# 2. 변수 reaction에 전체댓글을 다시저장
reaction = []
for line in lines:
    reaction.append(line)
file.close()

okt = Okt()

# 4. 각 문장별로 형태소 구분하기
sentences_tag = []
for sentence in reaction:
    morph = okt.pos(sentence, norm=True, stem=True)
    sentences_tag.append(morph)

# 5. 형용사인 품사만 선별해 리스트에 담기
adj_list = []
finallist = []
for sentence1 in sentences_tag:
    polarlist = ['None1', 'None2']
    for word, tag in sentence1:
        if tag in ['Adjective'] and ("이다" not in word)and ("아니다" not in word)and ("있다" not in word)and ("없다" not in word)and ("많다" not in word)and ("같다" not in word)and ("그렇다" not in word)and ("이렇다" not in word)and ("어떻다" not in word):
            adj_list.append(word)
            with open('data/SentiWord_info.json', encoding='utf-8-sig', mode='r') as f:
                data = json.load(f)
            result = ['None3', 'None4']
            for i in range(0, len(data)):
                if data[i]['word'] == word:
                    result.pop()
                    result.pop()
                    result.append(data[i]['word_root'])
                    result.append(data[i]['polarity'])

            r_word = result[0]
            s_word = result[1]

            polarlist.pop()
            polarlist.pop()
            polarlist.append(r_word)
            polarlist.append(s_word)

    polar_word1 = polarlist[0]
    polar_word2 = polarlist[1]

    finallist.append(polar_word2)

print("-2점 : ", finallist.count('-2'))
print("-1점 : ", finallist.count('-1'))
print("0점 : ", finallist.count('0'))
print("1점 : ", finallist.count('1'))
print("2점 : ", finallist.count('2'))
#print("총 데이터 개수 : ", len(finallist))

a = finallist.count('-2')
b = finallist.count('-1')
c = finallist.count('0')
d = finallist.count('1')
e = finallist.count('2')

#감성분석되지 않은 데이터는 제외한 총 데이터 개수
all = a+b+c+d+e

a2 = a*1
b2 = b*2
c2 = c*3
d2 = d*4
e2 = e*5

all2 = a2+b2+c2+d2+e2

#별점(5점만점)
starnum = all2/all

print("별점 : ", starnum)

print("별점(소수점둘째자리까지) : ", "%0.2f" % starnum)


# 6. 선별된 품사별 빈도수 계산 & 빈도수대로 정렬
counts = Counter(adj_list)
tags = counts.most_common(200)

#7. 워드클라우드 만들기
wordcloud = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf', background_color='white', width=1200, height=800).generate_from_frequencies(dict(tags))

fig = plt.figure()
plt.axis('off')
plt.imshow(wordcloud)
plt.show()
fig.savefig('wordcloud_image.png')