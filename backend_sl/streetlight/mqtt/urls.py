from django.urls import path
from .views import *  
from django.contrib.auth import views as auth_views
from . import views
app_name = "api"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    
    # path('publish_cmd/<str:mac>/', views.publish_cmd, name='publish_cmd'),
    # path('subscribe/', views.subscribe, name='subscribe'),
    ]


 
 