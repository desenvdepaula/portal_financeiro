from django.shortcuts import render
from django.contrib import messages
from django.views import View

from .forms import RecibimentosForm 

from .controller import Controller

class RecibimentosView(View):

    template = "utilitarios/recibimentos_empresarial/pagina_de_recibimentos_empresarial.html"
    form = RecibimentosForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            context['form'].clean_log(request.user.username)
            try:
                controller = Controller(True, True)
                if context['form'].cleaned_data['operacao'] == 'juros':
                    controller.gerarRecebimentosJuros(
                        context['form'].cleaned_data['inicio_periodo'],
                        context['form'].cleaned_data['fim_periodo'],
                        context['form'].cleaned_data['codigo_empresa'],
                    )
                else:
                    controller.gerarRecebimentosRecebimentos(
                        context['form'].cleaned_data['inicio_periodo'],
                        context['form'].cleaned_data['fim_periodo'],
                        context['form'].cleaned_data['codigo_empresa'],
                    )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
            else:
                messages.success(request, "Processo Finalizado com Sucesso!!")
        else:
            messages.error(request, "Ocorreu um erro ao executar")


        return render(request, self.template, context)

