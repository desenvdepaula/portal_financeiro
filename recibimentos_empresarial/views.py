from django.shortcuts import render
from django.contrib import messages
from django.views import View

from .forms import RecibimentosForm 

from .controller import Controller
from .src.dict import get_dicionario

class RecibimentosView(View):

    template = "utilitarios/recibimentos_empresarial/pagina_de_recibimentos_empresarial.html"
    form = RecibimentosForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        context['contas'] = {}
        dicio_contas = get_dicionario()
        for i in dicio_contas:
            list_contas = [str(key) for key in dicio_contas[i][1].keys()]
            context['contas'][str(i)] = '*'.join(list_contas)
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid() and 'contas' in request.POST:
            context['form'].clean_log(request.user.username)
            try:
                contas = request.POST.getlist('contas')
                controller = Controller(True, True)
                if context['form'].cleaned_data['operacao'] == 'juros':
                    controller.gerarRecebimentosJuros(
                        context['form'].cleaned_data['inicio_periodo'],
                        context['form'].cleaned_data['fim_periodo'],
                        context['form'].cleaned_data['codigo_empresa'],
                        contas
                    )
                else:
                    controller.gerarRecebimentosRecebimentos(
                        context['form'].cleaned_data['inicio_periodo'],
                        context['form'].cleaned_data['fim_periodo'],
                        context['form'].cleaned_data['codigo_empresa'],
                        contas
                    )
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
            else:
                messages.success(request, "Processo Finalizado com Sucesso!!")
        else:
            messages.error(request, "Ocorreu um erro ao executar")


        return render(request, self.template, context)

