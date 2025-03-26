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

class DistratoForm(forms.Form):
    OBRIGACOES_ANUAIS = (
        ('ECD','ECD'),
        ('ECF','ECF'),
        ('IBGE','IBGE'),
        ('RAIS','RAIS'),
        ('DEFIS','DEFIS'),
        ('DIRF','DIRF'),
        ('BACEN','BACEN'),
        ('RADAR','RADAR'),
        ('DMED','DMED'),
        ('DIMOB','DIMOB'),
        ('ITR','ITR'),
        ('RDE','RDE'),
        ('CBE','CBE')
    )

    codigo_empresa = forms.IntegerField(label="N° da Empresa", help_text="Código identificador da empresa")
    codigo_estab = forms.IntegerField(label="N° do Estabelecimento", help_text="Código identificador do estabelecimento", initial=1)
    data_novo_contador = forms.DateField(label="Contratação de Novo Contador", help_text="Data de início do contrato com outro contador", widget=forms.DateInput(attrs={'type':'date'}))
    data_competencia = forms.DateField(label="Nossa Competência", help_text="Data de competência", widget=forms.DateInput(attrs={'type':'date'}))
    ano_competencia = forms.IntegerField(label="Ano de competência", help_text="", required=False)
    boletos_a_pagar = forms.BooleanField(label="Boletos à Pagar?", required=False)
    nr_boleto = forms.CharField(label="N° Boleto", help_text="Identificador do boleto", required=False)
    data_vencimento_boletos = forms.DateField(label="Data de Vencimento dos Boletos", help_text="Data de vencimento do boleto", widget=forms.DateInput(attrs={'type':'date'}), required=False)
    valor = forms.DecimalField(label="Valor à Pagar", max_digits=8, decimal_places=2, required=False)
    obrigacoes_anuais = forms.MultipleChoiceField(label="", widget=forms.CheckboxSelectMultiple(attrs={}), choices=OBRIGACOES_ANUAIS)

    def clean_log(self, username):
        codigo_empresa = self.cleaned_data['codigo_empresa']
        codigo_estab = self.cleaned_data['codigo_estab']
        data_novo_contador = self.cleaned_data['data_novo_contador']
        data_competencia = self.cleaned_data['data_competencia']
        ano_competencia = self.cleaned_data['ano_competencia']
        boletos_a_pagar = self.cleaned_data['boletos_a_pagar']
        nr_boleto = self.cleaned_data['nr_boleto']
        data_vencimento_boletos = self.cleaned_data['data_vencimento_boletos']
        valor = self.cleaned_data['valor']
        obrigacoes_anuais = self.cleaned_data['obrigacoes_anuais']
        dados = f"Codigo Estab.: {codigo_estab} | Data Novo Contador: {data_novo_contador} | Data Competencia: {data_competencia} | Ano Competencia: {ano_competencia} | Boletos: {boletos_a_pagar} | Número dos boletos: {nr_boleto} | Data Vencimento Boleto: {data_vencimento_boletos} | Valor: {valor} | Obrigações Anuais: {obrigacoes_anuais}"
        request_project_log(codigo_empresa, dados, "GERADOC / DISTRATO", username)

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor:
            valor = "{:,.2f}".format(valor).split('.')
            valor = "{0},{1}".format(valor[0].replace(',','.'), valor[1])
        return valor

    def clean_data_novo_contador(self):
        dia = numero_por_extenso.real(str(self.cleaned_data['data_novo_contador']).split("-")[-1])
        ano = numero_por_extenso.real(str(self.cleaned_data['data_novo_contador']).split("-")[0])
        self.cleaned_data['diaDataNovoContador'] = dia
        self.cleaned_data['anoDataNovoContador'] = ano
        return self.cleaned_data['data_novo_contador']

    def clean_data_competencia(self):
        dia = numero_por_extenso.real(str(self.cleaned_data['data_competencia']).split("-")[-1])
        ano = numero_por_extenso.real(str(self.cleaned_data['data_competencia']).split("-")[0])
        self.cleaned_data['diaDatacompetencia'] = dia
        self.cleaned_data['anoDatacompetencia'] = ano
        return self.cleaned_data['data_competencia']

    def clean_ano_competencia(self):
        ano = numero_por_extenso.real(str(self.cleaned_data['ano_competencia']))
        self.cleaned_data['anoCompetencia'] = ano
        return self.cleaned_data['ano_competencia']