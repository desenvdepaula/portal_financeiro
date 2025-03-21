from django import forms
from core.views import request_project_log
from decimal import Decimal
import locale
import numero_por_extenso # type: ignore

class ContratoHonorarioForm(forms.Form):
    
    OPCOES = (
        ('icc', 'ICC: ÍNDICE DE CUSTO CONTÁBIL'),
        ('igpm', 'IGPM'),
        ('minimo', 'SALÁRIO MÍNIMO'),
    )

    OPTIONS = (
        ('empresa', 'EMPRESA'),
        ('condominio', 'CONDOMÍNIO'),
    )

    codigo_empresa = forms.IntegerField(label="N° da Empresa", help_text="Número inteiro que identifica a empresa.")
    data_inicio_contrato = forms.DateField(label="Início do Contrato", help_text="Data para o início do contrato de honorário", widget=forms.DateInput(attrs={'type':'date'}))
    reajuste = forms.ChoiceField(label="Reajuste", help_text="Selecione o Reajuste", choices=OPCOES)
    opcoes = forms.ChoiceField(label="Empresa / Condomínio", help_text="Selecione uma das opções (obrigatório)", choices=OPTIONS)
    honorario = forms.DecimalField(label="Valor de Honorário", help_text="Valor fixo do honorário", max_digits=8, decimal_places=2)
    valor_por_empregado = forms.DecimalField(label="Valor por Empregado", help_text="", max_digits=5, decimal_places=2)

    def clean_log(self, username):
        codigo_empresa = self.cleaned_data['codigo_empresa']
        reajuste = self.cleaned_data['reajuste']
        data_inicio_contrato = self.cleaned_data['data_inicio_contrato']
        honorario = self.cleaned_data['honorario']
        valor_por_empregado = self.cleaned_data['valor_por_empregado']
        dados = f"Reajuste: {reajuste} | Inicio Contrato: {data_inicio_contrato} | Honorario: {honorario} | Valor por Empregados: {valor_por_empregado}"
        request_project_log(codigo_empresa, dados, "GERADOC / CONTRATO HONORARIO", username)

    def clean_honorario(self):
        self.cleaned_data['honorario_extenso'] = numero_por_extenso.monetario(self.cleaned_data['honorario'])
        return locale.currency(self.cleaned_data['honorario'], grouping=True)

    def clean_valor_por_empregado(self):
        self.cleaned_data['valor_por_empregado_extenso'] = numero_por_extenso.monetario(self.cleaned_data['valor_por_empregado'])
        return locale.currency(self.cleaned_data['valor_por_empregado'], grouping=True)
