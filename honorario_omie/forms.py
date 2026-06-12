from django import forms
from core.views import request_project_log

class HonorarioApiOMIEForm(forms.Form):
    OPCOES = (
        ('recebimentos', 'RECEBIMENTOS'),
        ('faturamentos', 'FATURAMENTOS'),
    )
    
    data_inicial = forms.DateField(label="Data Inicial: ", help_text="Data Inicial do Período de Atualização...", widget=forms.DateInput(attrs={'type': 'date'}))
    data_final = forms.DateField(label="Data Final: ", help_text="Data Final do Período de Atualização...", widget=forms.DateInput(attrs={'type': 'date'}))
    rotas = forms.ChoiceField(label="Tipo da Atualização:", help_text="Selecione a Atualização Necessária", choices=OPCOES)
    
    def clean_log(self, username):
        data_inicial = self.cleaned_data['data_inicial']
        data_final = self.cleaned_data['data_final']
        request_project_log(0, f"{data_inicial} até {data_final}", "HONORARIO OMIE / ATUALIZAÇÃO DO RELATÓRIO", username)