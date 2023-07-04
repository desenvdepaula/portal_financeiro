from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import InadimplentesView, ContratoHonorarioView

urlpatterns = [
    path('inadimplentes', login_required(InadimplentesView.as_view()), name="inadimplentes"),
    path('export_inadimplentes', login_required(InadimplentesView.export_relatorio_inadimplentes), name="export_inadimplentes"),
    path('contrato_honorario', login_required(ContratoHonorarioView.as_view()), name="request_contrato_honorario"),
]