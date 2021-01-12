#coding=utf-8
import requests
import time
import base64
import json
t1 = time.time()
s = requests
with open('6.jpg', 'rb') as f:
    imgbase64 = base64.b64encode(f.read())
data={'imgbase64':imgbase64, 'class_id':'base', 'face_public_sign':1}
r = s.post('http://192.168.132.151:8086/findfaces', data)

print(json.loads(r.text))
print('time cost:', time.time() - t1)
