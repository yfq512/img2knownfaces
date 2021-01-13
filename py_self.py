#coding=utf-8
import requests
import time
import base64
import json
import os

while True:
    try:
        s = requests
        with open('5.jpg', 'rb') as f:
            imgbase64 = base64.b64encode(f.read())
        data={'imgbase64':imgbase64, 'class_id':'test', 'face_public_sign':1}
        r = s.post('http://192.168.132.151:8086/findfaces', data)
        print(json.loads(r.text))
    except:
        str1 = '服务自启动： ' + time.strftime("%F-%H:%M:%S")
        os.system('gunicorn -c gun.py server_face_out:app')
        with open('repy.log','a') as f:
            f.write(str1)
            f.write('\n')
            f.close()
    time.sleep(1000)
