from distutils.command.clean import clean
from random import random
from django.http.response import HttpResponse
from importlib.abc import Finder
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from django.shortcuts import render
import pickle
import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime
from PIL import Image

def findEncodings(images):
    encodelist=[]
    for img in images:
        et=face_recognition.face_encodings(img)[0]
        encodelist.append(et)
    return encodelist

# # while True:
# success,img=cap.read()
# im=cv2.resize(img,(0,0),None,0.25,0.25)
# im=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
# faceloc=face_recognition.face_locations(im)[0]
# encodeloc=face_recognition.face_encodings(im,faceloc)[0]

# matches=face_recognition.compare_faces(encodelist,encodeloc)
# facedis=face_recognition.face_distance(encodelist,encodeloc)
# matchIndex=np.argmin(facedis)

# if matches[matchIndex]:
#     name='TARUN'
#     print(name)
#     y1,x2,y2,x1=faceloc
#     y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
#     cv2.rectangle(img,(x1,y1),(x2,y2),(200,0,200),3)
#     cv2.rectangle(img,(x1,y2-35),(x2,y2),(200,0,200),cv2.FILLED)
#     cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)



# cv2.imshow('webcam',img)
# cv2.waitKey(5)
# if cv2.waitKey(1) & 0xFF == ord('q'):
#     break




# cv2.imshow('t1',t1)
# cv2.imshow('t2',t2)

# cv2.waitKey(0)

def cleanup():
    for file in os.walk('static'):
        print(file)

# cleanup()

def homeview(request):
    if request.method=='POST':
        datauri = request.POST["src"]
        name=str(datetime.now())
        path='media/temps/'+name+'.jpg'
        image=open(path,'wb')
        image.write(urlopen(datauri).read())
        image.close()
        boxpath=putbox(name,path)
        os.remove(path)
        return render(request,'box.html',{'name':name+'-boxed.jpg'})

    return render(request,'home.html')

def putbox(name,path):
    t=cv2.imread(path)
    if face_recognition.face_locations(t):
        faceloc=face_recognition.face_locations(t)[0]
        y1,x2,y2,x1=faceloc
        cv2.rectangle(t,(x1,y1),(x2,y2),(200,0,200),3)
        cv2.rectangle(t,(x1,y2-10),(x2,y2),(200,0,200),cv2.FILLED)
        cv2.putText(t,'You',(x1+6,y2-3),cv2.FONT_HERSHEY_COMPLEX,0.4,(255,255,255),2)
    boxpath='static/'+name+'-boxed.jpg'
    cv2.imwrite(boxpath,t)
    enc=face_recognition.face_encodings(t)[0]
    # pick=pickle.dumps(enc)
    # print(enc)
    # print(pick)
    # print(pickle.loads(pick))
    return boxpath
