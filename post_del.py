#coding=utf-8
import requests
import time
import base64
import json
t1 = time.time()
s = requests
data={'class_id':'base', 'delname':'王力宏'}
r = s.post('http://192.168.132.151:8086/delfaces', data)

print(json.loads(r.text))
print('time cost:', time.time() - t1)
