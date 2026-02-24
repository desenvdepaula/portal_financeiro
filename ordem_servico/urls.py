from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import OrdemServicoView, ServicosView, Departamento, EmpresasOmieView, OrdensProvisoriasView

urlpatterns = [
    path('list_ordens_provisorias', login_required(OrdensProvisoriasView.as_view()), name="list_ordens_provisorias"),
    path('delete_ordem_servico_provisoria', OrdensProvisoriasView.delete_provisoria, name="delete_ordem_servico_provisoria"),
    path('arquivar_ordem_servico_provisoria/<int:id_ordem>/', OrdensProvisoriasView.request_arquivar_ordem_servico_provisoria),
    path('buscar_ordem_servico_provisoria/<int:id_ordem>/', OrdensProvisoriasView.buscar_ordem_servico_provisoria),
    path('criar_os_real/<int:id_ordem>/', OrdensProvisoriasView.criar_os_real),
    
    path('servicos_os/', login_required(OrdemServicoView.request_get_services_escritorio), name="servicos_os"),
    path('list_ordem_servico', login_required(OrdemServicoView.as_view()), name="list_ordem_servico"),
    path('debitar_em_lote', login_required(OrdemServicoView.debitar_em_lote), name="debitar_em_lote"),
    path('delete_ordem_servico', OrdemServicoView.delete, name="delete_ordem_servico"),
    path('buscar_ordem_servico/<int:id_ordem>/', OrdemServicoView.buscar_ordem_servico),
    path('debitar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_debitar_ordem_servico),
    path('aprovar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_aprovar_ordem_servico),
    path('arquivar_ordem_servico/<int:id_ordem>/', OrdemServicoView.request_arquivar_ordem_servico),
    path('download_boletos_escritorio/', OrdemServicoView.request_download_boletos_escritorio, name="download_boletos_escritorio"),
    path('baixar_planilha_ordens_servico', OrdemServicoView.request_download_planilha, name="baixar_planilha_ordens_servico"),
    path('baixar_boletos_os/<str:escritorio>/', OrdemServicoView.request_download_pdfs_boletos),
    path('verificar_boletos_escrit/<str:escritorio>/', OrdemServicoView.verify_pdf_os),
    path('status_task_os/<str:task_id>/', OrdemServicoView.status_task),
    
    path('list_empresas_omie', login_required(EmpresasOmieView.as_view()), name="list_empresas_omie"),
    
    path('controle_servicos_OS', login_required(ServicosView.as_view()), name="controle_servicos_OS"),
    path('buscar_servico/<int:nr_servico>/', ServicosView.buscar_servico),
    path('delete_servico_OS', ServicosView.delete_service, name="delete_servico_OS"),
    
    path('create_department', Departamento.create, name="create_department"),
    path('update_department', Departamento.update, name="update_department"),
    path('delete_department', Departamento.delete, name="delete_department"),
    
    path('dowload_relatorio_servicos_classificacoes', login_required(ServicosView.dowload_relatorio_servicos_classificacoes), name="dowload_relatorio_servicos_classificacoes"),
]