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
        ('115 * ALTERAÇÃO DE PRESIDENTE', 'ALTERAÇÃO DE PRESIDENTE'),
        ('136 * ALTERAÇÃO DE SÍNDICO/PRESIDENTE', 'ALTERAÇÃO DE SÍNDICO/PRESIDENTE'),
        ('51 * ALVARÁ', 'ALVARÁ'),
        ('142 * ATA DE REUNIÃO SÓCIOS REF. DEMONSTRAÇÕES CONTABEIS', 'ATA DE REUNIÃO SÓCIOS REF. DEMONSTRAÇÕES CONTABEIS'),
        ('19 * CADASTRO', 'CADASTRO'),
        ('23 * CERTIDAO NEGATIVA', 'CERTIDAO NEGATIVA'),
        ('4 * CONSULTORIA', 'CONSULTORIA'),
        ('61 * CURSOS E PALESTRAS - AUDITÓRIO', 'CURSOS E PALESTRAS - AUDITÓRIO'),
        ('110 * DARF DE CARNÊ  LEÃO', 'DARF DE CARNÊ  LEÃO'),
        ('114 * DARF PARCELAMENTO', 'DARF PARCELAMENTO'),
        ('122 * DARF PARCELAMENTO DIV', 'DARF PARCELAMENTO DIV'),
        ('128 * DAS PARCELAMENTO SIMPLES NACIONAL', 'DAS PARCELAMENTO SIMPLES NACIONAL'),
        ('140 * DASN-DECLARAÇÃO ANUAL SIMPLES NACIONAL', 'DASN-DECLARAÇÃO ANUAL SIMPLES NACIONAL'),
        ('40 * DCTF MENSAL', 'DCTF MENSAL'),
        ('17 * DECL IMP.RENDA P.F.', 'DECL IMP.RENDA P.F.'),
        ('103 * DECLARAÇÃO ANUAL DUMEI', 'DECLARAÇÃO ANUAL DUMEI'),
        ('146 * DECLARAÇÃO BANCO CENTRAL', 'DECLARAÇÃO BANCO CENTRAL'),
        ('113 * DECLARAÇÃO DE CAPITAL BR NO EXTERIOR', 'DECLARAÇÃO DE CAPITAL BR NO EXTERIOR'),
        ('14 * DECLARACAO FISCO CONTABIL DFC', 'DECLARACAO FISCO CONTABIL DFC'),
        ('116 * DECLARAÇÃO IBGE PERÍODO', 'DECLARAÇÃO IBGE PERÍODO'),
        ('145 * DECLARAÇÃO INATIVA', 'DECLARAÇÃO INATIVA'),
        ('63 * DECLARAÇÃO ITR.', 'DECLARAÇÃO ITR.'),
        ('109 * DECORE', 'DECORE'),
        ('149 * DECTFWEB', 'DECTFWEB'),
        ('144 * DEFIS - DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS', 'DEFIS - DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS'),
        ('33 * DIMOB - ATIVIDADES IMOBILIÁRIA', 'DIMOB - ATIVIDADES IMOBILIÁRIA'),
        ('21 * DIRF-DECLARAÇÃO IMPOSTO RENDA RETITO FONTE, ANO', 'DIRF-DECLARAÇÃO IMPOSTO RENDA RETITO FONTE, ANO'),
        ('16 * DIRPJ', 'DIRPJ'),
        ('112 * DMED- DECLARAÇÃO DE SERVIÇOS MÉDICOS', 'DMED- DECLARAÇÃO DE SERVIÇOS MÉDICOS'),
        ('157 * E-SOCIAL', 'E-SOCIAL'),
        ('119 * ECD ANO BASE', 'ECD ANO BASE'),
        ('123 * ECF - ESCRITURAÇÃO CONTABIL FISCAL ANO BASE', 'ECF - ESCRITURAÇÃO CONTABIL FISCAL ANO BASE'),
        ('135 * GPS PARCELAMENTO', 'GPS PARCELAMENTO'),
        ('12 * HONORÁRIO ALTERAÇÃO DE CONTRATO', 'HONORÁRIO ALTERAÇÃO DE CONTRATO'),
        ('56 * HONORÁRIO ALVARÁ DE LICENÇA', 'HONORÁRIO ALVARÁ DE LICENÇA'),
        ('108 * HONORÁRIOS ENCERRAMENTO ATIVIDADES', 'HONORÁRIOS ENCERRAMENTO ATIVIDADES'),
        ('55 * HONORÁRIOS EXTRAS', 'HONORÁRIOS EXTRAS'),
        ('25 * LEGALIZAÇÃO', 'LEGALIZAÇÃO'),
        ('1000 * OUTROS/DIVERSOS', 'OUTROS/DIVERSOS'),
        ('27 * PEDIDO DE PARCELAMENTO', 'PEDIDO DE PARCELAMENTO'),
        ('124 * PER/DCOMP', 'PER/DCOMP'),
        ('126 * PROCESSO ADMINISTRATIVO', 'PROCESSO ADMINISTRATIVO'),
        ('141 * RADAR', 'RADAR'),
        ('15 * RAIS-RELAÇÃO .ANUAL DOS EMPREGADOS', 'RAIS-RELAÇÃO .ANUAL DOS EMPREGADOS'),
        ('137 * RECADASTRAMENTO ALV.LICENÇA DOMICILIO TRIB. - PMFI', 'RECADASTRAMENTO ALV.LICENÇA DOMICILIO TRIB. - PMFI'),
        ('101 * RECRUTAMENTO E SELEÇÃO', 'RECRUTAMENTO E SELEÇÃO'),
        ('125 * REDARF PERÍODO', 'REDARF PERÍODO'),
        ('8 * REEMBOLSO COPIA', 'REEMBOLSO COPIA'),
        ('52 * REEMISSÃO DE BLOQUETOS APTO/LOTE', 'REEMISSÃO DE BLOQUETOS APTO/LOTE'),
        ('6 * REEMISSAO GUIA EM ATRASO', 'REEMISSAO GUIA EM ATRASO'),
        ('98 * REFIS', 'REFIS'),
        ('130 * REGISTRO CARTÓRIO', 'REGISTRO CARTÓRIO'),
        ('129 * REGULARIZAÇÃO DE OBRA - DISO', 'REGULARIZAÇÃO DE OBRA - DISO'),
        ('68 * RENOVAÇÃO ALVARÁ', 'RENOVAÇÃO ALVARÁ'),
        ('148 * REQUERIMENTO PMFI CANCELAMENTO NOTAS', 'REQUERIMENTO PMFI CANCELAMENTO NOTAS'),
        ('53 * RETIFICAÇÃO DE SERVIÇO', 'RETIFICAÇÃO DE SERVIÇO'),
        ('138 * RETIFICAÇÃO DIRPF', 'RETIFICAÇÃO DIRPF'),
        ('143 * SERVIÇOS EXTRAS - LEGALIZAÇÃO', 'SERVIÇOS EXTRAS - LEGALIZAÇÃO'),
        ('107 * SERVIÇOS PESSOA FÍSICIA', 'SERVIÇOS PESSOA FÍSICIA'),
        ('59 * SICAF', 'SICAF'),
        ('134 * SPED CONTRIBUIÇÕES MENSAL', 'SPED CONTRIBUIÇÕES MENSAL'),
        ('118 * SPED PIS/COFINS', 'SPED PIS/COFINS'),
        ('99 * TAXA SERVIÇO HOMOLOGAÇÃO RESCISÃO', 'TAXA SERVIÇO HOMOLOGAÇÃO RESCISÃO'),
        ('156 * TREINAMENTO, CURSO E PALESTRA', 'TREINAMENTO, CURSO E PALESTRA'),
    )

    id_ordem = forms.IntegerField(required=False)
    servico = forms.ChoiceField(label="Serviço: ", choices=SERVICO, help_text="Escolha uma dentre as Opções (Campo é necessário)")
    empresa = forms.IntegerField(max_value=9999, label="Código da Empresa:")
    data = forms.DateField(label="Data do Serviço Realizado: ", help_text="", widget=forms.DateInput(attrs={'type': 'date'}))
    execucao = forms.DateTimeField(input_formats=['%H:%M'], label="Tempo de Execução: ", help_text="Formato: HH:MM.", widget=forms.DateInput(attrs={'type': 'time'}))
    descricao = forms.CharField(max_length=51, label="Descrição:", help_text="Descrever a Descrição (51 Caracteres)", widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}), required=False)
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
