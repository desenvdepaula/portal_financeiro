from django.urls import path, include

from .views import request_login, signin, signout

urlpatterns = [
    path('logout/', signout, name="logout"),
    path('login/', request_login, name="request_login"),
    path('login/submit/', signin, name="login"),
]