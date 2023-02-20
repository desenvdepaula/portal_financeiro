from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import RecibimentosView

urlpatterns = [
    path('', login_required(RecibimentosView.as_view()), name="recibimentos_empresarial"),
]