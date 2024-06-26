from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import RelatorioFaturamentoServico, ClassificacoesServicos

urlpatterns = [
    path('relatorio_faturamento', login_required(RelatorioFaturamentoServico.as_view()), name="request_relatorio_faturamento"),
    path('classificacao_servicos', login_required(ClassificacoesServicos.as_view()), name="request_classificacao_servicos"),

    path('classificacao_servicos/create', ClassificacoesServicos.create_classificacao, name="request_create_classificacao"),
    path('classificacao_servicos/edit', ClassificacoesServicos.edit_classificacao, name="request_edit_classificacao"),
    path('classificacao_servicos/delete', ClassificacoesServicos.delete_classificacao, name="request_delete_classificacao"),
]