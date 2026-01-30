from datetime import datetime, date
from io import BytesIO
import csv
import requests
import base64
import pandas as pd
import fitz
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
                        ordem['cd_empresa'] = empresa.get('cd_empresa')
                        ordem['nome_empresa'] = empresa.get('name_empresa')
                    del ordem['_state']
                    del ordem['criador_os']
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
                    'cd_empresa' : 'Cd. Empresa',
                    'nome_empresa' : 'Nome Empresa',
                    'data_realizado' : 'Data Realizado',
                    'data_cobranca' : 'Data de Cobrança',
                    'quantidade' : 'Qauntidade',
                    'hora_trabalho' : 'Horas',
                    'valor' : 'Valor',
                    'autorizado_pelo_cliente' : 'Cliente Autorizou?',
                    'type_solicitacao' : 'Tipo da Solicitação',
                    'solicitado' : 'Solicitado Por:',
                    'executado' : 'Executado por:'
                }, axis=1)
                
                df2.to_excel(writer, sheet_name='Ordens de Serviços', index = False)
                writer.sheets['Ordens de Serviços'].set_column('A:A', 8, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('B:C', 15, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('D:E', 55, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('F:F', 70, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('G:G', 12, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('H:H', 60, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('I:M', 14, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('N:O', 20, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('P:Q', 60, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('R:R', 10, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('S:T', 18, alignCenter)
                
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
        try:
            pass
            # ordem = OrdemServico.objects.get(id=id_ordem)
            # if debitar:
            #     pass
            # elif not ordem.arquivado and ordem.ordem_debitada_id:
            #     ordem.ordem_debitada_id = None
            # elif ordem.debitar and not ordem.ordem_debitada_id:
            #     raise Exception("Esta Ordem não pode ser Excluida, Cancelada e nem Arquivada")
            # else:
            #     pass
                
        except Exception as err:
            raise Exception(err)
        # else:
        #     ordem.save()
            
    def debitar_em_lote_ordem_servico(self, orders_list, file):
        self.manager.connect()
        try:
            sucessos = []
            errors = []
            orders_list_set = set()
            dados_empresa_omie = EmpresasOmie.objects.all()
            os_list = {}
            os_list_escritorios = {}
            
            # for os in orders_list:
            #     orders_list_set.add(int(os))
            
            # if file:
            #     df = pd.read_excel(file)
            #     if 'id' in df.columns:
            #         for id_os in df.get("id").values.tolist():
            #             orders_list_set.add(id_os)
                    
            # ordens = OrdemServico.objects.filter(id__in=orders_list_set)
            
            
            df = pd.read_excel(file)
            df.fillna(0, inplace=True)
            for id_os, cd_servico, servico, ds_servico, observacoes_servico, codigo_escritorio, codigo_servico, cd_empresa, filial, vencimento, nome_empresa, data_realizado, data_cobranca, quantidade, hora_trabalho, valor, autorizado_pelo_cliente, type_solicitacao, solicitado, executado, debitar, arquivado, ordem_debitada_id in df.values.tolist():
                if codigo_escritorio == 9501:
                    print(cd_empresa, filial, codigo_servico)
                    vencimento = vencimento.strftime("%d/%m/%Y")
                    codigo_servico = int(codigo_servico)
                    codigo_escritorio = str(codigo_escritorio).replace("9", "")
                    
                    try:
                        empresa_omie = dados_empresa_omie.get(cd_empresa=cd_empresa, estab=filial)
                        data_get_os = get_request_to_api_omie(codigo_escritorio, "ListarOS", {"pagina": 1, "filtrar_por_cliente": empresa_omie.codigo_cliente_omie, "filtrar_por_etapa": "10", "filtrar_por_data_previsao_de": "02/12/2025"})
                        result_os = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_get_os, headers={'content-type': 'application/json'})
                        json_os = result_os.json()
                        if result_os.status_code == 200:
                            if json_os['total_de_registros'] == 1:
                                os = json_os['osCadastro'][0]
                                cd_os = os['Cabecalho']['nCodOS']
                                os_list_escritorios[cd_os] = codigo_escritorio
                                if cd_os in os_list:
                                    os_exists = os_list[cd_os]
                                    nSeqItem = max([n['nSeqItem'] for n in os_exists['ServicosPrestados']])+1
                                    if codigo_servico != 0:
                                        os_exists['ServicosPrestados'].append({"nCodServico": codigo_servico, "nQtde": quantidade, "nValUnit": valor, "cDescServ": ds_servico, "nSeqItem": nSeqItem, "cAcaoItem": "I", "impostos": {'cRetemCOFINS': 'S', 'cRetemCSLL': 'S', 'cRetemIRRF': 'S', 'cRetemPIS': 'S'}})
                                    else:
                                        if 'despesasReembolsaveis' in os_exists:
                                            os_exists['despesasReembolsaveis']['despesaReembolsavel'].append({"cDescReemb": ds_servico, "dDataReemb": "02/12/2025", "nValorReemb": valor, "cAcaoReemb": "I"})
                                        else:
                                            os_exists['despesasReembolsaveis'] = {
                                                "despesaReembolsavel": [{"cDescReemb": ds_servico, "dDataReemb": "02/12/2025", "nValorReemb": valor, "cAcaoReemb": "I"}]
                                            }
                                else:
                                    nSeqItem = max([n['nSeqItem'] for n in os['ServicosPrestados']])+1
                                    os['Cabecalho']['cCodParc'] = "999"
                                    os['Parcelas'][0]['dDtVenc'] = vencimento
                                    if codigo_servico != 0:
                                        os['ServicosPrestados'] = [{"nCodServico": codigo_servico, "nQtde": quantidade, "nValUnit": valor, "cDescServ": ds_servico, "nSeqItem": nSeqItem, "cAcaoItem": "I", "impostos": {'cRetemCOFINS': 'S', 'cRetemCSLL': 'S', 'cRetemIRRF': 'S', 'cRetemPIS': 'S'}}]
                                    else:
                                        os['despesasReembolsaveis'] = {
                                            "despesaReembolsavel": [{"cDescReemb": ds_servico, "dDataReemb": "02/12/2025", "nValorReemb": valor, "cAcaoReemb": "I"}]
                                        }
                                    os_list[cd_os] = os
                            else:
                                errors.append([id_os, cd_empresa, nome_empresa, empresa_omie.cnpj_cpf, codigo_escritorio, f"Nenhuma ou mais de uma OS na Pesquisa, quantidade: {json_os['total_de_registros']} !"])
                        else:
                            error_text = json_os.get('message') or json_os.get('faultstring')
                            errors.append([id_os, cd_empresa, nome_empresa, empresa_omie.cnpj_cpf, codigo_escritorio, f"Nenhuma OS Encontrada na OMIE, Erro:{error_text}"])
                    except Exception as err:
                        errors.append([id_os, cd_empresa, nome_empresa, "", "", f"Empresa Não Cadastrada Corretamente no Banco | Erro: {str(err)}"])
                            
            print(os_list)
            
            for id_os_omie in os_list:
                print("aaaaaaaaaaa")
                os = os_list[id_os_omie]
                escrit = os_list_escritorios[id_os_omie]
                data_update_os = get_request_to_api_omie(escrit, "AlterarOS", os)
                result = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_update_os, headers={'content-type': 'application/json'})
                json_result = result.json()
                print(json_result)
                if result.status_code == 200:
                    sucessos.append([id_os_omie, escrit])
                else:
                    error_text = json_result.get('message') or json_result.get('faultstring')
                    errors.append([id_os_omie, escrit, "", "", "", f"OS Não Alterada: {error_text}"])
                
                    # if not cd_empresa in dados_empresa_omie:
                    #     if int(cd_empresa) > 99999:
                    #         codigo_escritorio = 9505
                    #     else:
                    #         codigo_escritorio = get_codigo_escritorio(cd_empresa, self.manager.cursor)
                        
                    #     if codigo_escritorio:
                    #         codigo_escritorio = str(codigo_escritorio).replace("9", "")
                    #         cnpj = get_cnpj_empresa(cd_empresa, self.manager.cursor)
                    #         if cnpj:
                    #             params_client = {
                    #                 "pagina": 1,
                    #                 "registros_por_pagina": 10,
                    #                 "clientesFiltro": {
                    #                     "cnpj_cpf": cnpj
                    #                 }
                    #             }
                    #             data_get_client_omie = get_request_to_api_omie(codigo_escritorio, "ListarClientes", params_client)
                    #             result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                    #             json_client = result_client.json()
                    #             if result_client.status_code == 200:
                    #                 if json_client['total_de_registros'] == 1:
                    #                     client = json_client['clientes_cadastro'][0]
                    #                     email = client['email'] if 'email' in client else ""
                    #                     dados_empresa_omie[cd_empresa] = {
                    #                         'cnpj': cnpj,
                    #                         'razao_social': client['razao_social'],
                    #                         'codigo_cliente_omie': client['codigo_cliente_omie'],
                    #                         'email': email
                    #                     }
                    #                 else:
                    #                     errors.append([id_os, cd_empresa, nome_empresa, cnpj, codigo_escritorio, f"Nenhum ou Mais de um Código Omie para o mesmo CNPJ: {cnpj}, total: {json_client['total_de_registros']}"])
                    #                     dados_empresa_omie[cd_empresa] = None
                    #                     continue
                    #             else:
                    #                 error_text = json_client.get('message') or json_client.get('faultstring')
                    #                 errors.append([id_os, cd_empresa, nome_empresa, cnpj, codigo_escritorio, f"Erro ao Buscar o Código do Cliente: {error_text}"])
                    #                 dados_empresa_omie[cd_empresa] = None
                    #                 continue
                    #         else:
                    #             errors.append([id_os, cd_empresa, nome_empresa, "", codigo_escritorio, "CNPJ desta Empresa Não Encontrado"])
                    #             dados_empresa_omie[cd_empresa] = None
                    #             continue
                    #     else:
                    #         errors.append([id_os, cd_empresa, nome_empresa, "", "", "Código do Escritório Não Encontrado"])
                    #         dados_empresa_omie[cd_empresa] = None
                    #         continue
                    
                    # if not dados_empresa_omie[cd_empresa]:
                    #     errors.append([id_os, cd_empresa, nome_empresa, "", "", "Erro Na Empresa Desta OS !"])
                    #     continue
                    
                # break
                
        except Exception as err:
            raise Exception(err)
        else:
            return sucessos, errors
        finally:
            self.manager.disconnect()

    def gerar_arquivo_excel_auditoria_debitos(self, dfSucessos, dfErros):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignLeft = workbook.add_format({'align': 'left'})

                if not dfSucessos.empty:
                    dfSucessos.to_excel(writer, sheet_name='Sucesso', index=False)
                    writer.sheets['Sucesso'].set_column('A:B', 22, alignLeft)

                if not dfErros.empty:
                    dfErros.to_excel(writer, sheet_name='ERROS', index=False)
                    writer.sheets['ERROS'].set_column('A:B', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('C:C', 55, alignLeft)
                    writer.sheets['ERROS'].set_column('D:E', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('F:F', 120, alignLeft)

                writer.close()
                
                b.seek(0)
                excel_base64 = base64.b64encode(b.read()).decode('utf-8')
                return {
                    'filename': "Auditoria de Débito de OS em Lotes",
                    'file': excel_base64
                }
        except Exception as err:
            raise Exception(err)
        
    def update_empresas_for_omie(self, empresas_request):
        self.manager.default_connect_tareffa()
        self.manager.connect()
        empresas_list_omie = []
        response = {'errors': []}
        try:
            if empresas_request:
                empresas_list_omie = [int(emp.codigo_cliente_omie) for emp in EmpresasOmie.objects.filter(cd_empresa__in=empresas_request)]
                if not empresas_list_omie:
                    raise Exception("Nenhuma destas Empresas estão cadastradas !!")

            params_contrato = {
                "pagina": 1,
                "registros_por_pagina": 1000
            }
            escritorios = ['501', '502', '505', '567']
            empresas = { i[3]: list(i) for i in self.manager.run_query_for_select(get_cnpj_empresas())}
            for escrit in escritorios:
                data_get_contrato_omie = get_request_to_api_omie(escrit, "ListarContratos", params_contrato)
                result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/contrato/", json=data_get_contrato_omie, headers={'content-type': 'application/json'})
                json_contrato = result_contrato.json()
                if result_contrato.status_code == 200:
                    codigos_client = set([i['cabecalho']['nCodCli'] for i in json_contrato['contratoCadastro'] if i['cabecalho']['cCodSit'] == '10'])
                    if empresas_list_omie:
                        codigos_client = set([c for c in codigos_client if c in empresas_list_omie])
                    for client in codigos_client:
                        data_get_client_omie = get_request_to_api_omie(escrit, "ConsultarCliente", {"codigo_cliente_omie": client})
                        result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                        json_client = result_client.json()
                        if result_client.status_code == 200:
                            email = json_client['email'] if 'email' in json_client else ""
                            cnpj_cpf = json_client['cnpj_cpf']
                            if cnpj_cpf in empresas:
                                try:
                                    empresa, razaosocial, estab, cnpj = empresas[cnpj_cpf]
                                    enterprise, _ = EmpresasOmie.objects.get_or_create( codigo_cliente_omie = client )
                                    enterprise.escritorio = escrit
                                    enterprise.cd_empresa = empresa
                                    enterprise.estab = estab
                                    enterprise.name_empresa = razaosocial
                                    enterprise.cnpj_cpf = cnpj
                                    enterprise.email = email
                                    enterprise.save()
                                except Exception as err:
                                    response['errors'].append(f"Erro ao Criar a Empresa: ({cnpj}) Cliente: {client} Empresa: {empresa}/{estab} | Erro:{str(err)}")
                            else:
                                response['errors'].append(f"Este CNPJ/CPF não se encontra em nosso Banco: {cnpj_cpf} Escritório: {escrit} Cliente: {client}")
                        else:
                            error_text = json_client.get('message') or json_client.get('faultstring')
                            response['errors'].append(f"Erro ao Buscar este Cliente ({client}) do Escritório: {escrit} | Erro: {error_text}")
                else:
                    error_text = json_contrato.get('message') or json_contrato.get('faultstring')
                    response['errors'].append(f"Erro ao Buscar os Contratos deste Escritório: {escrit} | Erro: {error_text}")
        except Exception as err:
            raise Exception(err)
        else:
            return response
        finally:
            self.manager.disconnect()
    
    def gerar_boletos_por_escritorio(self, escritorio, file, filename):
        response_data = {"success": [], "errors": [], "files": {}}
        list_os = {}
        list_clients_db = EmpresasOmie.objects.all()
        if file:
            df_os = pd.read_excel(file.temporary_file_path(), sheet_name='ERROS')
            for os_file in df_os['OS'].values.tolist():
                list_os[os_file] = {}
        else:
            data_get_os = get_request_to_api_omie(escritorio, "ListarOS", {"pagina": 1, "filtrar_por_etapa": "20", "registros_por_pagina": 1000})
            result_os = requests.post("https://app.omie.com.br/api/v1/servicos/os/", json=data_get_os, headers={'content-type': 'application/json'})
            json_os = result_os.json()
            if result_os.status_code == 200:
                for os_request in json_os['osCadastro']:
                    list_os[os_request['Cabecalho']['nCodOS']] = {}
            else:
                raise Exception(f"Erro ao Buscar as OS na API: {json_os}")
                    
        data_get_contas = get_request_to_api_omie(escritorio, "ListarContasReceber", {"pagina": 1, "registros_por_pagina": 1000, "filtrar_apenas_titulos_em_aberto": "S"})
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
            if not obj_os:
                response_data['errors'].append([os, "", "", "Não foi Encontrado o Código do Título (Sem Conta a Receber) para Gerar o Boleto"])
                continue
            cd_titulo = obj_os['cd_titulo']
            cd_cliente = obj_os['cd_cliente']
            cliente = list_clients_db.filter(codigo_cliente_omie=cd_cliente).first()
            if not cliente:
                response_data['errors'].append([os, cd_titulo, cd_cliente, "Cliente Não Encontrado na nossa Base de Bados, Atualize !!"])
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
                response_data['errors'].append([os, cd_titulo, cd_cliente, f"Erro ao Gerar o PDF: {str(err)}"])
            else:
                if new_pdf.page_count > 0:
                    response_data['files'][filename_os] = new_pdf.write()
                else:
                    response_data['errors'].append([os, cd_titulo, cd_cliente, "PDF VAZIO !!"])
            finally:
                new_pdf.close()
        
        return response_data
    
    def gerar_arquivo_excel_auditoria_download_boletos(self, dfSucessos, dfErros):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignLeft = workbook.add_format({'align': 'left'})

                if not dfSucessos.empty:
                    dfSucessos.to_excel(writer, sheet_name='Sucesso', index=False)
                    writer.sheets['Sucesso'].set_column('A:A', 20, alignLeft)
                    writer.sheets['Sucesso'].set_column('B:B', 50, alignLeft)

                if not dfErros.empty:
                    dfErros.to_excel(writer, sheet_name='ERROS', index=False)
                    writer.sheets['ERROS'].set_column('A:C', 20, alignLeft)
                    writer.sheets['ERROS'].set_column('D:D', 100, alignLeft)

                writer.close()
                
                b.seek(0)
                return b.getvalue()
        except Exception as err:
            raise Exception(err)