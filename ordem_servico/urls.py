from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import OrdemServicoView

urlpatterns = [
    path('list_ordem_servico', login_required(OrdemServicoView.as_view()), name="list_ordem_servico"),
    path('delete_ordem_servico', OrdemServicoView.delete, name="delete_ordem_servico"),
    path('buscar_ordem_servico/<int:id_ordem>/', OrdemServicoView.buscar_ordem_servico),
    path('debitar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_debitar_ordem_servico),
    path('arquivar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_arquivar_ordem_servico),
    path('baixar_planilha_ordens_servico', OrdemServicoView.request_download_planilha, name="baixar_planilha_ordens_servico"),
]