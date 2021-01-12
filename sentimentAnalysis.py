class KnuSL():

   def data_list(wordname):
       with open('C:\\Users\\hj243\\OneDrive\\바탕 화면\\KnuSentiLex-master\\KnuSentiLex-master\\data', encoding='utf-8-sig', mode='r') as f:
           data = json.load(f)
       result = ['None', 'None']
       for i in range(0, len(data)):
           if data[i]['word'] == wordname:
               result.pop()
               result.pop()
               result.append(data[i]['word_root'])
               result.append(data[i]['polarity'])

       r_word = result[0]
       s_word = result[1]

       print('어근 : ' + r_word)
       print('극성 : ' + s_word)

       return r_word, s_word


if __name__ == "__main__":

   ksl = KnuSL

   while (True):
       wordname = 'movie_adj_list.txt'
       wordname = wordname.strip(" ")
       if wordname != "#":
           print(ksl.data_list(wordname))
           print("\n")


       elif wordname == "#":
           print("\n이용해주셔서 감사합니다~ :)")
           break
