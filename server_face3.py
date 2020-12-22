import face_recognition
import cv2, os, shutil, fcntl
import numpy as np
import time,re
import random
from skimage import io

import requests
from flask import Flask,render_template,request
import base64

def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

def updata_faces(updata_faces_root, dstroot):
    newfaces_list = os.listdir(updata_faces_root)
    if len(newfaces_list) == 0:
        return None, None
    new_face_encodings = []
    new_face_names = []
    for n in newfaces_list:
        img_face_path = os.path.join(updata_faces_root, n)
        print('adding faces: ', img_face_path)
        temp_image = face_recognition.load_image_file(img_face_path)
        try:
            temp_face_encoding = face_recognition.face_encodings(temp_image)[0]
        except:
            print('adding face error: ', img_face_path)
            continue
        new_face_encodings.append(temp_face_encoding)
        new_face_names.append(n.split('.')[0])
        copy_root = os.path.join(dstroot, n.split('.')[0]+'_auto')
        if not os.path.exists(copy_root):
            os.makedirs(copy_root)
        copy_path = os.path.join(copy_root, n.split('.')[0]+'_auto.jpg')
        shutil.copyfile(img_face_path, copy_path)
        os.remove(img_face_path)
    return new_face_encodings, new_face_names

def load_faces(dstroot):
    dstlist = os.listdir(dstroot)
    known_face_encodings = []
    known_face_names = []
    for n in dstlist:
        if n[0] == '.':
            continue
        path_ = os.path.join(dstroot, n)
        dstlist2 = os.listdir(path_)
        for m in dstlist2:
            if m[0] == '.':
                continue
            path_2 = os.path.join(path_, m)
            print(path_2)
            temp_image = face_recognition.load_image_file(path_2)
            try:
                temp_face_encoding = face_recognition.face_encodings(temp_image)[0]
            except:
                print('loadface error!')
                continue
            known_face_encodings.append(temp_face_encoding)
            known_face_names.append(n)
    return known_face_encodings, known_face_names

def get_list_index(org_list, new_list):
    nums_list = []
    cnt = 0
    for n in org_list:
        if n in new_list:
            nums_list.append(cnt)
        cnt = cnt + 1
    return nums_list

def remove_faces(_known_face_encodings, _known_face_names, delfacespath):
    print(len(_known_face_encodings), len(_known_face_names))
    del_name_list = []
    for n in open(delfacespath):
        del_name_list.append(n[:-1])
    print(del_name_list)
    del_num_list = get_list_index(_known_face_names, del_name_list)
    for index_ in del_num_list:
        del _known_face_names[index_]
        del _known_face_encodings[index_]
    return _known_face_encodings, _known_face_names

def find_faces(imgpath, known_face_encodings, known_face_names, updata_faces_root, dstroot, del_facels_root):
    new_face_encodings, new_face_names = updata_faces(updata_faces_root, dstroot)
    if not new_face_names == None:
        for n in new_face_encodings:
            known_face_encodings.append(n)
        for m in new_face_names:
            known_face_names.append(m)
    delfacespath = os.path.join(del_facels_root, 'delfaces.txt')
    if os.path.exists(delfacespath):
        known_face_encodings, known_face_names = remove_faces(known_face_encodings, known_face_names, delfacespath)
        os.remove(delfacespath)
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
    sign = -1
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
    small_frame = cv2.resize(frame,(int(x*3), int(y*3)))

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
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
                    knownpersons.append(person.split('.')[0])
                    knownlocations.append(face_locations[cnt_dst])
                cnt_dst = cnt_dst + 1
            img_resize_k = 3
            knownlocations_out = []
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
    return {'sign':sign, 'names':str(knownpersons), 'locations':knownlocations_out}

def del_name(dstroot, del_faces_root, delname):
    # delete denname file which in dstroot, write delnames in dsel_faces_root/delnames.txt
    dstlist = os.listdir(dstroot)
    del_face_path = os.path.join(dstroot, delname)
    del_face_path_auto = del_face_path + '_auto'
    if not (os.path.exists(del_face_path) or os.path.exists(del_face_path_auto)):
        return -1, dstlist
    else:
        if os.path.exists(del_face_path):
            shutil.rmtree(del_face_path)
        if os.path.exists(del_face_path_auto):
            shutil.rmtree(del_face_path_auto)
        del_faces_path = os.path.join(del_faces_root, 'delfaces.txt')
        with open(del_faces_path, 'a') as f:
            f.write(delname)
            f.write('\n')
            f.write(delname + '_auto')
            f.write('\n')
            f.close()
        return 0, None


# Get a reference to webcam #0 (the default one)
dstroot = './pictures_of_people_i_know3'
known_face_encodings, known_face_names = load_faces(dstroot)

app = Flask(__name__)
imgroot = 'images'
txtroot = 'result'
updata_faces_root = 'updata_faces'
del_faces_root = 'del_faces'

@app.route("/findfaces",methods = ['GET', 'POST'])
def findfaces():
    if request.method == "POST":
        # base64data encode to iamge and save
        imgbase64 = request.form.get('imgbase64')
        imgbase64 = re.sub(r'data:image/[a-zA-Z]*;base64,', "",imgbase64)
        imgbase64 = imgbase64.replace("data:image/jpeg;base64,", "")
        imgdata = base64.b64decode(imgbase64)
        randname = getRandomSet(15)
        imgrandpath = os.path.join(imgroot, randname + '.jpg')
        file = open(imgrandpath,'wb')
        file.write(imgdata)
        file.close()
        print(imgrandpath)
        try:
            str1  = find_faces(imgrandpath, known_face_encodings, known_face_names, updata_faces_root, dstroot, del_faces_root)
        except:
            str1 = {"sign":-1, "names":''}
        return str1
    else:
        return "<h1>Find faces, please use post!</h1>"

@app.route("/upfaces",methods = ['GET', 'POST'])
def upface():
    if request.method == "POST":
        try:
            imgbase64 = request.form.get('imgbase64')
            imgdata = base64.b64decode(imgbase64)
            _name = request.form.get('name')
            name = _name + '.jpg'
            upface_path = os.path.join(updata_faces_root, name)
            file = open(upface_path,'wb')
            file.write(imgdata)
            file.close()
            return {'sign':1}
        except:
            print('>>>upfaces error')
            return {'sign':-1}
    else:
        return "<h1>Updata faces, please use post!</h1>"

@app.route("/delfaces",methods = ['GET', 'POST'])
def delfaces():
    if request.method == "POST":
        delname = request.form.get('delname')
        sign, org_name_list = del_name(dstroot, del_faces_root, delname)
        return {'sign':sign, 'text':org_name_list}
    else:
        return "<h1>Delete faces, please use post!</h1>"

if __name__ == '__main__':
    host = '0.0.0.0'
    port = '8086'
    app.run(debug=True, host=host, port=port)
