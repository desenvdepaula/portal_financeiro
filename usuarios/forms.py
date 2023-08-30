from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django import forms

from .models import Usuario

class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('first_name','last_name','email')
        labels = {
            'username' : "Usuário"
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.email = self.cleaned_data["username"]
        if commit:
            user.save()
        return user

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name','last_name','email')

class LoginForm(forms.Form):
    login = forms.CharField(label="Login", max_length=120, widget=forms.TextInput( attrs={'autofocus':'true', 'class':'input'} ))
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class':'input'}))
    