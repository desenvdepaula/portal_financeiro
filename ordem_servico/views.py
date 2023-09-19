from django.shortcuts import render, redirect
from django.http import JsonResponse
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
            ordem.data_cobranca = ordem.data_cobranca.strftime('%d/%m/%Y')
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
                if request.POST.get('id_ordem'):
                    return controller.update_ordem_servico(context['form'].cleaned_data, request.user.username)
                else:
                    controller.update_ordem_servico(context['form'].cleaned_data, request.user.username)
                    messages.success(request, "Cadastrado com sucesso")
                    return redirect('list_ordem_servico') 
            except Exception as ex:
                messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
                raise Exception(ex)
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            return redirect('list_ordem_servico') 
    
    def delete(request):
        try:
            ordem = OrdemServico.objects.get(id=int(request.POST.get('id_ordem')))
            controller = Controller()
            if ordem.ordem_debitada_id:
                controller.delete_ordem_servico_debitada(ordem)
            cd_empresa = ordem.cd_empresa
            text = f"Serviço: {ordem.servico}, Realizado: {ordem.data_realizado}, Executado: {ordem.executado}, Quantidade: {ordem.quantidade}, Valor: {ordem.valor}"
            ordem.delete()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            request_project_log(cd_empresa, text, "ORDEM DE SERVIÇO / DELETAR ORDEM", request.user.username)
            return JsonResponse({'msg': 'correto'})
        
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
        
    def request_debitar_ordem_servico(request, id_ordem):
        try:
            controller = Controller()
            controller.debitar_or_delete_ordem_servico(id_ordem, request.GET.get('debitar') == 'True')
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
            
    def request_arquivar_ordem_servico(request, id_ordem):
        try:
            controller = Controller()
            controller.debitar_or_delete_ordem_servico(id_ordem, False, arquivar=request.GET.get('arquivar') == 'True')
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)

    def request_download_planilha(request):
        try:
            controller = Controller()
            return controller.gerarPlanilhasOrdens(request.POST)
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
        return redirect('list_ordem_servico')