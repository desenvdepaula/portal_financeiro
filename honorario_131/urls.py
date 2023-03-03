from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import RelatorioHonorarioView, RegrasHonorarioView, request_realizar_calculo_honorario_131, request_realizar_auditoria_honorario_131

urlpatterns = [
    path('realizar_calculo_honorario_131', login_required(request_realizar_calculo_honorario_131), name="realizar_calculo_honorario_131"),
    path('realizar_auditoria_honorario_131', login_required(request_realizar_auditoria_honorario_131), name="realizar_auditoria_honorario_131"),
    path('regras_131', login_required(RegrasHonorarioView.as_view()), name="regras_honorario_131"),
    path('relatorioHonorario_131/', login_required(RelatorioHonorarioView.as_view()), name="relatorioHonorario_131"),
    path('buscar_empresa_honorario/<int:cd_empresa>/', login_required(RegrasHonorarioView.buscar_empresa)),
    path('deletar_regra/', login_required(RegrasHonorarioView.delete), name="deletar_regra_honorario"),
    path('update_regra/', login_required(RegrasHonorarioView.update), name="update_regra_honorario"),
    path('validar_regra_honorario/', login_required(RegrasHonorarioView.validarCreateRegraHonorario), name="validar_regra_honorario"),
]