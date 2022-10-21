from flask import Flask,render_template,request

import tweepy
import csv
import MeCab
import pandas as pd

app =Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')

def Tweets_get(contents,number):
    # 認証に必要なキーとトークン
    API_KEY = 'cBJiQZHospBgBTwjCuO0wkM8R'
    API_SECRET = 'zdZ1PtGot0wqStiSDWzsn7cCfcLmoBmDa4n7iaxMi48tHcZnND'
    BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAJ2RfwEAAAAAwulLF62rAjRfIBzZcEEYXoGNoCE%3DXCPERUadD7LsShu9qaqNY8mVbRnJqFMioMqrmnyw5EoAIzL9Hd'
    ACCESS_TOKEN = '1558117300641079296-Lal44ACEn52BSECx59sTUFvdPDP7EL'
    ACCESS_TOKEN_SECRET = 'awvX9nHfBiJw5QYCIZVNtVQpNMsXdXtKLaOcrn55LAg3y'

    # APIの認証
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    # キーワードからツイートを取得
    tweet_count=number
    api = tweepy.API(auth)
    tweets = api.search_tweets(q=[contents], count=tweet_count)
    if(len(tweets) < tweet_count):
        print(contents+"のツイート数は"+str(tweet_count)+"未満でした．" + "\n"+ "ツイート数の設定を下げてください．")
        exit()
    tweets_list=[]
    for number in range(tweet_count):
        tweets_list.append(tweets[number].text)
    return tweets_list

class positive_negative:
    def __init__(self,text):
        self.text=text
    def read_dict(self):
        self.pn_yougen_dict, self.pn_meishi_dict = read_positive_negative_dict()
    def processing(self):
        self.word_list = text_processing(self.text)
    def judge(self):
        self.evaluate_result = judge_positive_negative(self.word_list,self.pn_yougen_dict, self.pn_meishi_dict)
    def result(self):
        self.positive_tweet_number,self.negative_tweet_number,self.sort_score=evaluate_result(self.evaluate_result)
        return self.positive_tweet_number,self.negative_tweet_number
    def pick_up(self):
        self.top3_positive_tweet,self.top3_negative_tweet=tweet_pick_up(self.text,self.sort_score)
        return self.top3_positive_tweet,self.top3_negative_tweet

def read_positive_negative_dict():
    ###csvファイル読み込み to dict型
    with open('yougen_positive_negative_dict.csv', mode = 'r', encoding = 'utf-8') as yougen_dict_file, open('meishi_positive_negative_dict.csv', mode = 'r', encoding ='utf-8') as meishi_dict_file:
        yougen_reader = csv.reader(yougen_dict_file)
        yougen_positive_negative_dict = {rows[0]:rows[1] for rows in yougen_reader}
        meishi_reader = csv.reader(meishi_dict_file)
        meishi_positive_negative_dict = {rows[0]:rows[1] for rows in meishi_reader}
    
    return yougen_positive_negative_dict, meishi_positive_negative_dict #pn_dict

def text_processing(text):
    mecab = MeCab.Tagger()
    word_list = []
    for sentence in text:
        sentence_word_list=[]
        for word_detail in mecab.parse(sentence).splitlines():
            word_detail_split=word_detail.split()
            if(len(word_detail_split) == 2):
                word = word_detail_split[0]
                word_infromation = word_detail_split[1].split(',')
                hinshi=word_infromation[0] #hinsi は 品詞
                if (hinshi in ['名詞','形容詞','動詞','副詞']):
                    sentence_word_list.append(word)
        word_list.append(sentence_word_list)
    
    return word_list

def judge_positive_negative(word_list,pn_yougen_dic,pn_meishi_dic):
    evaluate_result = []
    for sentence in word_list:
        sentence_result=[]
        for word in sentence:
            word_score = []
            yougen_score = pn_yougen_dic.get(word)
            meishi_score=pn_meishi_dic.get(word)
            if(yougen_score != None and meishi_score != None):
                score = max(int(yougen_score),int(meishi_score))
            elif(yougen_score != None):
                score = yougen_score
            elif(meishi_score != None):
                score= meishi_score
            else:
                score = None
            word_score = (word, score)
            sentence_result.append(word_score)
        evaluate_result.append(sentence_result)
    
    return evaluate_result

def evaluate_result(evaluate_result):
    tweet_count=0
    positive_tweet_count,negative_tweet_count=0,0
    TweetNumber_Score=[]
    for evaluate in evaluate_result:
        tweet_score_count=0
        for word, score in evaluate:
            if(score != None):
                tweet_score_count += int(score)
        score_average = tweet_score_count/len(evaluate) if len(evaluate)!=0 else 0
        if(score_average>0):
            positive_tweet_count+=1
        elif(score_average<0):
            negative_tweet_count+=1
        
        TweetNumber_Score.append((tweet_count,score_average))
        tweet_count+=1
        
    sort_score=sorted( TweetNumber_Score,key = lambda x: x[1])

    return positive_tweet_count, negative_tweet_count,sort_score

def tweet_pick_up(text,sort_score):
    top3_positive=sort_score[len(sort_score)-3:len(sort_score)]
    top3_positive=top3_positive[::-1]
    top3_negative=sort_score[:3]
    top3_positive_tweet,top3_negative_tweet=[],[]
    for number,score in top3_positive:
        if(score>0):
            top3_positive_tweet.append(text[number])
    for number,score in top3_negative:
        if(score<0):
            top3_negative_tweet.append(text[number])

    return top3_positive_tweet,top3_negative_tweet

@app.route('/', methods=['POST'])
def main():
    #contents=input("評価したいものを入力してください"+"\n"+"例:ワンピース"+"\n")
    contents=request.form.get('contents')
    contents_split=contents.split()
    number = request.form.get('tweet_number',type = int)
    tweets_list=Tweets_get([contents_split],number)
    pn = positive_negative(tweets_list)
    pn.read_dict()
    pn.processing()
    pn.judge()
    positive_user_count,negative_user_count=pn.result()
    top3_positive_tweet,top3_negative_tweet=pn.pick_up()
    user_count=[positive_user_count,negative_user_count]

    return render_template("index.html",user_count=user_count, contents=contents, number=number,
    top3_positive_tweet=top3_positive_tweet,top3_negative_tweet=top3_negative_tweet)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
###https://qiita.com/y_itoh/items/4693bd8f64ac811f8524
###https://qiita.com/y_itoh/items/7c528a04546c79c5eec2
