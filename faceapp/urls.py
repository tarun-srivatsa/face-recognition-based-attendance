from django.urls import path
from faceapp import views

urlpatterns = [
    path('',views.homeview,name='home'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('register-scan/',views.register_scan,name='registerscan'),
    path('studentreg/',views.student_register,name='studentregister'),
    path('create-session/',views.create_session,name='createsession'),
    path('attendance-scan/',views.attendance_scan,name='attendancescan'),
    path('active-session/',views.active_session,name='activesession'),
    path('show_class/',views.show_class,name='showclass'),
]