from django.urls import path
from .views import *  
from django.contrib.auth import views as auth_views
from . import views
from .views import UserUpdateAPIView
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
app_name = "accounts"
 
# app_name will help us do a reverse look-up latter.
urlpatterns = [
    # path('login/',loginAPI.as_view()),
    path('login/', loginAPI, name='login'),
    path('logout/',logoutapi,name='logout'),
    path('createuser/' ,UserCreate.as_view()),
    path('delete/<str:email>/', delete_user, name='delete'),
    # path('update/', update_user, name='update'),
    path('update-user/', UserUpdateAPIView.as_view(), name='update-user'),

    path('password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
]