from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.template import engines
from django.http import JsonResponse

from .lib.controller import Controller
from .models import ClassificacaoServicos
from .forms import RelatorioFaturamentoServicoForm

class ClassificacoesServicos(View):
    template_form = "./relatorios/classificacoes/form.html"
    
    def get(self, request):
        context={}
        context['classificacoes'] = ClassificacaoServicos.objects.all()
        return render(request, self.template_form, context)
        
    def create_classificacao(request):
        try:
            obj = ClassificacaoServicos.objects.create(
                classificacao = request.POST.get('classificacao_value')
            )
        except Exception as err:
            return JsonResponse({'msg': str(err)}, status=401)
        else:
            return JsonResponse({'status': 200, 'obj': {'id': obj.id, 'classificacao': obj.classificacao}}, status=200)
        
    def edit_classificacao(request):
        try:
            obj = ClassificacaoServicos.objects.get(id=request.POST.get('id_classificacao'))
            obj.classificacao = request.POST.get('classificacao_value')
            obj.save()
        except Exception as err:
            return JsonResponse({'msg': str(err)}, status=401)
        else:
            return JsonResponse({'status': 200, 'obj': {'id': obj.id, 'classificacao': obj.classificacao}}, status=200)
        
    def delete_classificacao(request):
        try:
            ClassificacaoServicos.objects.get(id=request.POST.get('id_classificacao')).delete()
        except Exception as err:
            return JsonResponse({'msg': str(err)}, status=401)
        else:
            return JsonResponse({'status': 200}, status=200)
    
class RelatorioFaturamentoServico(View):
    template_form = "./relatorios/relatorio_faturamento/form.html"
    
    def get(self, request):
        controller = Controller()
        context={}
        context['servicos'] = controller.get_dados_servicos()
        context['classificacoes'] = ClassificacaoServicos.objects.all()
        return render(request, self.template_form, context)
    
    def post(self, request):
        try:
            controller = Controller()
            codigos_servicos = set()
            valid_dados = RelatorioFaturamentoServicoForm(kwargs=request.POST)
            inicio, fim = valid_dados.valid_datas()
            classificacoes = valid_dados.valid_classificacoes()
            servicos = valid_dados.valid_servicos()
            for i in classificacoes+servicos:
                codigos_servicos.add(i)
                
            return controller.build_planilha_faturamento_servico(inicio, fim, codigos_servicos)
        except Exception as err:
            messages.error(request, err)
        return redirect('request_relatorio_faturamento')