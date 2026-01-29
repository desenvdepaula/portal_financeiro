from django import forms
from core.views import request_project_log
from operator import itemgetter
from .models import DepartamentosControle

class ServicoForm(forms.Form):
    CLASSIFICACAO = (
        ('',''),
        ('HONORÁRIO', 'HONORÁRIO'),
        ('EXTRA', 'EXTRA'),
    )
    
    nr_service = forms.IntegerField(required=False)
    tipo_servico = forms.IntegerField(required=False)
    considera_custo = forms.BooleanField(label="Considerar no Custo ?", required=False)
    regra_ativa = forms.BooleanField(label="Regra Ativa", required=False)
    classificacao = forms.ChoiceField(label="Classificação:", choices=CLASSIFICACAO, help_text="Escolha uma dentre as Opções (Campo é necessário)", required=False)
    obs = forms.CharField(label="Observaçoes:", help_text="Observação do Serviço", widget=forms.Textarea(attrs={'rows': 5, 'cols': 40}), required=False)
    
    def clean_departamentos(self, list_department):
        return DepartamentosControle.objects.filter(nome_departamento__in=list_department)
    
    def clean_service(self, servico_text):
        return servico_text.split(" *** ")

class OrdemServicoForm(forms.Form):
        
    AUTORIZACAO = (
        ('',''),
        ('SIM', 'SIM'),
        ('NÃO', 'NÃO'),
    )

    SOLICITACAO = (
        ('',''),
        ('INTERNA', 'INTERNA'),
        ('CLIENTE', 'CLIENTE'),
    )

    id_ordem = forms.IntegerField(required=False)
    servico = forms.CharField(max_length=255, label="Servico: ")
    empresa = forms.IntegerField(max_value=9999999, label="Código da Empresa:", required=False)
    data = forms.DateField(label="Data do Serviço Realizado: ", help_text="", widget=forms.DateInput(attrs={'type': 'date'}))
    execucao = forms.CharField(label="Tempo de Execução: ", help_text="Formato: HH:MM.")
    descricao = forms.CharField(max_length=47, label="Descrição:", help_text="Descrever a Descrição (47 Caracteres)", widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), required=False)
    descricao_servico = forms.CharField(label="Relatos do Serviço Prestado:", help_text="Descrever a Descrição da Ordem de serviço...", widget=forms.Textarea(attrs={'rows': 6, 'cols': 40}))
    quantidade = forms.IntegerField(label="Quantidade:")
    valor = forms.CharField(label="Valor do Serviço:")
    autorizacao = forms.ChoiceField(label="Autorizado pelo cliente:", choices=AUTORIZACAO, help_text="Escolha uma dentre as Opções (Campo é necessário)")
    solicitacaoLocal = forms.ChoiceField(label="Solicitação:", choices=SOLICITACAO, help_text="Escolha uma dentre as Opções (Campo é necessário)")
    typeCreate = forms.CharField(label="TypeCreate", required=False)
    solicitacao = forms.CharField(max_length=255, label="Solicitado por: (nome)")
    executado = forms.CharField(max_length=255, label="Executado por: (nome)")
    data_cobranca = forms.DateField(label="Data da Cobrança: ", widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    def clean_valor(self):
        valor = float(self.cleaned_data['valor'].replace('.','').replace(',','.'))
        return valor
    
    def clean_descricao(self):
        descricao = self.cleaned_data['descricao'].upper()
        return descricao
    
    def clean_autorizacao(self):
        return True if self.cleaned_data['autorizacao'] == 'SIM' else False
    
    def clean_log(self, username, cod):
        descricao = ' '.join(self.cleaned_data['descricao'].split('\n'))
        data = self.cleaned_data['data']
        servico = self.cleaned_data['servico']
        quantidade = self.cleaned_data['quantidade']
        execucao = self.cleaned_data['execucao']
        valor = self.cleaned_data['valor']
        autorizacao = self.cleaned_data['autorizacao']
        solicitacaoLocal = self.cleaned_data['solicitacaoLocal']
        solicitacao = self.cleaned_data['solicitacao']
        executado = self.cleaned_data['executado']
        dados = f"Descrição: {descricao} | Data: {data} | Serviço: {servico} | Quantidade: {quantidade} | Tempo de Execução: {execucao} | Valor: {valor} | Autorização: {autorizacao} | Solicitação {solicitacaoLocal} - {solicitacao} | Executado por: {executado}" 
        request_project_log(cod, dados, "ORDEM DE SERVIÇO / Update Ordem", username)
