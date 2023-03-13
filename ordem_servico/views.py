from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views import View

from .forms import OrdemServicoForm

from .lib.controller import Controller
from .models import OrdemServico
from .lib.database import ManagerTareffa
from core.views import request_project_log
    
class OrdemServicoView(View):
    
    template = "ordem_servico/index.html"
    form = OrdemServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        context['ordens'] = OrdemServico.objects.all()
        for ordem in context['ordens']:
            ordem.data_realizado = ordem.data_realizado.strftime('%d/%m/%Y')
            preco = float(ordem.valor)
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem.valor = preco_final
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            context['form'].clean_log(request.user.username)
            try:
                controller = Controller()
                controller.update_ordem_servico(context['form'].cleaned_data)
            except Exception as ex:
                messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
            else:
                messages.success(request, "Alterado com sucesso")
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            
        return redirect('list_ordem_servico')
    
    def delete(request):
        try:
            ordem = OrdemServico.objects.get(id=int(request.POST.get('id_ordem')))
            text = f"Serviço: {ordem.servico}, Realizado: {ordem.data_realizado}, Executado: {ordem.executado}, Quantidade: {ordem.quantidade}, Valor: {ordem.valor}"
            ordem.delete()
            request_project_log(ordem.cd_empresa, text, "ORDEM DE SERVIÇO / DELETAR ORDEM", request.user.username)
            return JsonResponse({'msg': 'correto'})
        except Exception as err:
            raise Exception(err)
        
    def buscar_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=id_ordem)
            ordem = vars(ordem)
            del ordem['_state']
            ordem['data_cobranca'] = ordem['data_cobranca'].strftime('%d/%m/%Y')
            ordem['data_realizado'] = ordem['data_realizado'].strftime('%d/%m/%Y')
            preco = float(ordem['valor'])
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem['valor'] = preco_final
            return JsonResponse(ordem)
        except Exception as err:
            raise Exception(err)

    def request_download_planilha(request):
        try:
            controller = Controller()
            return controller.gerarPlanilhasOrdens()
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
        return redirect('regras_honorario_131')