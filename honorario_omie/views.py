from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from datetime import date

from .forms import HonorarioApiOMIEForm

# from .models import RegrasHonorario
            
class HonorarioApiOMIEView(View):

    template = "./honorario_omie/form.html"
    form = HonorarioApiOMIEForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST or None)
        try:
            if form.is_valid():
                return JsonResponse({})
            else:
                raise Exception("Formulário Incorreto !!")
        except Exception as err:
            return JsonResponse({ 'message': str(err) }, status=400)
