from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import UsuarioChangeForm, UsuarioCreateForm
from .models import Usuario

# @admin.register(Usuario)
# class UsuarioAdmin(UserAdmin):
#     add_form = UsuarioCreateForm
#     form = UsuarioChangeForm
#     model = Usuario
#     list_display = ('first_name', 'last_name', 'email' )
#     fieldsets = (
#         (None, { 'fields': ('username','password')}),
#         ('Informações Pessoais', {'fields':('first_name','last_name', 'email','foto')}),
#         ('Permissões',{ 'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions') }),
#         ('Datas Importantes', {'fields': ('last_login','date_joined') })
#     )
