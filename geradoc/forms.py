from django import forms
from core.views import request_project_log
from decimal import Decimal
from .lib.numeric.numerais import Numerais

class ContratoHonorarioForm(forms.Form):
    REGIME_TRIBUTARIO = (
        ('isento', 'ISENTO'),
        ('SIMPLES NACIONAL', 'SIMPLES NACIONAL'),
        ('LUCRO PRESUMIDO', 'LUCRO PRESUMIDO'),
        ('LUCRO REAL', 'LUCRO REAL'),
    )
    
    OPCOES = (
        ('igpm', 'IGPM'),
        ('minimo', 'SALÁRIO MÍNIMO'),
    )

    OPTIONS = (
        ('', ''),
        ('empresa', 'EMPRESA'),
        ('condominio', 'CONDOMÍNIO'),
    )

    codigo_empresa = forms.IntegerField(label="N° da Empresa", help_text="Número inteiro que identifica a empresa.")
    data_inicio_contrato = forms.DateField(label="Início do Contrato", help_text="Data para o início do contrato de honorário", widget=forms.DateInput(attrs={'type':'date'}))
    regime_tributario = forms.ChoiceField(label="Regime Tributário", help_text="Selecio o Regime Tributário", choices=REGIME_TRIBUTARIO)
    reajuste = forms.ChoiceField(label="Reajuste", help_text="Selecione o Reajuste", choices=OPCOES)
    opcoes = forms.ChoiceField(label="Empresa / Condomínio", help_text="Selecione uma das opções (obrigatório)", choices=OPTIONS)
    honorario = forms.DecimalField(label="Valor de Honorário", help_text="Valor fixo do honorário", max_digits=8, decimal_places=2)
    limite_empregados = forms.IntegerField(label="N° Limite de Empregados", help_text="N° máximo de empregados", max_value=9999, initial=0)
    valor_por_empregado = forms.DecimalField(label="Valor por Empregado", help_text="", max_digits=4, decimal_places=2)
    #valor_ecd = forms.DecimalField(label="Valor ECD", help_text="", max_digits=8, decimal_places=2)

    def clean_log(self, username):
        codigo_empresa = self.cleaned_data['codigo_empresa']
        regime_tributario = self.cleaned_data['regime_tributario']
        reajuste = self.cleaned_data['reajuste']
        data_inicio_contrato = self.cleaned_data['data_inicio_contrato']
        honorario = self.cleaned_data['honorario']
        limite_empregados = self.cleaned_data['limite_empregados']
        valor_por_empregado = self.cleaned_data['valor_por_empregado']
        dados = f"Reajuste: {reajuste} | Regime Tributario: {regime_tributario} | Inicio Contrato: {data_inicio_contrato} | Honorario: {honorario} | Limites de Empregados: {limite_empregados} | Valor por Empregados: {valor_por_empregado}"
        request_project_log(codigo_empresa, dados, "GERADOC / CONTRATO HONORARIO", username)

    def clean_honorario(self):
        numero_extenso = Numerais.numero_extenso("{:.0f}".format(self.cleaned_data['honorario']))
        self.cleaned_data['honorario_extenso'] = Numerais.concatenar_numeros(numero_extenso)
        self.cleaned_data['valor_defis'] = self.get_valor_defis()
        self.cleaned_data['valor_ecf'] = self.get_valor_ecf() 
        return "{:.2f}".format(self.cleaned_data['honorario']).replace('.',',')

    def clean_valor_por_empregado(self):
        numero_extenso = Numerais.numero_extenso("{:.0f}".format(self.cleaned_data['valor_por_empregado']))
        self.cleaned_data['valor_por_empregado_extenso'] = Numerais.concatenar_numeros(numero_extenso)
        return "{:.2f}".format(self.cleaned_data['valor_por_empregado']).replace('.',',')
    
    def clean_limite_empregados(self):
        numero_extenso = Numerais.numero_extenso("{:.0f}".format(self.cleaned_data['limite_empregados']))
        self.cleaned_data['limite_empregados_extenso'] = Numerais.concatenar_numeros(numero_extenso)
        return self.cleaned_data['limite_empregados']

    def get_valor_defis(self):
        if self.cleaned_data['regime_tributario'] == 'SIMPLES NACIONAL':
            defis = self.cleaned_data['honorario'] * Decimal(0.3)
            return  "{:.2f}".format(defis if defis > Decimal(250) else Decimal(250)).replace('.',',')
        return 0.0

    def get_valor_ecf(self):
        if self.cleaned_data['regime_tributario'] == 'LUCRO PRESUMIDO':
            ecf = self.cleaned_data['honorario'] * Decimal(0.4)
            return ecf if ecf > Decimal(250) else Decimal(250)
        if self.cleaned_data['regime_tributario'] == 'LUCRO REAL':
            ecf = self.cleaned_data['honorario'] * Decimal(0.5) 
            return "{:.2f}".format(ecf if ecf > Decimal(250) else Decimal(250)).replace('.',',')
        return 0.0