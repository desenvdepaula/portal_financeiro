from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import EmissaoNFManual

urlpatterns = [
    path('emissao-nf-manual', login_required(EmissaoNFManual.as_view()), name="emissao-nf-manual"),
]