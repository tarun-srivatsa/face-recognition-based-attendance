from urllib.request import urlopen
import cv2
import numpy as np
import os
import json
import face_recognition
from datetime import datetime

from .models import Student

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
    datauri = request.POST.get('src','')
    name=datetime.now().strftime('%H-%M-%S')
    path='media/temps/'+name+'.jpg'
    image=open(path,'wb')
    image.write(urlopen(datauri).read())
    image.close()
    r1,r2,r3=putbox(name,path)
    os.remove(path)
    return r1,r2,r3

def face_recognise(enc,section):
    usnlist,enclist=fetch_encodings(section)
    if not enclist:
        return None
    facedistances=face_recognition.face_distance(enclist,enc)
    matchindex=np.argmin(facedistances)
    if not section:
        if facedistances[matchindex]<0.35:
            return usnlist[matchindex]
        else:
            return None

    if facedistances[matchindex]>0.5:
        return None

    print(usnlist,facedistances)
    return usnlist[matchindex]
