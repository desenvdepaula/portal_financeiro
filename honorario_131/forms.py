from django import forms
from core.views import request_project_log

class RegrasHonorariosForm(forms.Form):
    cpf_cnpj = forms.CharField(max_length=100)
    cd_empresa = forms.CharField(max_length=6)
    cd_filial = forms.CharField(max_length=2)
    razao_social = forms.CharField(max_length=255)
    have_rule = forms.CharField(max_length=6)
    calcular = forms.BooleanField(required=False)
    somar_filiais = forms.BooleanField(required=False)
    limite = forms.IntegerField(required=False)
    valor = forms.CharField(required=False)
    observacoes = forms.CharField(required=False, widget=forms.TextInput( attrs={'autofocus':'true', 'class':'input'} ))
    
    def clean_log(self, username):
        cpf_cnpj = self.cleaned_data['cpf_cnpj']
        cd_empresa = self.cleaned_data['cd_empresa']
        cd_filial = self.cleaned_data['cd_filial']
        razao_social = self.cleaned_data['razao_social']
        calcular = self.cleaned_data['calcular']
        somar_filiais = self.cleaned_data['somar_filiais']
        have_rule = self.cleaned_data['have_rule']
        limite = self.cleaned_data['limite']
        valor = self.cleaned_data['valor']
        observacoes = self.cleaned_data['observacoes']
        dados = f"CNPJ / CPF: {cpf_cnpj} | cd-empresa: {cd_empresa} / {cd_filial} - {razao_social} | Calcular: {calcular}, Somar: {somar_filiais}, limite: {limite}, valor: {valor}, observações: {observacoes}, tem regras? {have_rule}"
        request_project_log(int(cd_empresa), dados, "HONORARIO 131 / CRIAR REGRA", username)
    
class RegrasHonorariosUpdateForm(forms.Form):
    cpf_cnpj_update = forms.CharField(max_length=100)
    calcular_update = forms.BooleanField(required=False)
    somar_filiais_update = forms.BooleanField(required=False)
    limite_update = forms.IntegerField()
    valor_update = forms.CharField(max_length=10)
    observacoes = forms.CharField(required=False, widget=forms.TextInput( attrs={'autofocus':'true', 'class':'input'} ))
    
    def clean_log(self, username, cd_empresa):
        cpf_cnpj = self.cleaned_data['cpf_cnpj_update']
        calcular = self.cleaned_data['calcular_update']
        somar_filiais = self.cleaned_data['somar_filiais_update']
        limite = self.cleaned_data['limite_update']
        valor = self.cleaned_data['valor_update']
        observacoes = self.cleaned_data['observacoes']
        dados = f"CNPJ / CPF: {cpf_cnpj} | Calcular: {calcular}, Somar: {somar_filiais}, limite: {limite}, valor: {valor}, observações: {observacoes}"
        request_project_log(int(cd_empresa), dados, "HONORARIO 131 / EDITAR REGRA", username)

class RelatorioHonorariosForm(forms.Form):
    empresa = forms.IntegerField(max_value=9999, label="COD. Empresa", required=False)
    
class RealizarCalculoForm(forms.Form):
    compet = forms.CharField(label="Período de Competência (Mês e Ano)", help_text="Período de Competência (* Exemplo: 07/2022 *)")
    
    def clean_compet(self):
        periodo = self.cleaned_data['compet']
        if len(periodo) < 6:
            raise forms.ValidationError("Digite Corretamente o Período Competencia (MM/AAAA)", 'compet')
        else:
            mes_compet, ano_compet = periodo.split("/")
            self.cleaned_data['compet'] = f"01.{mes_compet}.{ano_compet}"

        return self.cleaned_data['compet']
    
    def clean_log(self, username):
        compet = self.cleaned_data['compet']
        dados = f"Competencia: {compet}"
        request_project_log(0, dados, "HONORARIO 131 / REALIZAR CALCULO", username)