from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from datetime import date
import pandas as pd

from .forms import HonorarioApiOMIEForm
from .models import HonorarioOMIEFaturadas
from .controller import gerar_arquivo_excel_auditoria_debitos
            
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
