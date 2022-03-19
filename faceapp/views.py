from django.urls import reverse
from django.http.response import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
import json
import cv2
import numpy as np
import os
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import FormView
from .models import Class, CurrentSession, Present, Section, Student
from .forms import NewSessionForm, StudentForm
from .utilities import face_scan,face_recognise

class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return self.form_invalid(form)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

def homeview(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.GET.get('close',''):
        session=CurrentSession.objects.get(id=request.GET.get('close',''))
        session.is_active=False
        session.save()
        return HttpResponseRedirect(reverse('home'))
        
    if request.POST.get('active',''):
        request.session['session_id']=request.POST.get('active','')
        return HttpResponseRedirect(reverse('activesession'))

    if request.POST.get('class',''):
        request.session['class_id']=request.POST.get('class','')
        return HttpResponseRedirect(reverse('showclass'))

    open_sessions=CurrentSession.objects.filter(is_active=True).order_by('-id')
    classes=Class.objects.all().order_by('course_code')
    return render(request,'home.html',{'open_sessions':open_sessions,'classes':classes})

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
        similar_face=face_recognise(np.array(enc),None)
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
            # session_id=sesobj.pk
            # request.session['session_id']=session_id
            return HttpResponseRedirect(reverse('home'))
    else:
        form=NewSessionForm()
    return render(request,'new_session.html',{'form':form,'date':date.today})

def attendance_scan(request):
    if request.GET.get('yesstudent',''):
        stud=request.GET.get('yesstudent','')
        stud=Student.objects.get(usn=request.GET.get('yesstudent',''))
        session=CurrentSession.objects.get(id=request.session['session_id'])
        pobj=Present(student=stud,session=session)
        pobj.save()
        return HttpResponseRedirect(reverse('attendancescan'))

    if request.GET.get('nostudent',''):
        return attendance_assist(request,request.GET.get('nostudent',''))

    return attendance_assist(request,None)

def attendance_assist(request,not_this):
    session=CurrentSession.objects.get(id=request.session['session_id'])
    section=session.classdetails.section
    context={'session':session}
    if request.method=='POST':
        is1face,boxpath,enc=face_scan(request)
        if is1face:
            usn=face_recognise(enc,section)
            if not_this:
                context['not_this_done']=True
                if usn==not_this:
                    context['not_this_done']=f'This is {usn} as per the database, if not, please contact the Admin to get the details changed'
            if not usn:
                context['message']='Unknown Face. Please Scan Again'
                return render(request,'facescan.html',context)
            if already_present(usn,session):
                context['already_present']=True
            student=Student.objects.get(usn=usn)
            context.update(student=student,path=boxpath)
            return render(request,'box.html',context)
        else:
            context['message']='No face/Multiple faced detected. Please Scan Again.'
            return render(request,'facescan.html',context)

    return render(request,'facescan.html',context)

def already_present(usn,session):
    stud=Student.objects.get(usn=usn)
    if Present.objects.filter(student=stud,session=session).exists():
        return True
    else:
        return False

def active_session(request):
    session=CurrentSession.objects.get(id=request.session['session_id'])
    presents=Present.objects.filter(session=session).order_by('student')
    a_list=[Student.objects.get(usn=a) for a in get_absent(session,presents)]
    context={'session':session,'presents':presents,'a_list':a_list}
    return render(request,'active_session.html',context)

def get_absent(session,presents):
    p_list=[]
    for p in presents:
        p_list.append(p.student.usn)
    a_list=[]
    full_list=Student.objects.filter(section=session.classdetails.section).order_by('usn').values_list('usn',flat=True)
    for s in full_list:
        if s not in p_list:
            a_list.append(s)

    return a_list

def show_class(request):
    this_class=Class.objects.get(id=request.session['class_id'])
    stud_list=Student.objects.filter(section=this_class.section).order_by('usn')
    session_count,stud_counts=zipcounts(this_class,stud_list)
    context={'class':this_class,'students':stud_list,
        'total':session_count,'stud_counts':stud_counts}
    return render(request,'show_class.html',context)

def zipcounts(class0,stud_list):
    session_list=CurrentSession.objects.filter(classdetails=class0,is_active=0)
    session_count=session_list.count()
    present_counts={}
    for stud in stud_list:
        present_counts[stud.usn]=0

    for session in session_list:
        presents=Present.objects.filter(session=session)
        for p in presents:
            present_counts[p.student.usn]+=1

    counts=[]
    percs=[]
    for stud in stud_list:
        counts.append(present_counts[stud.usn])
        if session_count > 0:
            percs.append(present_counts[stud.usn]*100/session_count)
        else:
            percs.append(0)

    return session_list.count,zip(stud_list,counts,percs)
 