from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import HonorarioApiOMIEView

urlpatterns = [
    path('honorario_api_omie/', login_required(HonorarioApiOMIEView.as_view()), name="honorario_api_omie"),
    path('gerar_analise_relatorios_omie/', login_required(HonorarioApiOMIEView.gerar_analise_relatorio), name="gerar_analise_relatorios_omie"),
]