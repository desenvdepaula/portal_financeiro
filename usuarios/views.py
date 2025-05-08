from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views import View
from django.contrib import messages
from datetime import date, datetime
import json

from .forms import LoginForm
from .models import Usuario

# <-- LOGIN --> #
def request_login(request):
    template = "./usuarios/login.html"
    context = {
        'login_form': LoginForm(request.POST or None) 
    }
    if not request.user.groups.filter(name__in=['Diretoria', 'Financeiro']).exists():
        messages.error(request, "Usuário não Logado ou não tem Permissão para acessar este portal")
    else:
        return redirect("core:home")
    return render(request, template, context)

def validate_groups(grupos):
    groups = []
    for grupo in grupos:
        groups.append(grupo.name)
    
    if 'Diretoria' in groups or 'Financeiro' in groups:
        return True
    else:
        return False

def signin(request):
    if request.POST:
        form = LoginForm(request.POST or None)
        if form.is_valid():
            usr = form.cleaned_data.get('login')
            senha = form.cleaned_data.get('senha')
            usuario = authenticate(request, username=usr, password=senha)
            valid = validate_groups(usuario.groups.all()) if usuario is not None else False
            if usuario is not None and valid:
                login(request, usuario)
                messages.success(request, "Login realizado com successo.")
                return redirect('core:home')
            else:
                messages.error(request, "Credênciais inválidas ou Não Tem Permissão para Acessar este Portal.")
        else:
            template = "./usuarios/login.html"
            context = {
                'login_form': form 
            }
            return render(request, template, context)
    return redirect('request_login')

def signout(request):
    logout(request)
    return redirect('request_login')
