from django import forms
from core.views import request_project_log

class EmissaoNFManualForm(forms.Form):

    ACOES = (
        ('9501', 9501),
        ('9502', 9502),
        ('9505', 9505),
        ('9567', 9567),
        ('9575', 9575),
    )

    data = forms.DateField(label="Data de Retorno:", help_text="Selecione a Data de Retorno", widget=forms.DateInput(attrs={'type': 'date'}))
    acoes = forms.ChoiceField(label="Código do Escritório", help_text="Selecione o Código do Escritório", choices=ACOES)

    def clean_empresas(self, empresas, username):
        if not empresas:
            raise forms.ValidationError("Ao menos uma empresa deve ser informada", code="empresa_ausente")
        else:
            acoes = self.cleaned_data['acoes']
            data = self.cleaned_data['data']
            dados = f"Data Retorno: {data} | Código do Escritório: {acoes}"
            for empresa in empresas:
                request_project_log(empresa, dados, "UTILITÁRIOS / EMISSÃO NF MANUAL", username)

        return empresas