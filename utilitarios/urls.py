from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import EmissaoNFManual, Boletos, request_notas_antecipadas

urlpatterns = [
    path('emissao-nf-manual', login_required(EmissaoNFManual.as_view()), name="emissao-nf-manual"),
    path('boletos', login_required(Boletos.as_view()), name="boletos"),
    path('notas_antecipadas', login_required(request_notas_antecipadas), name="notas_antecipadas"),
]