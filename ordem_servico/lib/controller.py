from datetime import datetime, date
from io import BytesIO
import csv
import requests
import base64
import pandas as pd
import fitz
import time
from django.http import HttpResponse, JsonResponse
from core.views import get_request_to_api_omie
from ..models import OrdemServico, EmpresasOmie
from .database import Manager
from .querys import filter_planilha, sql_get_services_questor, get_cnpj_empresas

class Controller():

    def __init__(self, *args, **kwargs):
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)

    #------------------ SERVIÇOS ------------------#
    
    def get_servicos_questor(self, codigos=None):
        self.manager.connect()
        try:
            if codigos:
                codigos = tuple([i.cd_servico for i in codigos])
            return self.manager.run_query_for_select(sql_get_services_questor(codigos))
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()
    
    def gerarPlanilhasOrdens(self, filtros):
        try:
            results = filter_planilha(filtros)
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                listOrdens = []
                
                for order in results:
                    ordem = vars(order)
                    if order.empresa:
                        empresa = vars(order.empresa)
                        ordem['codigo_cliente_omie'] = empresa.get('codigo_cliente_omie')
                        ordem['cd_empresa'] = empresa.get('cd_empresa')
                        ordem['nome_empresa'] = empresa.get('name_empresa')
                    del ordem['_state']
                    del ordem['criador_os']
                    del ordem['empresa_id']
                    ordem['data_cobranca'] = ordem['data_cobranca'].strftime('%d/%m/%Y')
                    ordem['data_realizado'] = ordem['data_realizado'].strftime('%d/%m/%Y')
                    ordem['autorizado_pelo_cliente'] = 'SIM' if ordem['autorizado_pelo_cliente'] else 'NÃO'
                    preco = float(ordem['valor'])
                    preco_convertido = f"R$ {preco:_.2f}"
                    preco_final = preco_convertido.replace('.',',').replace('_','.')
                    ordem['valor'] = preco_final
                    listOrdens.append(ordem)
                
                df = pd.DataFrame(listOrdens)
                df2 = df.rename({
                    'departamento': 'Departamento',
                    'cd_servico' : 'Cd. Serviço',
                    'servico' : 'Serviço',
                    'ds_servico' : 'Descrição do Serviço',
                    'observacoes_servico' : 'Observações do Serviço',
                    'cd_empresa' : 'Código Empresa',
                    'nome_empresa' : 'Nome Empresa',
                    'data_realizado' : 'Data Realizado',
                    'data_cobranca' : 'Data de Cobrança',
                    'quantidade' : 'Quantidade',
                    'hora_trabalho' : 'Horas',
                    'valor' : 'Valor',
                    'autorizado_pelo_cliente' : 'Cliente Autorizou?',
                    'type_solicitacao' : 'Tipo da Solicitação',
                    'arquivado' : 'Arquivado',
                    'solicitado' : 'Solicitado Por:',
                    'executado' : 'Executado por:'
                }, axis=1)
                
                df2.to_excel(writer, sheet_name='Ordens de Serviços', index = False)
                writer.sheets['Ordens de Serviços'].set_column('A:A', 8, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('B:C', 16, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('D:E', 60, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('F:F', 75, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('G:M', 14, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('N:O', 35, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('P:Q', 17, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('R:R', 18, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('S:S', 15, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('T:T', 65, alignCenter)
                
                writer.close()
                
                mes = date.today().strftime('%m')
                
                filename = f'PlanilhaOrdens_{mes}.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response

        except Exception as err:
            raise Exception(err)

    def update_ordem_servico(self, cleaned_data, user, empresa_db):
        try:
            cd_servico, servicoDesc = cleaned_data.get('servico').split(" * ")
            
            if cleaned_data.get('id_ordem'):
                ordem = OrdemServico.objects.get(id=cleaned_data.get('id_ordem'))
                ordem.cd_servico = cd_servico
                ordem.servico = servicoDesc
                ordem.ds_servico = cleaned_data.get('descricao')
                ordem.observacoes_servico = cleaned_data.get('descricao_servico')
                ordem.data_realizado = cleaned_data.get('data')
                ordem.data_cobranca = cleaned_data.get('data_cobranca')
                ordem.quantidade = cleaned_data.get('quantidade')
                ordem.hora_trabalho = self.validar_tempo_execucao(cleaned_data.get('execucao'))
                ordem.valor = cleaned_data.get('valor')
                ordem.autorizado_pelo_cliente = cleaned_data.get('autorizacao')
                ordem.type_solicitacao = cleaned_data.get('solicitacaoLocal')
                ordem.solicitado = cleaned_data.get('solicitacao')
                ordem.executado = cleaned_data.get('executado')
                ordem.empresa = empresa_db
            else:
                ordem = OrdemServico(
                    cd_servico = cd_servico,
                    servico = servicoDesc,
                    ds_servico = cleaned_data.get('descricao'),
                    observacoes_servico = cleaned_data.get('descricao_servico'),
                    data_realizado = cleaned_data.get('data'),
                    data_cobranca = cleaned_data.get('data_cobranca'),
                    quantidade = cleaned_data.get('quantidade'),
                    hora_trabalho = self.validar_tempo_execucao(cleaned_data.get('execucao')),
                    valor = cleaned_data.get('valor'),
                    autorizado_pelo_cliente = cleaned_data.get('autorizacao'),
                    type_solicitacao = cleaned_data.get('solicitacaoLocal'),
                    solicitado = cleaned_data.get('solicitacao'),
                    executado = cleaned_data.get('executado'),
                    criador_os = user,
                    empresa = empresa_db
                )
                if cleaned_data.get('typeCreate') == 'ARQUIVADO':
                    ordem.arquivado = True
        except Exception as err:
            raise err
        else:
            ordem.save()
            if cleaned_data.get('id_ordem'):
                preco = float(ordem.valor)
                preco_convertido = f"R$ {preco:_.2f}"
                preco_final = preco_convertido.replace('.',',').replace('_','.')
                return JsonResponse({
                    'empresa': f"{ordem.empresa.cd_empresa} - {ordem.empresa.name_empresa}",
                    'servico': ordem.servico,
                    'ds_servico': ordem.ds_servico,
                    'cobranca': ordem.data_cobranca.strftime("%d/%m/%Y"),
                    'valor': preco_final,
                    'quantidade': ordem.quantidade,
                })
            else:
                return JsonResponse({})
            
    def validar_tempo_execucao(self, execucao):
        if not ':' in execucao:
            return execucao.zfill(2)+':00'
        else:
            hora, minuto = execucao.split(":")
            return hora.zfill(2)+':'+minuto.zfill(2)
    
    def debitar_omie_ordem_servico(self, id_ordem):
        categoria_reembolsavel = {'501': '1.05.99', '502': '1.05.99', '505': '1.06.99', '567': '1.05.99', '575': '1.05.99'}
        try:
            ordem = OrdemServico.objects.get(id=id_ordem)
            if ordem.arquivado or ordem.cod_os_omie:
                raise Exception("Esta Ordem não pode ser Lançada, pois já tem lançamento ou está Arquivada !!")
            
            data_get_os = get_request_to_api_omie(ordem.empresa.escritorio, "ListarOS", {"pagina": 1, "registros_por_pagina": 3, "filtrar_por_etapa": "20", "filtrar_por_cliente": ordem.empresa.codigo_cliente_omie})
            result_os = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_get_os, headers={'content-type': 'application/json'})
            json_os = result_os.json()
            if result_os.status_code == 200:
                if json_os.get("total_de_registros") > 1 or json_os.get("total_de_registros") == 0:
                    raise Exception("Nenhuma ou Mais de Uma OS registrada nesta Etapa !!")
                os_api_omie = json_os.get("osCadastro")[0]
                if not os_api_omie['InfoCadastro']['cCancelada'] == "S":
                    os_api_omie['Cabecalho']['cCodParc'] = "999"
                    try:
                        nSeqItemOrigem = max([n['nSeqItem'] for n in os_api_omie['ServicosPrestados']])+1
                        os_api_omie['ServicosPrestados'] = []
                        nSeqItem = max([n['nSeqItem'] for n in os_api_omie['ServicosPrestados']])+1 if len(os_api_omie['ServicosPrestados']) > 0 else nSeqItemOrigem

                        if ordem.cd_servico == 0:
                            raise Exception("Serviço desta OS está Zerado, ou seja, sem Serviço Adicionado !!")

                        if ordem.cd_servico:
                            new_service_prested = {"nCodServico": ordem.cd_servico, "nQtde": ordem.quantidade, "nValUnit": ordem.valor, "cDescServ": ordem.ds_servico, "nSeqItem": nSeqItem, "cAcaoItem": "I"}
                            if ordem.empresa.escritorio == '501':
                                new_service_prested["impostos"] = {'cRetemCOFINS': 'S', 'cRetemCSLL': 'S', 'cRetemIRRF': 'S', 'cRetemPIS': 'S'}
                            os_api_omie['ServicosPrestados'].append(new_service_prested)
                        else:
                            if 'REEMBOLSO' in ordem.servico:
                                if 'despesasReembolsaveis' in os_api_omie:
                                    os_api_omie['despesasReembolsaveis']['cCodCategReemb'] = categoria_reembolsavel[ordem.empresa.escritorio]
                                    os_api_omie['despesasReembolsaveis']['despesaReembolsavel'].append({"cDescReemb": ordem.ds_servico, "dDataReemb": os_api_omie['Cabecalho']['dDtPrevisao'], "nValorReemb": ordem.valor, "cAcaoReemb": "I"})
                                else:
                                    os_api_omie['despesasReembolsaveis'] = {
                                        "cCodCategReemb": categoria_reembolsavel[ordem.empresa.escritorio],
                                        "despesaReembolsavel": [{"cDescReemb": ordem.ds_servico, "dDataReemb": os_api_omie['Cabecalho']['dDtPrevisao'], "nValorReemb": ordem.valor, "cAcaoReemb": "I"}]
                                    }
                            else:
                                raise Exception("Erro ao Verificar o Lançamento de REEMBOLSO !!")
                        
                        ordem.cod_os_omie = str(os_api_omie['Cabecalho']['nCodOS'])
                        up = self.atualizar_os_omie(ordem.empresa.escritorio, os_api_omie)
                    except Exception as err:
                        raise Exception(f"Erro ao Atualizar Esta OS: N: {os_api_omie['Cabecalho']['cNumOS']} / Erro: {str(err)}")
                    else:
                        if up:
                            ordem.save()
                else:
                    raise Exception(f"OS Num. {os_api_omie['Cabecalho']['cNumOS']} Cancelada !")
            else:
                error_text = json_os.get('message') or json_os.get('faultstring')
                raise Exception(f"Erro na API da OMIE ao Buscar esta OS, Err: {error_text}")
            
        except Exception as err:
            raise Exception(err)
        
    def buscar_os_list_omie(self, escritorio):
        list_os = []
        errors = []
        page_os = 1
        while True:
            data_get_os = get_request_to_api_omie(escritorio, "ListarOS", {"pagina": page_os, "registros_por_pagina": 500, "filtrar_por_etapa": "20"})
            result_os = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_get_os, headers={'content-type': 'application/json'})
            json_os = result_os.json()
            if result_os.status_code == 200:
                list_os.extend(json_os.get("osCadastro"))
                if json_os.get("total_de_paginas") == page_os:
                    break
            else:
                error_text = json_os.get('message') or json_os.get('faultstring')
                errors.append([escritorio, f"Erro na API da OMIE ao Buscar as OS na Página {page_os}, ou Nenhuma OS Encontrada Nesta Etapa / Err: {error_text}"])
                break
            page_os += 1
            time.sleep(0.7)
        return list_os, errors
        
    def atualizar_os_omie(self, escritorio, new_os):
        data_update_os = get_request_to_api_omie(escritorio, "AlterarOS", new_os)
        result = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_update_os, headers={'content-type': 'application/json'})
        json_result = result.json()
        if result.status_code == 200:
            return True
        else:
            error_text = json_result.get('message') or json_result.get('faultstring')
            raise Exception(f"OS Não Alterada: {error_text}")
            
    def debitar_em_lote_ordem_servico(self, type_lanc, list_ordens, file, datas, escritorio_lote):
        sucessos = []
        errors = []
        erros_gerais = []
        categoria_reembolsavel = {'501': '1.05.99', '502': '1.05.99', '505': '1.06.99', '567': '1.05.99', '575': '1.05.99'}
        try:
            validation_clientes_lancamento = set()
            orders_list_set = set()
            os_list_separado_por_escritorios = {}
            
            if type_lanc == 'datas':
                os_list_db = OrdemServico.objects.filter(data_cobranca__range=datas, empresa__escritorio__in=escritorio_lote, arquivado=False, cod_os_omie__isnull=True)
                for os_db in os_list_db:
                    if os_db.cd_servico == '0':
                        errors.append([os_db.id, os_db.empresa.cd_empresa, os_db.empresa.name_empresa, os_db.empresa.cnpj_cpf, os_db.empresa.escritorio, f"OS Sem Serviço Corretamente ALocado, Veja Novamente e Trate o Serviço !!"])
                    else:
                        orders_list_set.add(os_db)
            else:
                orders_list_id = set()
                for os in list_ordens:
                    orders_list_id.add(int(os))
                
                # if file:
                #     df = pd.read_excel(file)
                #     if 'id' in df.columns:
                #         for id_os in df.get("id").values.tolist():
                #             orders_list_id.add(id_os)
                        
                for os_livres in OrdemServico.objects.filter(id__in=orders_list_id):
                    if os_livres.cd_servico == '0':
                        errors.append([os_livres.id, os_livres.empresa.cd_empresa, os_livres.empresa.name_empresa, os_livres.empresa.cnpj_cpf, os_livres.empresa.escritorio, f"OS Sem Serviço Corretamente ALocado, Veja Novamente e Trate o Serviço !!"])
                    else:
                        orders_list_set.add(os_livres)

            for os_to_update in orders_list_set:
                escritorio_desta_os = os_to_update.empresa.escritorio
                cliente_desta_os = os_to_update.empresa.codigo_cliente_omie
                if escritorio_desta_os in os_list_separado_por_escritorios:
                    if cliente_desta_os in os_list_separado_por_escritorios[escritorio_desta_os]:
                        os_list_separado_por_escritorios[escritorio_desta_os][cliente_desta_os].append(os_to_update)
                    else:
                        os_list_separado_por_escritorios[escritorio_desta_os][cliente_desta_os] = [os_to_update]
                else:
                    os_list_separado_por_escritorios[escritorio_desta_os] = {cliente_desta_os: [os_to_update]}

            for codigo_escritorio in os_list_separado_por_escritorios.keys():
                clientes_escritorio = os_list_separado_por_escritorios[codigo_escritorio].keys()
                list_os_omie, errors_api = self.buscar_os_list_omie(codigo_escritorio)
                erros_gerais.extend(errors_api)
                for os_api_omie in list_os_omie:
                    cliente_omie = str(os_api_omie['Cabecalho']['nCodCli'])
                    if cliente_omie in clientes_escritorio:
                        if os_api_omie['InfoCadastro']['cCancelada'] == "S":
                            erros_gerais.append([codigo_escritorio, f"OS: {os_api_omie['Cabecalho']['nCodOS']} / N: {os_api_omie['Cabecalho']['cNumOS']}, cliente: {cliente_omie} está cancelada !!"])
                            continue
                        os_api_omie['Cabecalho']['cCodParc'] = "999"
                        validation_clientes_lancamento.add(cliente_omie)
                        try:
                            list_os_lancadas = []
                            nSeqItemOrigem = max([n['nSeqItem'] for n in os_api_omie['ServicosPrestados']])+1
                            os_api_omie['ServicosPrestados'] = []
                            for os_db_lancamento in os_list_separado_por_escritorios[codigo_escritorio][cliente_omie]:
                                try:
                                    nSeqItem = max([n['nSeqItem'] for n in os_api_omie['ServicosPrestados']])+1 if len(os_api_omie['ServicosPrestados']) > 0 else nSeqItemOrigem
                                    
                                    if os_db_lancamento.cd_servico:
                                        new_service_prested = {"nCodServico": os_db_lancamento.cd_servico, "nQtde": os_db_lancamento.quantidade, "nValUnit": os_db_lancamento.valor, "cDescServ": os_db_lancamento.ds_servico, "nSeqItem": nSeqItem, "cAcaoItem": "I"}
                                        if codigo_escritorio == '501':
                                            new_service_prested["impostos"] = {'cRetemCOFINS': 'S', 'cRetemCSLL': 'S', 'cRetemIRRF': 'S', 'cRetemPIS': 'S'}
                                        os_api_omie['ServicosPrestados'].append(new_service_prested)
                                    else:
                                        if 'REEMBOLSO' in os_db_lancamento.servico:
                                            if 'despesasReembolsaveis' in os_api_omie:
                                                os_api_omie['despesasReembolsaveis']['cCodCategReemb'] = categoria_reembolsavel[codigo_escritorio]
                                                os_api_omie['despesasReembolsaveis']['despesaReembolsavel'].append({"cDescReemb": os_db_lancamento.ds_servico, "dDataReemb": os_api_omie['Cabecalho']['dDtPrevisao'], "nValorReemb": os_db_lancamento.valor, "cAcaoReemb": "I"})
                                            else:
                                                os_api_omie['despesasReembolsaveis'] = {
                                                    "cCodCategReemb": categoria_reembolsavel[codigo_escritorio],
                                                    "despesaReembolsavel": [{"cDescReemb": os_db_lancamento.ds_servico, "dDataReemb": os_api_omie['Cabecalho']['dDtPrevisao'], "nValorReemb": os_db_lancamento.valor, "cAcaoReemb": "I"}]
                                                }
                                        else:
                                            errors.append([os_db_lancamento.id, os_db_lancamento.empresa.cd_empresa, os_db_lancamento.empresa.name_empresa, os_db_lancamento.empresa.cnpj_cpf, codigo_escritorio, f"Erro ao Verificar o Lançamento de REEMBOLSO !!"])
                                            continue
                                    
                                    os_db_lancamento.cod_os_omie = str(os_api_omie['Cabecalho']['nCodOS'])
                                    list_os_lancadas.append(os_db_lancamento)
                                except Exception as err:
                                    errors.append([os_db_lancamento.id, os_db_lancamento.empresa.cd_empresa, os_db_lancamento.empresa.name_empresa, os_db_lancamento.empresa.cnpj_cpf, codigo_escritorio, f"Erro ao Lançar Esta OS: {str(err)}"])
                            
                            up = self.atualizar_os_omie(codigo_escritorio, os_api_omie)
                        except Exception as err:
                            erros_gerais.append([codigo_escritorio, f"Erro ao Atualizar Esta OS: {os_api_omie['Cabecalho']['nCodOS']} / N: {os_api_omie['Cabecalho']['cNumOS']}, cliente: {cliente_omie} / Erro: {str(err)}"])
                        else:
                            if up:
                                for order in list_os_lancadas:
                                    order.save()
                                sucessos.append([str(os_api_omie['Cabecalho']['nCodOS']), codigo_escritorio])
                    else:
                        continue
                    
                for codigo_cliente_validation in clientes_escritorio:
                    if codigo_cliente_validation not in validation_clientes_lancamento:
                        erros_gerais.append([codigo_escritorio, f"Esta Empresa ({codigo_cliente_validation}) não teve suas OS Lançadas, pois não foi encontrado este Cliente na Etapa 20 da API da OMIE, contate a INOVAÇÃO !"])
                    else:
                        continue
                
        except Exception as err:
            raise Exception(err)
        else:
            return sucessos, errors, erros_gerais

    def gerar_arquivo_excel_auditoria_debitos(self, dfSucessos, dfErros, dfErrosGerais):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignLeft = workbook.add_format({'align': 'left'})

                if not dfSucessos.empty:
                    dfSucessos.to_excel(writer, sheet_name='Sucesso', index=False)
                    writer.sheets['Sucesso'].set_column('A:A', 20, alignLeft)
                    writer.sheets['Sucesso'].set_column('B:B', 80, alignLeft)

                if not dfErros.empty:
                    dfErros.to_excel(writer, sheet_name='ERROS', index=False)
                    writer.sheets['ERROS'].set_column('A:B', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('C:C', 55, alignLeft)
                    writer.sheets['ERROS'].set_column('D:E', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('F:F', 120, alignLeft)
                    
                if not dfErrosGerais.empty:
                    dfErrosGerais.to_excel(writer, sheet_name='ERROS GERAIS', index=False)
                    writer.sheets['ERROS GERAIS'].set_column('A:A', 20, alignLeft)
                    writer.sheets['ERROS GERAIS'].set_column('B:B', 80, alignLeft)

                writer.close()
                
                b.seek(0)
                excel_base64 = base64.b64encode(b.read()).decode('utf-8')
                return {
                    'filename': "Auditoria de Débito de OS em Lotes",
                    'file': excel_base64
                }
        except Exception as err:
            raise Exception(err)
        
    def update_empresas_for_omie(self, empresas_request, escrit_list):
        self.manager.default_connect_tareffa()
        self.manager.connect()
        response = {'errors': []}
        try:
            escritorios = escrit_list if escrit_list else ['501', '502', '505', '567', '575']
            empresas = { i[3]: list(i) for i in self.manager.run_query_for_select(get_cnpj_empresas(empresas_request))}
            if empresas_request:
                for cnpj_empresa_req in empresas:
                    for escrit in escritorios:
                        data_get_contrato_omie = get_request_to_api_omie(escrit, "ListarContratos", { "pagina": 1, "registros_por_pagina": 5, "cExibeObs": "N", "cExibirProdutos": "N", "cExibirInfoCadastro": "N", "filtrar_cnpj_cpf": cnpj_empresa_req })
                        result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/contrato/", json=data_get_contrato_omie, headers={'content-type': 'application/json'})
                        json_contrato = result_contrato.json()
                        if result_contrato.status_code == 200:
                            contrato = json_contrato.get("contratoCadastro")[0]
                            if contrato['cabecalho']['cCodSit'] == '10':
                                time.sleep(0.2)
                                data_get_client_omie = get_request_to_api_omie(escrit, "ConsultarCliente", {"codigo_cliente_omie": contrato['cabecalho']['nCodCli']})
                                result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                                json_client = result_client.json()
                                empresa, razaosocial, estab, cnpj = empresas[cnpj_empresa_req]
                                if result_client.status_code == 200:
                                    email = json_client['email'] if 'email' in json_client else ""
                                    cd_omie_empresa = json_client.get("codigo_cliente_omie")
                                    try:
                                        enterprise, _ = EmpresasOmie.objects.get_or_create( cnpj_cpf = cnpj )
                                        enterprise.escritorio = escrit
                                        enterprise.cd_empresa = empresa
                                        enterprise.estab = estab
                                        enterprise.name_empresa = razaosocial
                                        enterprise.codigo_cliente_omie = cd_omie_empresa
                                        enterprise.email = email
                                        enterprise.save()
                                    except Exception as err:
                                        response['errors'].append(f"Erro ao Criar a Empresa: ({cnpj}) Cliente: {cd_omie_empresa} Empresa: {empresa}/{estab} | Erro:{str(err)}")
                                    finally:
                                        break
                                else:
                                    error_text = json_client.get('message') or json_client.get('faultstring')
                                    response['errors'].append(f"Erro ao Buscar este Cliente ({empresa} - {estab}) do Escritório: {escrit} | Erro: {error_text}")
                                    break
                        time.sleep(0.7)
            else:
                for escrit in escritorios:
                    page = 1
                    while True:
                        data_get_contrato_omie = get_request_to_api_omie(escrit, "ListarContratos", { "pagina": page, "registros_por_pagina": 500, "cExibeObs": "N", "cExibirProdutos": "N", "cExibirInfoCadastro": "N" })
                        result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/contrato/", json=data_get_contrato_omie, headers={'content-type': 'application/json'})
                        json_contrato = result_contrato.json()
                        if result_contrato.status_code == 200:
                            codigos_client = set([i['cabecalho']['nCodCli'] for i in json_contrato['contratoCadastro'] if i['cabecalho']['cCodSit'] == '10'])
                            for client in codigos_client:
                                time.sleep(0.2)
                                data_get_client_omie = get_request_to_api_omie(escrit, "ConsultarCliente", {"codigo_cliente_omie": client})
                                result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                                json_client = result_client.json()
                                if result_client.status_code == 200:
                                    email = json_client['email'] if 'email' in json_client else ""
                                    cnpj_cpf = json_client['cnpj_cpf']
                                    if cnpj_cpf in empresas:
                                        try:
                                            empresa, razaosocial, estab, cnpj = empresas[cnpj_cpf]
                                            enterprise, _ = EmpresasOmie.objects.get_or_create( cnpj_cpf = cnpj )
                                            enterprise.escritorio = escrit
                                            enterprise.cd_empresa = empresa
                                            enterprise.estab = estab
                                            enterprise.name_empresa = razaosocial
                                            enterprise.codigo_cliente_omie = client
                                            enterprise.email = email
                                            enterprise.save()
                                        except Exception as err:
                                            response['errors'].append(f"Erro ao Criar a Empresa: ({cnpj}) Cliente: {client} Empresa: {empresa}/{estab} | Erro:{str(err)}")
                                    else:
                                        response['errors'].append(f"Este CNPJ/CPF não se encontra em nosso Banco: {cnpj_cpf} Escritório: {escrit} Cliente: {client} - {json_client['razao_social']}")
                                else:
                                    error_text = json_client.get('message') or json_client.get('faultstring')
                                    response['errors'].append(f"Erro ao Buscar este Cliente ({client}) do Escritório: {escrit} | Erro: {error_text}")
                                
                            if json_contrato.get("total_de_paginas") == page:
                                break
                        else:
                            error_text = json_contrato.get('message') or json_contrato.get('faultstring')
                            response['errors'].append(f"Erro ao Buscar os Contratos deste Escritório: {escrit}, Página: {page} | Erro: {error_text}")
                            break
                        
                        page += 1
                        time.sleep(0.5)
        except Exception as err:
            raise Exception(err)
        else:
            return response
        finally:
            self.manager.disconnect()
    
    def gerar_boletos_por_escritorio(self, escritorio, file, filename):
        response_data = {"errors": [], "files": {}}
        list_os = {}
        list_clients_db = EmpresasOmie.objects.all()
        if file:
            df_os = pd.read_excel(file.temporary_file_path(), sheet_name='ERROS')
            for row in df_os.values.tolist():
                list_os[row[0]] = {'numOS': row[1]}
        else:
            data_get_os = get_request_to_api_omie(escritorio, "ListarOS", {"pagina": 1, "filtrar_por_etapa": "20", "registros_por_pagina": 500})
            result_os = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_get_os, headers={'content-type': 'application/json'})
            json_os = result_os.json()
            if result_os.status_code == 200:
                for os_request in json_os['osCadastro']:
                    if not os_request['InfoCadastro']['cCancelada'] == "S":
                        list_os[os_request['Cabecalho']['nCodOS']] = {'numOS': os_request['Cabecalho']['cNumOS']}
            else:
                raise Exception(f"Erro ao Buscar as OS na API: {json_os}")

        data_get_contas = get_request_to_api_omie(escritorio, "ListarContasReceber", {"pagina": 1, "registros_por_pagina": 500, "filtrar_apenas_titulos_em_aberto": "S"})
        result_contas = requests.post("https://app.omie.com.br/api/v1/financas/contareceber/", json=data_get_contas, headers={'content-type': 'application/json'})
        json_contas = result_contas.json()
        if result_contas.status_code == 200:
            for conta_request in json_contas['conta_receber_cadastro']:
                if 'nCodOS' in conta_request:
                    cod_os = conta_request['nCodOS']
                    if cod_os in list_os:
                        list_os[cod_os]['cd_titulo'] = conta_request['codigo_lancamento_omie']
                        list_os[cod_os]['cd_cliente'] = conta_request['codigo_cliente_fornecedor']
        else:
            raise Exception(f"Erro ao Buscar as Contas a Receber na API: {json_contas}")
        
        for os in list_os:
            obj_os = list_os[os]
            num_os = obj_os['numOS']
            if 'cd_titulo' not in obj_os:
                response_data['errors'].append([os, num_os, "", "", "Não foi Encontrado o Código do Título (Sem Conta a Receber) para Gerar o Boleto"])
                continue
            cd_titulo = obj_os['cd_titulo']
            cd_cliente = obj_os['cd_cliente']
            cliente = list_clients_db.filter(codigo_cliente_omie=cd_cliente).first()
            if not cliente:
                response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, "Cliente Não Encontrado na nossa Base de Bados, Atualize !!"])
                continue
            
            filename_os = str(cliente.cd_empresa).zfill(3) + f"{f'-{cliente.estab}' if int(cliente.estab) > 1 else ''}" + f" - {filename}.pdf"
            new_pdf = fitz.open()
            try:
                url_boleto = ""
                # TENTAR OBTER BOLETO
                data_get_boleto = get_request_to_api_omie(escritorio, "ObterBoleto", {"nCodTitulo": cd_titulo})
                result_obter_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_get_boleto, headers={'content-type': 'application/json'})
                json_obter_boleto = result_obter_boleto.json()
                if result_obter_boleto.status_code == 200:
                    if json_obter_boleto['cCodStatus'] == "0":
                        url_boleto = json_obter_boleto['cLinkBoleto']
                else:
                    raise Exception(f"Erro na API, rota de ObterBoleto: {json_obter_boleto}")
                
                if "https" not in url_boleto:
                    # GERAR BOLETO
                    data_gerar_boleto = get_request_to_api_omie(escritorio, "GerarBoleto", {"nCodTitulo": cd_titulo})
                    result_gerar_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_gerar_boleto, headers={'content-type': 'application/json'})
                    json_gerar_boleto = result_gerar_boleto.json()
                    if result_gerar_boleto.status_code == 200:
                        if json_gerar_boleto['cCodStatus'] == "0":
                            if "https" not in json_gerar_boleto['cLinkBoleto']:
                                raise Exception(f"Não Veio a URL na ROTA GERANDO O BOLETO: {json_gerar_boleto['cDesStatus']}")
                            else:
                                url_boleto = json_gerar_boleto['cLinkBoleto']
                        else:
                            raise Exception(f"Erro na API, rota de GERAR BOLETO, Não Gerou o Boleto pelo Motivo: {json_gerar_boleto['cDesStatus']}")
                    else:
                        raise Exception(f"Erro na API, rota de GERAR BOLETO: {json_gerar_boleto}")
                
                if "https" in url_boleto:
                    r = requests.get(url_boleto, timeout=25)
                    if r.status_code == 200:
                        try:
                            pdf_doc = fitz.open(stream=r.content, filetype="pdf")
                            try:
                                new_pdf.insert_pdf(pdf_doc)
                            except Exception as err:
                                raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
                            finally:
                                pdf_doc.close()
                        except Exception as err:
                            raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
                    else:
                        raise Exception(f"Erro no momento de requisitar o PDF")
                else:
                    raise Exception(f"Por algum motivo mesmo depois de buscar ou gerar, está sem URL")
                
                if new_pdf.page_count > 0:
                    data_get_pdf_os = get_request_to_api_omie(escritorio, "ObterOS", {"nIdOs": os})
                    result_obter_pdf_os = requests.post("https://app.omie.com.br/api/v1/servicos/osdocs/", json=data_get_pdf_os, headers={'content-type': 'application/json'})
                    json_obter_pdf_os = result_obter_pdf_os.json()
                    if result_obter_pdf_os.status_code == 200:
                        if json_obter_pdf_os['cCodStatus'] == "0" and "https" in json_obter_pdf_os['cPdfOs']:
                            r = requests.get(json_obter_pdf_os['cPdfOs'], timeout=25)
                            if r.status_code == 200:
                                try:
                                    pdf_doc = fitz.open(stream=r.content, filetype="pdf")
                                    try:
                                        new_pdf.insert_pdf(pdf_doc)
                                    except Exception as err:
                                        raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
                                    finally:
                                        pdf_doc.close()
                                except Exception as err:
                                    raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
                            else:
                                raise Exception(f"Erro no momento de requisitar o PDF da OS")
                        else:
                            raise Exception(f"Rota de ObterOS, Erro pelo Código: {json_obter_pdf_os}")
                    else:
                        raise Exception(f"Erro na API, rota de ObterOS: {json_obter_pdf_os}")
                else:
                    raise Exception(f"Não Gerou PDF da OS, pois Não gerou o Boleto para")
                
            except Exception as err:
                response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, f"Erro ao Gerar o PDF: {str(err)}"])
            else:
                if new_pdf.page_count > 0:
                    response_data['files'][filename_os] = new_pdf.write()
                else:
                    response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, "PDF VAZIO !!"])
            finally:
                new_pdf.close()
        
        return response_data
    
    def gerar_arquivo_excel_auditoria_download_boletos(self, dfErros):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignLeft = workbook.add_format({'align': 'left'})

                if not dfErros.empty:
                    dfErros.to_excel(writer, sheet_name='ERROS', index=False)
                    writer.sheets['ERROS'].set_column('A:D', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('E:E', 100, alignLeft)

                writer.close()
                
                b.seek(0)
                return b.getvalue()
        except Exception as err:
            raise Exception(err)