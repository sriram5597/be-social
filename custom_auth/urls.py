from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.SignupUserView.as_view(), name='signup-user'),
    path('login', views.LoginUserView.as_view(), name='login-user')
]
