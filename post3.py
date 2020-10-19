#coding=utf-8
import requests
import time
import base64

t1 = time.time()
s = requests
name = '张三'
data={'delname':name}
r = s.post('http://0.0.0.0:8082/delfaces', data)

print(r.text)
print('time cost:', time.time() - t1)
