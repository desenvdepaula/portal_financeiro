from django import forms
from core.views import request_project_log

class BoletosForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BoletosForm, self).__init__(*args, **kwargs)
        self.fields.get('arquivo').label = str(self.files.get('arquivo')) 
    
    OPTIONS = (
        ('', ''),
        ('encerramento', 'encerramento'),
        ('encerramento unico', 'encerramento unico'),
        ('honorario contabil', 'honorario contabil'),
    )

    arquivo = forms.FileField(label="Selecione o PDF", help_text="Somente arquivos .PDF", widget=forms.FileInput(attrs={'type':'file','class':'custom-file-input','id':'ARQUIVO'}))
    data = forms.CharField(label="Digite a Data no formato MMYYYY:", help_text="Exemplo: 122022")
    filename = forms.ChoiceField(label="Digite o Nome de Saída dos arquivos:", help_text="Selecione uma das opções (obrigatório)", choices=OPTIONS)

    def clean(self):
        if self.cleaned_data['arquivo'].name.split('.')[-1] != 'pdf':
            raise forms.ValidationError("O arquivo precisa ser de formato .pdf", code="invalid")

    def clean_log(self, username):
        cod = None
        arquivo = self.cleaned_data['arquivo'].name
        arquivoName = self.cleaned_data['filename']
        data = self.cleaned_data['data']
        dados = f"Nome do ARquivo: {arquivo} | Filename: {arquivoName} | Data: {data}"
        request_project_log(cod, dados, "UTILITÁRIOS / BOLETOS", username)

    def clean_arquivo(self):
        arquivoName = self.cleaned_data['arquivo']
        self.cleaned_data['path'] = arquivoName.temporary_file_path()
        return arquivoName

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