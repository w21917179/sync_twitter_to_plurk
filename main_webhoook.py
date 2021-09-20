from flask import Flask
from flask import request
import requests
from requests_oauthlib import OAuth1
import json
import re
import base64
import hashlib
import hmac
import json
from hashlib import sha1
import os

#Token
TWITTER_CONSUMER_SECRET = ''
plurk_app_key = ''
plurk_app_secret = ''
plurk_oauth_token = ''
plurk_oauth_token_secret = ''

app = Flask(__name__)


@app.route("/", methods=['GET'])
def getpost():   
    # creates HMAC SHA-256 hash from incomming token and your consumer secret
    sha256_hash_digest = hmac.new(
        TWITTER_CONSUMER_SECRET.encode('utf-8'),
        msg=request.args.get('crc_token').encode('utf-8'),
        digestmod=hashlib.sha256).digest()
    print(sha256_hash_digest)
    # construct response data with base64 encoded hash
    response = {
        'response_token':
        'sha256=' + base64.b64encode(sha256_hash_digest).decode()
    }

    # returns properly formatted json response
    return json.dumps(response)


@app.route("/", methods=['POST'])
def gethook():

    data = request.get_json()
    #print("======\n" + str(data) + "\n======")
    #print(json.dumps(data, indent=4, sort_keys=True))

    
    if 'tweet_create_events' in data:
        #當推文過長時，完整推文會被放到extended_tweet；當有圖片時，圖片連結會放在extended_entites
        #先找有沒有extended_tweet，沒有的話取text，並設定extended_entites
        extended = data['tweet_create_events'][0].get('extended_tweet')
        if extended == None:
            text = data['tweet_create_events'][0]['text']
            extended_entities = data['tweet_create_events'][0].get('extended_entities', 'empty')
        else:
            text = extended['full_text']
            extended_entities = extended.get('extended_entities', 'empty')
        text = re.sub(r'https:\/\/t.co\/[a-zA-Z0-9]*', '', text)
        text = text.strip()
        print('去除短網址後 : %s' % text)

	#下載圖片，上傳至plurk取得網址後放入text
        if 'media' in extended_entities:
            text = text + '\n'
            for media in extended_entities['media']:
                mediaName = media['media_url_https'][-10:]
                mediaURL = media['media_url_https'] + ':orig'
                print(mediaURL)
                print(mediaName)
                r = requests.get(mediaURL, allow_redirects=True)
                open(mediaName, 'wb').write(r.content)
                f = open(mediaName, 'rb')
                files = {'image': f}
                plurkurl = 'https://www.plurk.com/APP/Timeline/uploadPicture'
                plurkauth = OAuth1(plurk_app_key, plurk_app_secret, plurk_oauth_token, plurk_oauth_token_secret)
                plurkR = requests.post(plurkurl, auth=plurkauth, files=files)
                plurkRjson = plurkR.json()
                text = text + ' ' + plurkRjson['full']
                f.close()
                os.remove(mediaName)
                
        print('加入連結後的文章 : %s' % text)
        
        #plurk發送
        url = 'https://www.plurk.com/APP/Timeline/plurkAdd'
        auth = OAuth1(plurk_app_key, plurk_app_secret, plurk_oauth_token, plurk_oauth_token_secret)
        payload = {'content': str(text), 'qualifier': ':'}
        r = requests.get(url, auth=auth, params=payload)
        print('發送成功')
        
      

    return '200 ok'


if __name__ == "__main__":
    app.run(port=80)

