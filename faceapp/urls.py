from django.urls import path
from faceapp import views

urlpatterns = [
    path('',views.homeview,name='home'),
    path('register-scan/',views.register_scan,name='registerscan'),
    path('studentreg/',views.student_register,name='studentregister'),
    path('create-session/',views.create_session,name='createsession'),
    path('attendance-scan/',views.attendance_scan,name='attendancescan'),
    path('active-sessions/',views.active_sessions,name='activesessions'),
]