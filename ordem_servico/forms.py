from django import forms
from core.views import request_project_log

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

    SERVICO = (
        ('', ''),
        ('4 * CONSULTORIA',  'CONSULTORIA'),
        ('6 * REEMISSAO GUIA EM ATRASO',  'REEMISSAO GUIA EM ATRASO'),
        ('8 * REEMBOLSO COPIA',  'REEMBOLSO COPIA'),
        ('17 * DECLARAÇÃO IMPOSTO DE RENDA PF',  'DECLARAÇÃO IMPOSTO DE RENDA PF'),
        ('19 * CADASTRO',  'CADASTRO'),
        ('21 * DIRF',  'DIRF'),
        ('23 * CERTIDAO NEGATIVA',  'CERTIDAO NEGATIVA'),
        ('25 * HONORÁRIOS DE LEGALIZAÇÃO',  'HONORÁRIOS DE LEGALIZAÇÃO'),
        ('27 * PEDIDO DE PARCELAMENTO',  'PEDIDO DE PARCELAMENTO'),
        ('33 * DIMOB – ATIVIDADES IMOBILIÁRIA',  'DIMOB – ATIVIDADES IMOBILIÁRIA'),
        ('35 * HONORÁRIOS DE MENTORIA',  'HONORÁRIOS DE MENTORIA'),
        ('36 * SPED ICMS',  'SPED ICMS'),
        ('40 * DCTF MENSAL',  'DCTF MENSAL'),
        ('50 * IMPLANTAÇÃO CONTÁBIL',  'IMPLANTAÇÃO CONTÁBIL'),
        ('51 * ALVARÁ DE FUNCIONAMENTO',  'ALVARÁ DE FUNCIONAMENTO'),
        ('52 * REEMISSÃO DE BLOQUETOS APTO/LOTE',  'REEMISSÃO DE BLOQUETOS APTO/LOTE'),
        ('53 * RETIFICAÇÃO DE SERVIÇO',  'RETIFICAÇÃO DE SERVIÇO'),
        ('55 * HONORÁRIOS EXTRAS',  'HONORÁRIOS EXTRAS'),
        ('59 * SICAF',  'SICAF'),
        ('60 * SUCESSÃO TRABALHISTA',  'SUCESSÃO TRABALHISTA'),
        ('90 * REGIMENTO INTERNO',  'REGIMENTO INTERNO'),
        ('98 * REFIS',  'REFIS'),
        ('99 * HOMOLOGAÇÃO RESCISÃO',  'HOMOLOGAÇÃO RESCISÃO'),
        ('103 * DECLARAÇÃO ANUAL DUMEI',  'DECLARAÇÃO ANUAL DUMEI'),
        ('107 * SERVIÇOS PESSOA FÍSICA',  'SERVIÇOS PESSOA FÍSICA'),
        ('109 * DECORE',  'DECORE'),
        ('110 * DARF DE CARNÊ LEÃO',  'DARF DE CARNÊ LEÃO'),
        ('112 * DMED – DECLARAÇÃO DE SERVIÇOS MÉDICOS',  'DMED – DECLARAÇÃO DE SERVIÇOS MÉDICOS'),
        ('113 * SCE – REGISTRO DE CAPITAL ESTRANGEIRO NO BRASIL',  'SCE – REGISTRO DE CAPITAL ESTRANGEIRO NO BRASIL'),
        ('116 * IBGE – DECLARAÇÃO PERÍODO',  'IBGE – DECLARAÇÃO PERÍODO'),
        ('118 * SPED PIS/COFINS',  'SPED PIS/COFINS'),
        ('119 * ECD ANO BASE',  'ECD ANO BASE'),
        ('123 * ECF – ESCRITURAÇÃO CONTABIL FISCAL ANO BASE',  'ECF – ESCRITURAÇÃO CONTABIL FISCAL ANO BASE'),
        ('124 * PER/DCOMP',  'PER/DCOMP'),
        ('125 * REDARF PERÍODO',  'REDARF PERÍODO'),
        ('126 * PROCESSO ADMINISTRATIVO',  'PROCESSO ADMINISTRATIVO'),
        ('128 * DAS PARCELAMENTO SIMPLES NACIONAL',  'DAS PARCELAMENTO SIMPLES NACIONAL'),
        ('129 * REGULARIZAÇÃO DE OBRA-SERO',  'REGULARIZAÇÃO DE OBRA-SERO'),
        ('130 * REGISTRO DE ATA',  'REGISTRO DE ATA'),
        ('132 * REPROCESSAMENTO',  'REPROCESSAMENTO'),
        ('134 * SPED CONTRIBUIÇÕES MENSAL',  'SPED CONTRIBUIÇÕES MENSAL'),
        ('138 * RETIFICAÇÃO DIRPF',  'RETIFICAÇÃO DIRPF'),
        ('141 * RADAR',  'RADAR'),
        ('142 * ATA DE REUNIÃO SÓCIOS REF. DEMONSTRAÇÕES CONTABEIS',  'ATA DE REUNIÃO SÓCIOS REF. DEMONSTRAÇÕES CONTABEIS'),
        ('143 * SERVIÇOS EXTRAS-LEGALIZAÇÃO',  'SERVIÇOS EXTRAS-LEGALIZAÇÃO'),
        ('144 * DEFIS – DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS',  'DEFIS – DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS'),
        ('145 * DECLARAÇÃO INATIVA',  'DECLARAÇÃO INATIVA'),
        ('146 * CBE – DECLARAÇÃO DE CAPITAL BR NO EXTERIOR',  'CBE – DECLARAÇÃO DE CAPITAL BR NO EXTERIOR'),
        ('148 * REQUERIMENTO PMFI CANCELAMENTO NOTAS',  'REQUERIMENTO PMFI CANCELAMENTO NOTAS'),
        ('149 * DCTFWEB',  'DCTFWEB'),
        ('152 * ATENDIMENTO A NOTIFICAÇÃO',  'ATENDIMENTO A NOTIFICAÇÃO'),
        ('156 * RESTITUIÇÃO FGTS',  'RESTITUIÇÃO FGTS'),
        ('157 * E-SOCIAL',  'E-SOCIAL'),
        ('166 * CADASTRO NO BANCO CENTRAL',  'CADASTRO NO BANCO CENTRAL'),
        ('243 * FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO',  'FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO'),
        ('456 * ACORDO COLETIVO DE TRABALHO',  'ACORDO COLETIVO DE TRABALHO'),
        ('1000 * OUTROS/DIVERSOS',  'OUTROS/DIVERSO'),
    )

    id_ordem = forms.IntegerField(required=False)
    servico = forms.ChoiceField(label="Serviço: ", choices=SERVICO, help_text="Escolha uma dentre as Opções (Campo é necessário)")
    empresa = forms.IntegerField(max_value=9999999, label="Código da Empresa:")
    data = forms.DateField(label="Data do Serviço Realizado: ", help_text="", widget=forms.DateInput(attrs={'type': 'date'}))
    execucao = forms.DateTimeField(input_formats=['%H:%M'], label="Tempo de Execução: ", help_text="Formato: HH:MM.", widget=forms.DateInput(attrs={'type': 'time'}))
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
    
    def clean_log(self, username):
        cod = self.cleaned_data['empresa']
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
