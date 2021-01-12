#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:02:24 2021

@author: kpinfo
"""
import face_recognition
import cv2, os, shutil, fcntl, json
import numpy as np
import random

def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

def add_face(imgpath, data_npy_root, class_id):
    try:
        temp_image = face_recognition.load_image_file(imgpath)
        temp_face_encoding = face_recognition.face_encodings(temp_image)[0]
        face_img = cv2.imread(imgpath)
        rgb_small_frame = face_img[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        if len(face_locations) == 0:
            print('not find face')
            return -1
    except:
        print('load face error', imgpath)
        return -1
    save_path = os.path.join(data_npy_root, class_id)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    data_npy_path = os.path.join(save_path, 'data.npy')
    if os.path.exists(data_npy_path): # 存在人脸数据
        f1 = open(data_npy_path)
        fcntl.flock(f1,fcntl.LOCK_EX) # 获取锁
        data_face = np.load(data_npy_path, allow_pickle=True).item()
        faces_encodes_list = data_face.get('faces_encodes')
        face_paths_list = data_face.get('face_paths')
        faces_encodes_list.append(temp_face_encoding)
        face_paths_list.append(imgpath)
        np.save(data_npy_path, data_face)
        fcntl.flock(f1,fcntl.LOCK_UN) # 解除锁
    else: # 新建人脸数据
        data_face = {'faces_encodes':[temp_face_encoding], 'face_paths':[imgpath]}
        np.save(data_npy_path, data_face)
        
    # 制作人脸列表
    
    (top, right, bottom, left) = face_locations[0]
    face_cropped = face_img[top:bottom, left:right, :]
    face_cropped_root = '/opt/docker/python/img_all/face_crops/'
    face_cropped_root2 = os.path.join(face_cropped_root, class_id)
    if not os.path.exists(face_cropped_root2):
        os.makedirs(face_cropped_root2)
    randname = getRandomSet(15)+'.jpg'
    chinese_name = imgpath.split('/')[-1].split('.')[0]
    face_cropped_path = os.path.join(face_cropped_root, class_id, randname)
    cv2.imwrite(face_cropped_path, face_cropped) # 再用反向代理的方式返回face_crop列表
    record_txt = os.path.join(face_cropped_root2, 'record.txt')
    file = open(record_txt,'a')
    file.write(chinese_name+','+randname)
    file.write('\n')
    file.close()
    return 1

if __name__ == "__main__":
    imgroot = 'data_face_base'
    data_npy_root = 'data_face_npy'
    class_id = 'base'
    img_list = os.listdir(imgroot)
    for n in img_list:
        imgpath = os.path.join(imgroot, n)
        sign = add_face(imgpath, data_npy_root, class_id)
        if sign == -1:
            print('failed load face: ',imgpath)
        else:
            print('scuessful load face: ',imgpath)
        
