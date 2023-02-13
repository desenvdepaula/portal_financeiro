from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps

from django.contrib import messages

def get_permission_error(except_redirect, message="Você não tem permissão para acessar este recurso"):
    def wrapper_decorator(view):
        @wraps(view)
        def slave_function(request, *args, **kwargs):
            try:
                return view(request, *args, **kwargs)
            except:
                messages.error(request, message)
                return redirect(except_redirect)
        return slave_function
    return wrapper_decorator

