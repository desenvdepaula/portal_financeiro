from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import home, erro404

app_name = 'core'
urlpatterns = [
    path('', login_required(home), name='home'),
    path('erro404/', login_required(erro404), name='erro404')
]