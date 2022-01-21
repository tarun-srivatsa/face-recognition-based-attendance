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
from .models import Class, CurrentSession, Present, Section, Student
from .forms import NewSessionForm, StudentForm

norm = np.zeros((500,500))

def fetch_encodings(section):
    if not section:
        studs=Student.objects.all()
    else:
        studs=Student.objects.filter(section=section)
    usns=list(studs.order_by('usn').values_list('usn',flat=True))
    json_encs=list(studs.order_by('usn').values_list('json_encoding',flat=True))
    encs=[np.array(json.loads(x)) for x in json_encs]
    return usns,encs

# im=cv2.resize(img,(0,0),None,0.25,0.25)
# if matches[matchIndex]:
#     name='TARUN'
#     print(name)
#     y1,x2,y2,x1=faceloc
#     y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
#     cv2.rectangle(img,(x1,y1),(x2,y2),(200,0,200),3)
#     cv2.rectangle(img,(x1,y2-35),(x2,y2),(200,0,200),cv2.FILLED)
#     cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
# def cleanup():
#     for file in os.walk('static'):
#         print(file)

def homeview(request):
    return render(request,'home.html')

def register_scan(request):
    if request.method=='POST':
        is1face,boxpath,enc=face_scan(request)
        if is1face:
            request.session['boxed']=boxpath
            request.session['encoding']=enc.tolist()
            return HttpResponseRedirect(reverse('studentregister'))
        else:
            return render(request,'facescan.html',{'message':'No face/Multiple faced detected\nPlease Scan Again.'})

    return render(request,'facescan.html')

def student_register(request):
    boxpath=request.session['boxed']
    enc=request.session['encoding']
    context={'path':boxpath}
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
        similar_face=face_recognise(np.array(enc),None,None)
        if similar_face:
            context['similar_face']=Student.objects.get(usn=similar_face)
    context['regform']=form
    return render(request,'box.html',context)

def create_session(request):
    if request.method=='POST':
        form=NewSessionForm(request.POST)
        if form.is_valid():
            class_details=form.cleaned_data.get('class_details')
            countage=form.cleaned_data.get('attendance_countage')
            sesobj=CurrentSession(classdetails=class_details,countage=countage)
            sesobj.save()
            session_id=sesobj.pk
            request.session['session_id']=session_id
            return HttpResponseRedirect(reverse('attendancescan'))
    else:
        form=NewSessionForm()
    return render(request,'new_session.html',{'form':form,'date':date.today})

def attendance_scan(request):
    if request.GET.get('yesstudent',''):
        pass
    if request.GET.get('nostudent',''):
        return attendance_assist(request,request.GET.get('nostudent',''))

    return attendance_assist(request,None)

def attendance_assist(request,not_this):
    session_id=request.session['session_id']
    session=CurrentSession.objects.get(id=session_id)
    section=session.classdetails.section
    context={'session':session}
    if request.method=='POST':
        is1face,boxpath,enc=face_scan(request)
        if is1face:
            usn=face_recognise(enc,section,not_this)
            if not usn:
                context['message']='Unknown Face. Please Scan Again'
                return render(request,'facescan.html',context)
            student=Student.objects.get(usn=usn)
            context.update(student=student,path=boxpath)
            return render(request,'box.html',context)
        else:
            context['message']='No face/Multiple faced detected. Please Scan Again.'
            return render(request,'facescan.html',context)

    return render(request,'facescan.html',context)

def face_recognise(enc,section,not_this):
    usnlist,enclist=fetch_encodings(section)
    facedistances=face_recognition.face_distance(enclist,enc)
    print(usnlist,facedistances)
    matchindex=np.argmin(facedistances)

    if not section:
        if facedistances[matchindex]<0.3:
            return usnlist[matchindex]
        else:
            return None

    if facedistances[matchindex]>0.5:
        return None

    if not_this and usnlist[matchindex]==not_this:
        del enclist[matchindex]
        del usnlist[matchindex]
        matchindex=np.argmin(facedistances)

    return usnlist[matchindex]

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
    boxpath='tempfaces/'+name+'-boxed.jpg'
    cv2.imwrite('static/'+boxpath,t)
    return True,boxpath,encloc

def face_scan(request):
    datauri = request.POST["src"]
    name=datetime.now().strftime('%H-%M')
    path='media/temps/'+name+'.jpg'
    image=open(path,'wb')
    image.write(urlopen(datauri).read())
    image.close()
    r1,r2,r3=putbox(name,path)
    os.remove(path)
    return r1,r2,r3

def active_sessions(request):
    if request.method=='POST':
        session_id=request.POST.get('session','')
        request.session['session_id']=session_id
        return HttpResponseRedirect(reverse('attendancescan'))

    session_list=CurrentSession.objects.all()
    return render(request,'active_sessions.html',{'sessions':session_list})