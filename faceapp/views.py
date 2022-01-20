from django.urls import reverse
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from urllib.request import urlopen
from django.shortcuts import render
import json
import cv2
import numpy as np
import os
import face_recognition
from datetime import datetime,date
from .models import CurrentSession, Present, Section, Student
from .forms import NewSessionForm, StudentForm

norm = np.zeros((300,300))

def fetch_encodings(section):
    studs=Student.objects.filter(section=section)
    usns=list(studs.values_list('usn',flat=True))
    # print(names)
    json_encs=list(studs.values_list('json_encoding',flat=True))
    encs=[np.array(json.loads(x)) for x in json_encs]
    return usns,encs

current_encodings={}
active_session=CurrentSession.objects.all()[0]
# sessions=CurrentSession.objects.filter(is_active=True)
# for s in sessions:
#     sect=s.class_details.section
#     current_encodings[sect]=fetch_encodings(sect)

# im=cv2.resize(img,(0,0),None,0.25,0.25)
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

def cleanup():
    for file in os.walk('static'):
        print(file)

def homeview(request):
    return render(request,'home.html')

def facescan(request):
    if request.GET['studentpresent']:
        presobj=Present(session=active_session,student=Student.objects.get(usn=request.GET['studentpresent']))
        # presobj.save()
        print(presobj)

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
            return render(request,'facescan.html',{'message':'No face/Multiple faced detected\nPlease Scan Again.'})

    return render(request,'facescan.html')

def putbox(name,path):
    t=cv2.imread(path)
    t=cv2.normalize(t,norm,0,255,cv2.NORM_MINMAX)
    fls=face_recognition.face_locations(t)
    
    if not fls or len(fls)!=1:
        return False,path,None

    faceloc=fls[0]
    encloc=face_recognition.face_encodings(t,fls,num_jitters=2)[0]
    y1,x2,y2,x1=faceloc
    cv2.rectangle(t,(x1,y1),(x2,y2),(20,255,0),1)
    cv2.rectangle(t,(x1,y2-10),(x2,y2),(20,255,0),cv2.FILLED)
    boxpath='tempfaces/'+name+'-boxed.jpg'
    cv2.imwrite('static/'+boxpath,t)
    return True,boxpath,encloc

def student_register(request):
    boxpath=request.session['boxed']
    enc=request.session['encoding']
    if request.method=='POST':
        form=StudentForm(request.POST)
        if form.is_valid():
            name=request.POST.get('name','')
            usn=request.POST.get('usn','')
            section=Section.objects.get(id=request.POST.get('section',''))
            photo=f'static/faces/{usn}.jpg'
            cv2.imwrite(photo,cv2.imread('static/'+boxpath))
            os.remove('static/'+boxpath)
            jenc=json.dumps(enc)
            stobj=Student(name=name,usn=usn,section=section,photo=photo,json_encoding=jenc)
            stobj.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form=StudentForm()
    return render(request,'box.html',{'regform':form,'path':boxpath})

def create_session(request):
    if request.method=='POST':
        form=NewSessionForm(request.POST)
        if form.is_valid():
            class_details=form.cleaned_data.get('class_details')
            countage=form.cleaned_data.get('attendance_countage')
            sesobj=CurrentSession(classdetails=class_details,countage=countage)
            section=class_details.section
            # ziplist=fetch_encodings(section)
            # current_encodings[str(section)]=ziplist
            active_session=sesobj
            active_session=sesobj
            sesobj.save()
            return HttpResponseRedirect(reverse('attendancescan'))
    else:
        form=NewSessionForm()
    return render(request,'new_session.html',{'form':form,'date':date.today})

# def run_attendance(request):

# def face_recognise()

def attendance_scan(request):
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
            usnlist,enclist=fetch_encodings(active_session.classdetails.section)
            facedistances=face_recognition.face_distance(enclist,enc)
            matchindex=np.argmin(facedistances)
            print(facedistances)
            name=Student.objects.get(usn=usnlist[matchindex]).name
            return render(request,'box.html',{'predicted':name,'usn':usnlist[matchindex],'path':boxpath})
        else:
            return render(request,'facescan.html',{'message':'No face/Multiple faced detected\nPlease Scan Again.'})

    return render(request,'facescan.html')
