from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from datetime import date
import pandas as pd

from .forms import HonorarioApiOMIEForm
from .models import HonorarioOMIEFaturadas
from .controller import gerar_arquivo_excel_auditoria_debitos, AnaliseRelatorio
            
class HonorarioApiOMIEView(View):

    template = "./honorario_omie/form.html"
    form = HonorarioApiOMIEForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        response_data = {}
        # form = self.form(request.POST or None)
        try:
            # if form.is_valid():
            #     return JsonResponse({})
            # else:
            #     raise Exception("Formulário Incorreto !!")
            if request.POST.get("rotas") == 'faturamentos':
                df_db = pd.DataFrame(HonorarioOMIEFaturadas.objects.values())
                response_data['auditoria'] = gerar_arquivo_excel_auditoria_debitos(df_db)
            else:
                raise Exception("Apenas Relatório de Faturamentos")
            return JsonResponse(response_data)
        except Exception as err:
            return JsonResponse({ 'message': str(err) }, status=400)
        
    def gerar_analise_relatorio(request):
        response_data = {}
        try:
            file_api = request.FILES.get("file_api").temporary_file_path() if "file_api" in request.FILES else None
            file_omie = request.FILES.get("file_omie").temporary_file_path() if "file_omie" in request.FILES else None
            if not file_api or not file_omie:
                raise Exception("Erro no Formulário, passe os Arquivos corretamente e em XLSX !!")
            analise = AnaliseRelatorio(file_api, file_omie)
            response_data['auditoria'] = analise.gerar_analise_relatorio()
            return JsonResponse(response_data)
        except Exception as err:
            return JsonResponse({ 'message': str(err) }, status=400)
