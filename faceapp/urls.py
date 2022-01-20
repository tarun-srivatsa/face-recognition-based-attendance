from django.urls import path
from faceapp import views

urlpatterns = [
    path('',views.homeview,name='home'),
    path('facescan/',views.facescan,name='facescan'),
    path('studentreg/',views.student_register,name='studentreg'),
    path('create-session/',views.create_session,name='createsession'),
]