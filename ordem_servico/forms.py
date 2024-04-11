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
    tipo_servico = forms.CharField(max_length=255, help_text="Digite o Tipo do Serviço", label="Tipo do Serviço: ")
    considera_custo = forms.BooleanField(label="Considerar no Custo ?", required=False)
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

    SERVICO = (
        ('', ''),
        ("2 * REEMBOLSO TAXA CONFORME DOCUMENTO", "REEMBOLSO TAXA CONFORME DOCUMENTO"),
        ("3 * ALVARÁ POLICIAL", "ALVARÁ POLICIAL"),
        ("8 * REEMBOLSO COPIA", "REEMBOLSO COPIA"),
        ("11 * MANUTENÇÃO IMPLANTAÇÃO", "MANUTENÇÃO IMPLANTAÇÃO"),
        ("12 * HONORÁRIO ALTERAÇÃO DE CONTRATO", "HONORÁRIO ALTERAÇÃO DE CONTRATO"),
        ("13 * REEMBOLSO TAXA - 1º TABELIONATO", "REEMBOLSO TAXA - 1º TABELIONATO"),
        ("14 * HORAS COLABORADOR NA EMPRESA", "HORAS COLABORADOR NA EMPRESA"),
        ("17 * DECLARAÇÃO IMPOSTO DE RENDA PF", "DECLARAÇÃO IMPOSTO DE RENDA PF"),
        ("19 * CADASTRO", "CADASTRO"),
        ("21 * DIRF", "DIRF"),
        ("23 * CERTIDÃO", "CERTIDÃO"),
        ("24 * NEGOCIAÇÕES DE CÂMBIO", "NEGOCIAÇÕES DE CÂMBIO"),
        ("25 * HONORÁRIOS DE LEGALIZAÇÃO", "HONORÁRIOS DE LEGALIZAÇÃO"),
        ("27 * PEDIDO DE PARCELAMENTO", "PEDIDO DE PARCELAMENTO"),
        ("33 * DIMOB – ATIVIDADES IMOBILIÁRIA", "DIMOB – ATIVIDADES IMOBILIÁRIA"),
        ("34 * BPO CONDOMÍNIO - SERVIÇO ADMINISTRATIVO FINANCEIRO", "BPO CONDOMÍNIO - SERVIÇO ADMINISTRATIVO FINANCEIRO"),
        ("35 * HONORÁRIOS DE MENTORIA", "HONORÁRIOS DE MENTORIA"),
        ("36 * SPED ICMS", "SPED ICMS"),
        ("37 * CONTRATOS - ELABORAÇÃO E/OU REVISÃO", "CONTRATOS - ELABORAÇÃO E/OU REVISÃO"),
        ("39 * REEMBOLSO TAXAS CARTORIO/JUNTA COMERCIAL", "REEMBOLSO TAXAS CARTORIO/JUNTA COMERCIAL"),
        ("40 * DCTF MENSAL", "DCTF MENSAL"),
        ("41 * REEMBOLSO TAXA - FORUM", "REEMBOLSO TAXA - FORUM"),
        ("46 * REEMBOLSO ENCADERNAÇÃO LIVRO RAZÃO/DIÁRIO", "REEMBOLSO ENCADERNAÇÃO LIVRO RAZÃO/DIÁRIO"),
        ("47 * REEMBOLSO LIVRO RAZAO Nº FLS", "REEMBOLSO LIVRO RAZAO Nº FLS"),
        ("50 * IMPLANTAÇÃO CONTÁBIL", "IMPLANTAÇÃO CONTÁBIL"),
        ("51 * ALVARÁ DE FUNCIONAMENTO", "ALVARÁ DE FUNCIONAMENTO"),
        ("52 * REEMISSÃO DE BOLETOS APTO/LOTE", "REEMISSÃO DE BOLETOS APTO/LOTE"),
        ("54 * CONVENÇÃO COLETIVA DE TRABALHO", "CONVENÇÃO COLETIVA DE TRABALHO"),
        ("59 * SICAF", "SICAF"),
        ("60 * SUCESSÃO TRABALHISTA", "SUCESSÃO TRABALHISTA"),
        ("62 * SERVIÇOS EXTRAS - BPO FINANCEIRO", "SERVIÇOS EXTRAS - BPO FINANCEIRO"),
        ("63 * DECLARAÇÃO ITR", "DECLARAÇÃO ITR"),
        ("64 * ATUALIZAÇÃO SCE-IED (RDE) – BPO FINANCEIRO", "ATUALIZAÇÃO SCE-IED (RDE) – BPO FINANCEIRO"),
        ("67 * SERVIÇOS OMIE", "SERVIÇOS OMIE"),
        ("88 * SÍNDICO PROFISSIONAL", "SÍNDICO PROFISSIONAL"),
        ("89 * HONORÁRIO DE CONSULTORIA - DIEX", "HONORÁRIO DE CONSULTORIA - DIEX"),
        ("90 * REGIMENTO INTERNO", "REGIMENTO INTERNO"),
        ("93 * AUDITORIA EM CARTÕES DE CRÉDITO, DÉBITO E VOUCHER", "AUDITORIA EM CARTÕES DE CRÉDITO, DÉBITO E VOUCHER"),
        ("95 * DECLARAÇÃO ITCMD", "DECLARAÇÃO ITCMD"),
        ("98 * REFIS - HONORÁRIO DE ELABORAÇÃO", "REFIS - HONORÁRIO DE ELABORAÇÃO"),
        ("99 * HOMOLOGAÇÃO RESCISÃO", "HOMOLOGAÇÃO RESCISÃO"),
        ("103 * DECLARAÇÃO ANUAL MEI", "DECLARAÇÃO ANUAL MEI"),
        ("105 * BPO – FISCAL", "BPO – FISCAL"),
        ("107 * SERVIÇOS PESSOA FÍSICA", "SERVIÇOS PESSOA FÍSICA"),
        ("108 * HONORÁRIOS ENCERRAMENTO ATIVIDADES", "HONORÁRIOS ENCERRAMENTO ATIVIDADES"),
        ("109 * DECORE – DECLARAÇÃO COMPROBATÓRIA DE PERCEPÇÃO DE RENDIMENTOS", "DECORE – DECLARAÇÃO COMPROBATÓRIA DE PERCEPÇÃO DE RENDIMENTOS"),
        ("110 * DARF DE CARNÊ LEÃO", "DARF DE CARNÊ LEÃO"),
        ("112 * DMED – DECLARAÇÃO DE SERVIÇOS MÉDICOS", "DMED – DECLARAÇÃO DE SERVIÇOS MÉDICOS"),
        ("113 * SCE - REGISTRO DE CAPITAL ESTRANGEIRO BRASIL (RDE) – BPO FINANCEIRO", "SCE - REGISTRO DE CAPITAL ESTRANGEIRO BRASIL (RDE) – BPO FINANCEIRO"),
        ("116 * IBGE – DECLARAÇÃO PERÍODO", "IBGE – DECLARAÇÃO PERÍODO"),
        ("118 * SPED PIS/COFINS", "SPED PIS/COFINS"),
        ("119 * ECD ANO BASE", "ECD ANO BASE"),
        ("123 * ECF – ESCRITURAÇÃO CONTABIL FISCAL ANO BASE", "ECF – ESCRITURAÇÃO CONTABIL FISCAL ANO BASE"),
        ("124 * PER/DCOMP", "PER/DCOMP"),
        ("129 * REGULARIZAÇÃO DE OBRA-SERO", "REGULARIZAÇÃO DE OBRA-SERO"),
        ("130 * REGISTRO DE ATA", "REGISTRO DE ATA"),
        ("134 * SPED CONTRIBUIÇÕES MENSAL", "SPED CONTRIBUIÇÕES MENSAL"),
        ("138 * RETIFICAÇÃO DIRPF", "RETIFICAÇÃO DIRPF"),
        ("141 * RADAR", "RADAR"),
        ("142 * ATA DE REUNIÃO SÓCIOS - DEMONSTRAÇÕES CONTÁBEIS", "ATA DE REUNIÃO SÓCIOS - DEMONSTRAÇÕES CONTÁBEIS"),
        ("143 * SERVIÇOS EXTRAS - LEGALIZAÇÃO", "SERVIÇOS EXTRAS - LEGALIZAÇÃO"),
        ("144 * DEFIS – DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS", "DEFIS – DECL.INFORMAÇÕES SOCIOECONÔMICAS E FISCAIS"),
        ("145 * DECLARAÇÃO INATIVA", "DECLARAÇÃO INATIVA"),
        ("146 * CBE - DECLARAÇÃO DE CAPITAL BR NO EXTERIOR – BPO FINANCEIRO", "CBE - DECLARAÇÃO DE CAPITAL BR NO EXTERIOR – BPO FINANCEIRO"),
        ("148 * REQUERIMENTO P/ PREFEITURA – ESCRITA FISCAL", "REQUERIMENTO P/ PREFEITURA – ESCRITA FISCAL"),
        ("149 * DCTFWEB", "DCTFWEB"),
        ("153 * SERVIÇOS EXTRAS – DEPARTAMENTO PESSOAL", "SERVIÇOS EXTRAS – DEPARTAMENTO PESSOAL"),
        ("154 * SERVIÇOS EXTRAS - ESCRITA FISCAL", "SERVIÇOS EXTRAS - ESCRITA FISCAL"),
        ("156 * RESTITUIÇÃO FGTS", "RESTITUIÇÃO FGTS"),
        ("157 * E-SOCIAL", "E-SOCIAL"),
        ("159 * SERVIÇOS EXTRAS - CONTABILIDADE", "SERVIÇOS EXTRAS - CONTABILIDADE"),
        ("161 * SERVIÇOS OPERACIONAIS FINANCEIROS/ADMINISTRATIVOS", "SERVIÇOS OPERACIONAIS FINANCEIROS/ADMINISTRATIVOS"),
        ("162 * ADMINISTRADOR DELEGADO", "ADMINISTRADOR DELEGADO"),
        ("165 * IMPLANTAÇÃO AUDITORIA CARTÕES CRED, DEB E VOUCHER", "IMPLANTAÇÃO AUDITORIA CARTÕES CRED, DEB E VOUCHER"),
        ("166 * CADASTRO NO BANCO CENTRAL – BPO FINANCEIRO", "CADASTRO NO BANCO CENTRAL – BPO FINANCEIRO"),
        ("167 * SERVIÇOS EXTRAS – CONDOMÍNIO", "SERVIÇOS EXTRAS – CONDOMÍNIO"),
        ("168 * SERVIÇOS EXTRAS – ROCKET", "SERVIÇOS EXTRAS – ROCKET"),
        ("169 * SERVIÇOS EXTRAS – AUDITORIA", "SERVIÇOS EXTRAS – AUDITORIA"),
        ("170 * SERVIÇOS EXTRAS – CONSULTORIA TRIBUTÁRIA", "SERVIÇOS EXTRAS – CONSULTORIA TRIBUTÁRIA"),
        ("171 * SERVIÇOS EXTRAS – COMERCIAL", "SERVIÇOS EXTRAS – COMERCIAL"),
        ("172 * RETIFICAÇÃO DE SERVIÇO – ESCRITA FISCAL", "RETIFICAÇÃO DE SERVIÇO – ESCRITA FISCAL"),
        ("173 * RETIFICAÇÃO DE SERVIÇO – CONTABILIDADE ", "RETIFICAÇÃO DE SERVIÇO – CONTABILIDADE "),
        ("174 * RETIFICAÇÃO DE SERVIÇO – DEPARTAMENTO PESSOAL", "RETIFICAÇÃO DE SERVIÇO – DEPARTAMENTO PESSOAL"),
        ("175 * RETIFICAÇÃO DE SERVIÇO – CONSULTORIA TRIBUTÁRIA", "RETIFICAÇÃO DE SERVIÇO – CONSULTORIA TRIBUTÁRIA"),
        ("176 * RETIFICAÇÃO DE SERVIÇO – ROCKET", "RETIFICAÇÃO DE SERVIÇO – ROCKET"),
        ("177 * REPROCESSAMENTO – DEPARTAMENTO PESSOAL", "REPROCESSAMENTO – DEPARTAMENTO PESSOAL"),
        ("178 * REPROCESSAMENTO – ESCRITA FISCAL", "REPROCESSAMENTO – ESCRITA FISCAL"),
        ("179 * REPROCESSAMENTO – CONTABILIDADE", "REPROCESSAMENTO – CONTABILIDADE"),
        ("180 * REPROCESSAMENTO – ROCKET", "REPROCESSAMENTO – ROCKET"),
        ("182 * REEMISSAO GUIA EM ATRASO – DEPARTAMENTO PESSOAL", "REEMISSAO GUIA EM ATRASO – DEPARTAMENTO PESSOAL"),
        ("183 * REEMISSAO GUIA EM ATRASO – ESCRITA FISCAL", "REEMISSAO GUIA EM ATRASO – ESCRITA FISCAL"),
        ("184 * REEMISSAO GUIA EM ATRASO – CONTABILIDADE", "REEMISSAO GUIA EM ATRASO – CONTABILIDADE"),
        ("185 * REEMISSAO GUIA EM ATRASO – CONDOMÍNIO", "REEMISSAO GUIA EM ATRASO – CONDOMÍNIO"),
        ("186 * REEMISSAO GUIA EM ATRASO – ROCKET", "REEMISSAO GUIA EM ATRASO – ROCKET"),
        ("187 * REEMISSAO GUIA EM ATRASO – LEGALIZAÇÃO", "REEMISSAO GUIA EM ATRASO – LEGALIZAÇÃO"),
        ("188 * PROCESSO ADMINISTRATIVO – LEGALIZAÇÃO", "PROCESSO ADMINISTRATIVO – LEGALIZAÇÃO"),
        ("189 * PROCESSO ADMINISTRATIVO – CONSULTORIA TRIBUTÁRIA", "PROCESSO ADMINISTRATIVO – CONSULTORIA TRIBUTÁRIA"),
        ("190 * PROCESSO ADMINISTRATIVO – ROCKET", "PROCESSO ADMINISTRATIVO – ROCKET"),
        ("191 * PROCESSO ADMINISTRATIVO – ESCRITA FISCAL", "PROCESSO ADMINISTRATIVO – ESCRITA FISCAL"),
        ("192 * ACOMPANHAMENTO EM ASSEMBLEIAS", "ACOMPANHAMENTO EM ASSEMBLEIAS"),
        ("193 * HONORARIOS DE CONSULTORIA – DEPARTAMENTO PESSOAL", "HONORARIOS DE CONSULTORIA – DEPARTAMENTO PESSOAL"),
        ("194 * PROCESSO ADMINISTRATIVO – DEPARTAMENTO PESSOAL", "PROCESSO ADMINISTRATIVO – DEPARTAMENTO PESSOAL"),
        ("195 * REDARF – DEPARTAMENTO PESSOAL", "REDARF – DEPARTAMENTO PESSOAL"),
        ("196 * REDARF – CONTABILIDADE", "REDARF – CONTABILIDADE"),
        ("197 * HONORARIOS DE CONSULTORIA – COMERCIAL", "HONORARIOS DE CONSULTORIA – COMERCIAL"),
        ("198 * ATENDIMENTO A NOTIFICAÇÃO – CONTABILIDADE", "ATENDIMENTO A NOTIFICAÇÃO – CONTABILIDADE"),
        ("199 * ATENDIMENTO A NOTIFICAÇÃO – LEGALIZAÇÃO", "ATENDIMENTO A NOTIFICAÇÃO – LEGALIZAÇÃO"),
        ("200 * ATENDIMENTO A NOTIFICAÇÃO – CONSULTORIA TRIBUTÁRIA", "ATENDIMENTO A NOTIFICAÇÃO – CONSULTORIA TRIBUTÁRIA"),
        ("243 * FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO - DP", "FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO - DP"),
        ("360 * GANHO DE CAPITAL", "GANHO DE CAPITAL"),
        ("363 * PARCELAMENTOS DE TRIBUTOS – PESSOA FÍSICA", "PARCELAMENTOS DE TRIBUTOS – PESSOA FÍSICA"),
        ("364 * COMUNICAÇÃO DE SAÍDA DEFINITIVA DO PAÍS", "COMUNICAÇÃO DE SAÍDA DEFINITIVA DO PAÍS"),
        ("401 * PROCESSO ADMINISTRATIVO – PESSOA FÍSICA", "PROCESSO ADMINISTRATIVO – PESSOA FÍSICA"),
        ("402 * RECUPERAÇÃO DE TRIBUTOS – PESSOA FÍSICA", "RECUPERAÇÃO DE TRIBUTOS – PESSOA FÍSICA"),
        ("403 * REDARF – CONSULTORIA TRIBUTÁRIA", "REDARF – CONSULTORIA TRIBUTÁRIA"),
        ("404 * REQUERIMENTO P/ PREFEITURA – CONSULTORIA TRIBUTÁRIA", "REQUERIMENTO P/ PREFEITURA – CONSULTORIA TRIBUTÁRIA"),
        ("405 * PROCESSO DE ABERTURA DE LOJA FRANCA", "PROCESSO DE ABERTURA DE LOJA FRANCA"),
        ("406 * ATUALIZAÇÃO SCE-IED (RDE) – CONSULTORIA TRIBUTÁRIA", "ATUALIZAÇÃO SCE-IED (RDE) – CONSULTORIA TRIBUTÁRIA"),
        ("407 * CADASTRO NO BANCO CENTRAL – CONSULTORIA TRIBUTÁRIA", "CADASTRO NO BANCO CENTRAL – CONSULTORIA TRIBUTÁRIA"),
        ("408 * CBE - DECLARAÇÃO DE CAPITAL BR NO EXTERIOR – CONSULTORIA TRIBUTÁRIA", "CBE - DECLARAÇÃO DE CAPITAL BR NO EXTERIOR – CONSULTORIA TRIBUTÁRIA"),
        ("409 * SCE - REGISTRO DE CAPITAL ESTRANGEIRO BRASIL (RDE) – CONSULTORIA TRIBUTÁRIA", "SCE - REGISTRO DE CAPITAL ESTRANGEIRO BRASIL (RDE) – CONSULTORIA TRIBUTÁRIA"),
        ("410 * REEMBOLSO TAXA - 2º TABELIONATO", "REEMBOLSO TAXA - 2º TABELIONATO"),
        ("411 * REEMBOLSO TAXA RTD - REGISTRO TÍTULOS E DOCUMENTOS", "REEMBOLSO TAXA RTD - REGISTRO TÍTULOS E DOCUMENTOS"),
        ("412 * REEMBOLSO TAXA PREFEITURA", "REEMBOLSO TAXA PREFEITURA"),
        ("456 * ACORDO COLETIVO DE TRABALHO", "ACORDO COLETIVO DE TRABALHO"),
        ("657 * REEMBOLSO TAXAS E CARTÓRIO", "REEMBOLSO TAXAS E CARTÓRIO"),
        ("659 * FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO - ROCKET", "FOLHA COMPLEMENTAR OU DISSÍDIO COLETIVO - ROCKET"),
        ("1000 * OUTROS/DIVERSOS", "OUTROS/DIVERSOS"),
    )

    id_ordem = forms.IntegerField(required=False)
    servico = forms.ChoiceField(label="Serviço: ", choices=tuple([i for i in sorted(SERVICO, key=itemgetter(1))]), help_text="Escolha uma dentre as Opções (Campo é necessário)")
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
