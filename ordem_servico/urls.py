from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import OrdemServicoView, ServicosView, Departamento

urlpatterns = [
    path('list_ordem_servico', login_required(OrdemServicoView.as_view()), name="list_ordem_servico"),
    path('debitar_em_lote', login_required(OrdemServicoView.debitar_em_lote), name="debitar_em_lote"),
    path('delete_ordem_servico', OrdemServicoView.delete, name="delete_ordem_servico"),
    path('buscar_ordem_servico/<int:id_ordem>/', OrdemServicoView.buscar_ordem_servico),
    path('debitar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_debitar_ordem_servico),
    path('arquivar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_arquivar_ordem_servico),
    path('baixar_planilha_ordens_servico', OrdemServicoView.request_download_planilha, name="baixar_planilha_ordens_servico"),
    
    path('controle_servicos_OS', login_required(ServicosView.as_view()), name="controle_servicos_OS"),
    path('buscar_servico/<int:nr_servico>/', ServicosView.buscar_servico),
    path('delete_servico_OS', ServicosView.delete_service, name="delete_servico_OS"),
    
    path('create_department', Departamento.create, name="create_department"),
    path('update_department', Departamento.update, name="update_department"),
    path('delete_department', Departamento.delete, name="delete_department"),
    
    path('dowload_relatorio_servicos_classificacoes', login_required(ServicosView.dowload_relatorio_servicos_classificacoes), name="dowload_relatorio_servicos_classificacoes"),
]