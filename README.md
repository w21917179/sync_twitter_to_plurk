# sync twitter tweet to plurk

### 使用  

修改main檔案，將token填入
```
pip3 install -r requirements.txt  
python3 main_.py  
```

#### IFTTT  
<pre>
IF
  twitter:New tweet by you
THEN
  Webhooks:Make a web request
    URL:對外網址
    Method:POST
    Content Type:json
    Body: {"LinkToTWEET" : " {{LinkToTweet}}"}
</pre>    
    
#### twitter webhook
將對外網址註冊到twitter webhook  
參考連結  
https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/overview  
https://github.com/twitterdev/account-activity-dashboard-enterprise
