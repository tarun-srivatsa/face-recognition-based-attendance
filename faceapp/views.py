from itertools import count
from django.urls import reverse
from distutils.command.clean import clean
from random import random
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from importlib.abc import Finder
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from django.shortcuts import render
import json
import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime
from PIL import Image
from .models import CurrentSession, Section, Student
from .forms import NewSessionForm, StudentForm

norm = np.zeros((300,300))

def fetch_encodings(section):
    studs=Student.objects.filter(section=section)
    json_encs=list(studs.values_list('json_encodings',flat=True))
    encs=[np.array(x) for x in json.loads(json_encs)]
    return encs

def find_encodings(images):
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

def homeview(request):
    return render(request,'home.html')

def facescan(request):
    if request.method=='POST':
        datauri = request.POST["src"]
        name=datetime.now().strftime('%H-%M')
        path='media/temps/'+name+'.jpg'
        image=open(path,'wb')
        image.write(urlopen(datauri).read())
        image.close()
        is1face,boxpath,enc=putbox(name,path)
        os.remove(path)
        if is1face:
            request.session['boxed']=boxpath
            request.session['encoding']=enc.tolist()
            return HttpResponseRedirect(reverse('studentreg'))
        else:
            return render(request,'facescan.html',{'noface':True})

    return render(request,'facescan.html')

def putbox(name,path):
    t=cv2.imread(path)
    t=cv2.normalize(t,norm,0,255,cv2.NORM_MINMAX)
    fls=face_recognition.face_locations(t)
    
    if not fls or len(fls)!=1:
        return False,path,None

    faceloc=fls[0]
    print(type(fls[0]))
    encloc=face_recognition.face_encodings(t,fls,num_jitters=2)[0]
    y1,x2,y2,x1=faceloc
    cv2.rectangle(t,(x1,y1),(x2,y2),(20,255,0),1)
    cv2.rectangle(t,(x1,y2-10),(x2,y2),(20,255,0),cv2.FILLED)
    # cv2.putText(t,'You',(x1+6,y2-3),cv2.FONT_HERSHEY_COMPLEX,0.4,(255,255,255),2)
    boxpath='tempfaces/'+name+'-boxed.jpg'
    cv2.imwrite('static/'+boxpath,t)
    return True,boxpath,encloc

def student_register(request):
    boxpath=request.session['boxed']
    enc=request.session['encoding']
    if request.method=='POST':
        print(boxpath)
        form=StudentForm(request)
        name=request.POST.get('name','')
        usn=request.POST.get('usn','')
        section=Section.objects.get(id=request.POST.get('section',''))
        photo=f'static/faces/{usn}.jpg'
        cv2.imwrite(photo,cv2.imread('static/'+boxpath))
        os.remove('static/'+boxpath)
        # enc=face_recognition.face_encodings(cv2.imread('static/'+boxed))[0]
        jenc=json.dumps(enc)
        stobj=Student(name=name,usn=usn,section=section,photo=photo,json_encoding=jenc)
        stobj.save()
        return HttpResponseRedirect(reverse('home'))

    form=StudentForm()
    return render(request,'box.html',{'form':form,'path':boxpath})

def create_session(request):
    if request.method=='POST':
        form=NewSessionForm(request.POST)
        if form.is_valid():
            class_details=form.cleaned_data.get('class_details')
            countage=form.cleaned_data.get('attendance_countage')
            sesobj=CurrentSession(classdetails=class_details,countage=countage)
            print(sesobj)
            # sesobj.save()
            return HttpResponseRedirect(reverse('home'))
    
    form=NewSessionForm()
    return render(request,'new_session.html',{'form':form,'date':datetime.today})