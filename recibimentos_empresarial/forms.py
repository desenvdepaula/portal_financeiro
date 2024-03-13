from django import forms
from django.core.validators import ValidationError
from core.views import request_project_log

OPERACAO = [
    ('',''),
    ('juros', 'JUROS'),
    ('recebimentos', 'RECEBIMENTOS'),
]

class RecibimentosForm(forms.Form):
    inicio_periodo = forms.DateField(label="Periodo de Início",widget=forms.DateInput(attrs={'name':'inicio_periodo', 'id':'inicio_periodo', 'class':"form-control datepicker", 'type':"date"}))
    fim_periodo = forms.DateField(label="Periodo Final",widget=forms.DateInput(attrs={'name':'fim_periodo', 'id':'fim_periodo', 'class':"form-control datepicker", 'type':"date"}))
    operacao = forms.ChoiceField(label="Operação", choices=OPERACAO)
    
    def clean(self):
        if self.cleaned_data['inicio_periodo'] > self.cleaned_data['fim_periodo']:
            raise ValidationError("Verifique as Datas Novamente.", code="invalid")

    def clean_log(self, username, contas):
        cod = 0
        inicio_periodo = self.cleaned_data['inicio_periodo']
        fim_periodo = self.cleaned_data['fim_periodo']
        operacao = self.cleaned_data['operacao']
        dados = f"OPERAÇÃO: {operacao} | Data Inicial: {inicio_periodo} | Data Final: {fim_periodo} | Contas: {contas}"
        request_project_log(cod, dados, "UTILITÁRIOS / RECEBIMENTO EMPRESARIAL", username)
        
    def clean_empresas_contas(self, contas):
        response = {}
        for row in contas:
            empresa, conta = [i.strip() for i in row.split("-")]
            if empresa in response:
                response[empresa].append(conta)
            else:
                response[empresa] = [conta]
        return response
