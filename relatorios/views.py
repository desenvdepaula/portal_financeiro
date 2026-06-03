from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from .models import ClassificacaoServicos

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