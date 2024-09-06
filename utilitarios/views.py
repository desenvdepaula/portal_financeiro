from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from datetime import date, datetime
import os
from django.conf import settings

from .forms import EmissaoNFManualForm, BoletosForm, NotasAntecipadasForm, EmissaoNFForm
from .lib.controller import Controller

def request_notas_antecipadas(request):
    template = "./utilitarios/notas_antecipadas/form.html"
    context = { 'form': NotasAntecipadasForm(request.POST or None) }

    if request.POST:
        if context['form'].is_valid():
            notas = [int(nota) for nota in request.POST.getlist('cod_nota')]
            context['form'].clean_log(request.user.username, notas)
            try:
                controller = Controller()
                controller.lancar_nota_antecipada(
                    context['form'].cleaned_data['escritorio_origem'],
                    context['form'].cleaned_data['escritorio_destino'],
                    notas,
                    request.user.cd_questor
                )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
            else:
                messages.success(request, "Finalizado com Sucesso!!")
        else:
            messages.error(request, "Ocorreu um erro no Formulário, preencha corretamente !")

    return render(request, template, context)

class EmissaoNF(View):
    template_form = "./utilitarios/emissao_nf_retorno/form.html"
    form_class = EmissaoNFForm
    
    def get(self, request, *args, **kwargs):
        context = {}
        context['form'] = self.form_class()
        return render(request, self.template_form, context)

    def post(self, request, *args, **kwargs):
        context = {'form': self.form_class(request.POST or None, request.FILES or None)}

        if context['form'].is_valid():
            context['form'].clean_log(request.user.username)
            try:
                controller = Controller()
                return controller.gerar_emissao_NF(
                    context['form'].cleaned_data['empresas'],
                    context['form'].cleaned_data['data'].strftime('%d.%m.%Y'),
                )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
        else:
            messages.error(request, "Ocorreu um erro ao executar, Algo no Formulário não esta correto Correto!!")
        return render(request, self.template_form, context)

class Boletos(View):
    template_form = "./utilitarios/boletos/boletos.html"
    form_class = BoletosForm
    
    def get(self, request, *args, **kwargs):
        context = {}
        context['form'] = self.form_class()
        return render(request, self.template_form, context)

    def post(self, request, *args, **kwargs):
        context = {'form': self.form_class(request.POST or None, request.FILES or None)}

        if context['form'].is_valid():
            context['form'].clean_log(request.user.username)
            try:
                controller = Controller()
                return controller.getPdfs(
                    context['form'].cleaned_data['path'],
                    context['form'].cleaned_data['data'],
                    context['form'].cleaned_data['filename']
                )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
        else:
            messages.error(request, "Ocorreu um erro ao executar, O arquivo não é um .PDF, Escolha o Arquivo Correto!!")
        return render(request, self.template_form, context)

class EmissaoNFManual(View):
    template_form = "./utilitarios/emissao_nf_manual/form.html"
    form_class = EmissaoNFManualForm
    
    def get(self, request, *args, **kwargs):
        context = {}
        context['form'] = self.form_class()
        return render(request, self.template_form, context)

    def post(self, request, *args, **kwargs):
        context = {'form': self.form_class(request.POST or None)}

        if context['form'].is_valid():
            try:
                controller = Controller()
                return controller.gerar_emissao_NF_Manual(
                    context['form'].clean_empresas( request.POST.getlist('empresas'), request.user.username ),
                    context['form'].cleaned_data['acoes'],
                    context['form'].cleaned_data['data'].strftime('%d.%m.%Y'),
                )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
        else:
            messages.error(request, "Ocorreu um erro ao executar por lagum motivo ai!!")
        return render(request, self.template_form, context)
