from flask import Flask
from flask import request
import requests
from requests_oauthlib import OAuth1
import json
import re

twitter_Bearer = ''
plurk_app_key = ''
plurk_app_secret = ''
plurk_oauth_token = ''
plurk_oauth_token_secret = ''

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def getpost():
    if request.method == 'POST':
        #接收資料後將網址切斷，擷取出後面的數字
        data = request.get_json()
        print("======\n" + str(data) + "\n======")
        print("twitterURL : [%s]" % data['LinkToTWEET'])
        twitterID = data['LinkToTWEET'].split("/status/")[1]
        print("twitterID : [%s]" % twitterID)

        #發送請求到twitterAPI
        url = "https://api.twitter.com/labs/2/tweets"
        headers = {
            'Authorization' : twitter_Bearer
        }
        payload ={
            'ids' : str(twitterID),
            'expansions' : 'attachments.media_keys',
            'media.fields' : 'url'
        }
        r = requests.get(url, headers=headers, params=payload)
        rjson = r.json()
        print("json : [%s]" % type(rjson['data']))
        text = rjson['data'][0]['text']

        #取出文字，並刪除短連結
        print("text : [%s]" % text)
        text = re.sub(r'https:\/\/t.co\/[a-zA-Z0-9]*','',text)
        text = text.strip()
        print("text without url : [%s]" % text)
    
        #下載圖片，上傳到plurk後將圖片網址加到文字
        for media in rjson['includes']['media']:
            mediaName =media['url'][-10:]
            mediaURL = media['url'] + ':orig'
            print(mediaURL)
            print(mediaName)
            r = requests.get(mediaURL, allow_redirects=True)
            open(mediaName, 'wb').write(r.content)
            f = open(mediaName, 'rb')
            files={'image' : f }
            plurkurl = 'https://www.plurk.com/APP/Timeline/uploadPicture'
            plurkauth = OAuth1(plurk_app_key, plurk_app_secret, plurk_oauth_token, plurk_oauth_token_secret)
            plurkR = requests.post(plurkurl, auth=plurkauth, files=files)
            plurkRjson = plurkR.json()
            text = text + '\n' + plurkRjson['full']
            f.close()
            
        #plurk發送
        url = 'https://www.plurk.com/APP/Timeline/plurkAdd'
        auth = OAuth1(plurk_app_key, plurk_app_secret, plurk_oauth_token, plurk_oauth_token_secret)
        payload = {'content': str(text), 'qualifier': ':'}
        r = requests.get(url, auth=auth, params=payload)


        return 'ok'
    else:
        return 'hello world!'


if __name__ == "__main__":
    app.run()