from django.http import HttpResponseForbidden
from django.urls import reverse

class GrupoAutorizadoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorar algumas URLs (como login, logout, admin)
        url_livre = (
            request.path.startswith('/static/') or
            request.user.is_anonymous  # ignora usuários não logados
        )

        if not url_livre:
            if not request.user.groups.filter(name__in=['Diretoria', 'Financeiro']).exists():
                return HttpResponseForbidden('Você não tem permissão para acessar esse recurso.')

        response = self.get_response(request)
        return response