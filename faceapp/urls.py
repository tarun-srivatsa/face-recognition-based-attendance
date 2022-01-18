from django.urls import path
from faceapp import views

urlpatterns = [
    path('',views.homeview,name='home'),
]