from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from datetime import date, datetime
import os

from .forms import EmissaoNFManualForm
from .lib.controller import Controller

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
            finally:
                self.excluirArquivos()
        else:
            messages.error(request, "Ocorreu um erro ao executar por lagum motivo ai!!")
        return render(request, self.template_form, context)

    def excluirArquivos(self):
        try:
            for file in os.listdir('temp/files/emissao_nf_manual/'):
                if not ".py" in file:
                    os.remove(f'temp/files/emissao_nf_manual/{file}')
        except OSError as e:
            print(f"Error:{ e }")
