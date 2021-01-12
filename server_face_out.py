import face_recognition
import cv2, os, shutil, fcntl, json
import numpy as np
import time,re
import random
from skimage import io

from updata_face import add_face

import requests
from flask import Flask,render_template,request
import base64

# test
def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

def find_faces(imgpath, data_npy_root, class_id, face_public_sign):
    sign = -1
    data_npy_path = os.path.join(data_npy_root, class_id, 'data.npy')
    if not os.path.exists(data_npy_path):
        return {'sign':sign, 'names':[], 'locations':[]}
    data_face = np.load(data_npy_path, allow_pickle=True).item()
    known_face_encodings = data_face.get('faces_encodes')
    known_face_names = data_face.get('face_paths')
    
    if face_public_sign == 1: # 使用公共人脸数据
        data_face2 = np.load(os.path.join(data_npy_root, 'base', 'data.npy'), allow_pickle=True).item()
        known_face_encodings2 = data_face2.get('faces_encodes')
        known_face_names2 = data_face2.get('face_paths')
        known_face_encodings.extend(known_face_encodings2)
        known_face_names.extend(known_face_names2)
    
    #print(known_face_names)
    knownpersons = []
    knownlocations = []
    # Grab a single frame of video                                                                                   
    print('>>>>>>', imgpath)
    # Initialize some variables
    face_locations = []                                                                                          
    face_encodings = []
    face_names = []
    process_this_frame = True
    time.sleep(0.1)
    
    try:
        io.imread(imgpath)
    except Exception as e:
        print(e)
    #try:
    frame = cv2.imread(imgpath)
    # Resize frame of video to 1/4 size for faster face recognition processing
    # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    #small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    x = frame.shape[1]
    y = frame.shape[0]
    img_resize_k = 1
    small_frame = cv2.resize(frame,(int(x*img_resize_k), int(y*img_resize_k)))

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    knownlocations_out = []
    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.40)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)
        sign = 0 # 0,1,2 means:noperson, unknownperson, knownperson
        if not len(face_names) == 0:
            sign = 1
            knownpersons = []
            cnt_dst = 0
            for person in face_names:
                if not person == 'Unknown':
                    sign = 2
                    knownpersons.append(person.split('/')[-1].split('.')[0])
                    knownlocations.append(face_locations[cnt_dst])
                cnt_dst = cnt_dst + 1
            for knownlocations_i in knownlocations:
                location_tuple_0 = int(knownlocations_i[0]/img_resize_k)
                location_tuple_1 = int(knownlocations_i[1]/img_resize_k)
                location_tuple_2 = int(knownlocations_i[2]/img_resize_k)
                location_tuple_3 = int(knownlocations_i[3]/img_resize_k)
                knownlocations_out.append({'x1':location_tuple_0,'y1':location_tuple_1,'x2':location_tuple_2,'y2':location_tuple_3})
    #except:
    #    pass

    print(sign, knownpersons)
    str1 = str(sign) + ':' + str(knownpersons)
    if os.path.exists(imgpath):
        os.remove(imgpath)
    return {'sign':sign, 'names':knownpersons, 'locations':json.dumps(knownlocations_out)}

# Get a reference to webcam #0 (the default one)

app = Flask(__name__)
imgroot = 'images'
txtroot = 'result'
updata_faces_root = 'updata_faces'
del_faces_root = 'del_faces'
data_npy_root = 'data_face_npy'
face_save_root = 'data_face'
face_crop_root = '/opt/docker/python/img_all/face_crops/'

@app.route("/findfaces",methods = ['GET', 'POST'])
def findfaces():
    if request.method == "POST":
        # base64data encode to iamge and save
        imgbase64 = request.form.get('imgbase64')
        class_id = request.form.get('class_id')
        face_public_sign = request.form.get('face_public_sign')
        imgbase64 = re.sub(r'data:image/[a-zA-Z]*;base64,', "",imgbase64)
        imgbase64 = imgbase64.replace("data:image/jpeg;base64,", "")
        imgdata = base64.b64decode(imgbase64)
        randname = getRandomSet(15)
        imgrandpath = os.path.join(imgroot, randname + '.jpg')
        file = open(imgrandpath,'wb')
        file.write(imgdata)
        file.close()
        print(imgrandpath)
        #try:
        str1  = find_faces(imgrandpath, data_npy_root, class_id, face_public_sign)
        #except:
        #    str1 = {"sign":-1, "names":''}
        return str1
    else:
        return "<h1>Find faces, please use post!</h1>"

@app.route("/addfaces",methods = ['GET', 'POST'])
def addface():
    if request.method == "POST":
        imgbase64 = request.form.get('imgbase64')
        class_id = request.form.get('class_id')
        imgbase64 = re.sub(r'data:image/[a-zA-Z]*;base64,', "",imgbase64)
        imgbase64 = imgbase64.replace("data:image/jpeg;base64,", "")
        imgdata = base64.b64decode(imgbase64)
        name = request.form.get('name')
        
        img_root = os.path.join(face_save_root, class_id)
        if not os.path.exists(img_root):
            os.makedirs(img_root)
        imgpath = os.path.join(img_root, name+'.jpg')
        file = open(imgpath,'wb')
        file.write(imgdata)
        file.close()
        sign = add_face(imgpath, data_npy_root, class_id)
        if sign == -1:
            os.remove(imgpath)
            return json.dumps({'sign':-1})
        else:
            return json.dumps({'sign':1})
    else:
        return "<h1>Updata faces, please use post!</h1>"

@app.route("/delfaces",methods = ['GET', 'POST'])
def delface():
    if request.method == "POST":
        delname = request.form.get('delname')
        class_id = request.form.get('class_id')
        #try:
        # 删除npy数据
        data_face_npy_path = os.path.join(data_npy_root, class_id, 'data.npy')
        if not os.path.exists(data_face_npy_path):
            print('not exists this npy')
            return json.dumps({'sign':-1})
        data_face_npy = np.load(data_face_npy_path, allow_pickle=True).item()
        faces_encodes = data_face_npy.get('faces_encodes')
        face_names = data_face_npy.get('face_paths')
        names = []
        for n in face_names:
            names.append(n.split('/')[-1].split('.jpg')[0])
        try:
            index_ = names.index(delname)
            del faces_encodes[index_]
            del face_names[index_]
            print(data_face_npy_path)
            np.save(data_face_npy_path, data_face_npy) # 删除后重写npy数据

        except:
            print('not find name in npy data')
        # 删除原始图像保存
        del_img_path = os.path.join(face_save_root, class_id, delname+'.jpg')
        if not os.path.exists(del_img_path):
            print('>>>>', del_img_path)
            print('not find delname in face_save_root')
            #return json.dumps({'sign':-1})
        # 删除人脸crop
        del_face_crop_path = os.path.join(face_crop_root, class_id, delname+'.jpg')
        chinese_name = []
        rand_name = []
        record_txt_path = os.path.join(face_crop_root, class_id, 'record.txt')
        for m in open(record_txt_path):
            line = m[:-1]
            line_split = line.split(',')
            if len(line_split) == 2: # 正常行
                chinese_name.append(line_split[0])
                rand_name.append(line_split[1])
        try:
            index_ = []
            cnt = 0
            for n in chinese_name:
                if n == delname:
                    index_.append(cnt)
                cnt = cnt + 1
            for i in index_:
                del_rand_name = rand_name[i]
                del_face_crop_path = os.path.join(face_crop_root, class_id, del_rand_name)
                if os.path.exists(del_face_crop_path):
                    os.remove(del_face_crop_path)
                else:
                    print('not find delname in face_crop_root')
        except:
            return json.dumps({'sign':-1})
        
        return json.dumps({'sign':1})
        #except:
        #    return json({'sign':-1})
    else:
        return "<h1>Delete faces, please use post!</h1>"

@app.route("/getfacelist",methods = ['GET', 'POST'])
def get_face_list():
    if request.method == "POST":
        class_id = request.form.get('class_id')
        face_crop_root_2 = os.path.join(face_crop_root, class_id)
        face_crop_list = os.listdir(face_crop_root_2)
        out_url = []
        names = []
        
        record_txt_path = os.path.join(face_crop_root_2, 'record.txt')
        chinese_name = []
        randname = []
        for m in open(record_txt_path):
            line = m[:-1]
            line_split = line.split(',')
            if len(line_split) == 2: # 正常行
                chinese_name.append(line_split[0])
                randname.append(line_split[1])
        for n in face_crop_list:
            if n[-3:] == 'txt':
                continue
            index_ = randname.index(n)
            names.append(chinese_name[index_])
            temp_url = 'http://192.168.132.151:8801/' + 'img_all/face_crops/' + os.path.join(class_id, n) # 反向代理
            out_url.append(temp_url)
        return json.dumps({'sign':1, 'all_face_urls':out_url, 'all_names':names})
    else:
        return "<h1>Delete faces, please use post!</h1>"

if __name__ == '__main__':
    host = '0.0.0.0'
    port = '8086'
    app.run(debug=True, host=host, port=port)
