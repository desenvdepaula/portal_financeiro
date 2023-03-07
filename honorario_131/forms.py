from django import forms

class RegrasHonorariosForm(forms.Form):
    cd_financeiro = forms.CharField(max_length=100)
    cd_empresa = forms.CharField(max_length=6)
    cd_filial = forms.CharField(max_length=2)
    razao_social = forms.CharField(max_length=255)
    calcular = forms.BooleanField(required=False)
    somar_filiais = forms.BooleanField(required=False)
    limite = forms.IntegerField()
    valor = forms.FloatField()
    
class RegrasHonorariosUpdateForm(forms.Form):
    cd_financeiro_update = forms.CharField(max_length=100)
    calcular_update = forms.BooleanField(required=False)
    somar_filiais_update = forms.BooleanField(required=False)
    limite_update = forms.IntegerField()
    valor_update = forms.CharField(max_length=10)

class RelatorioHonorariosForm(forms.Form):
    empresa = forms.IntegerField(max_value=9999, label="COD. Empresa", required=False)
    
class RealizarCalculoForm(forms.Form):
    data = forms.DateField(widget=forms.DateInput(attrs={"type":"date"}))
    compet = forms.CharField(label="Período de Competência (Mês e Ano)", help_text="Período de Competência (* Exemplo: 07/2022 *)")
    
    def clean_compet(self):
        periodo = self.cleaned_data['compet']
        if len(periodo) < 6:
            raise forms.ValidationError("Digite Corretamente o Período Competencia (MM/AAAA)", 'compet')
        else:
            mes_compet, ano_compet = periodo.split("/")
            self.cleaned_data['compet'] = f"01.{mes_compet}.{ano_compet}"

        return self.cleaned_data['compet']