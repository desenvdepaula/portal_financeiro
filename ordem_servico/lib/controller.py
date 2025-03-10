from datetime import datetime, date
from io import BytesIO
import csv
import pandas as pd
from django.http import HttpResponse, JsonResponse
from ..models import OrdemServico
from .database import Manager
from .querys import filter_planilha, get_codigo_escritorio, get_sequencia_variavel_empresa, get_id_ordem_servico, build_insert_os, valid_notas_delete, build_delete_os, sql_get_services_questor

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
    
    #------------------ AUDITORIA 131 ------------------#
    
    def gerarPlanilhasOrdens(self, filtros):
        try:
            results = filter_planilha(filtros)
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                listOrdens = []
                
                for ordem in results:
                    ordem = vars(ordem)
                    del ordem['_state']
                    del ordem['id']
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
                writer.sheets['Ordens de Serviços'].set_column('A:B', 15, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('C:D', 30, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('E:E', 70, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('F:F', 12, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('G:G', 60, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('H:L', 14, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('M:N', 20, alignCenter)
                writer.sheets['Ordens de Serviços'].set_column('O:P', 60, alignCenter)
                
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

    def delete_ordem_servico_debitada(self, ordem):
        self.manager.connect()
        try:
            valid = valid_notas_delete(ordem.ordem_debitada_id, self.manager.cursor)
            if not valid['valid']:
                raise Exception(valid['msg'])
            self.manager.cursor.execute(build_delete_os(ordem.ordem_debitada_id))
            self.manager.connection.commit()
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()
            
    def update_ordem_servico(self, cleaned_data, user):
        self.manager.connect()
        try:
            query = self.manager.run_query_for_select(f"select nome from pessoafinanceiro where codigopessoafin = {cleaned_data.get('empresa')}")
            list_nomes = [nome for nome in query]
            if not list_nomes:
                raise Exception(f"Esta Empresa: {cleaned_data.get('empresa')} Não possui nome, Provavelmente não existe, escreva novamente !")
            
            nome_empresa = list(list_nomes[0])[0]
            cd_servico, servicoDesc = cleaned_data.get('servico').split(" * ")
            
            if cleaned_data.get('id_ordem'):
                ordem = OrdemServico.objects.get(id=cleaned_data.get('id_ordem'))
                ordem.cd_servico = cd_servico
                ordem.servico = servicoDesc
                ordem.ds_servico = cleaned_data.get('descricao')
                ordem.observacoes_servico = cleaned_data.get('descricao_servico')
                ordem.cd_empresa = cleaned_data.get('empresa')
                ordem.nome_empresa = nome_empresa
                ordem.data_realizado = cleaned_data.get('data')
                ordem.data_cobranca = cleaned_data.get('data_cobranca')
                ordem.quantidade = cleaned_data.get('quantidade')
                ordem.hora_trabalho = self.validar_tempo_execucao(cleaned_data.get('execucao'))
                ordem.valor = cleaned_data.get('valor')
                ordem.autorizado_pelo_cliente = cleaned_data.get('autorizacao')
                ordem.type_solicitacao = cleaned_data.get('solicitacaoLocal')
                ordem.solicitado = cleaned_data.get('solicitacao')
                ordem.executado = cleaned_data.get('executado')
            else:
                ordem = OrdemServico(
                    cd_servico = cd_servico,
                    servico = servicoDesc,
                    ds_servico = "NULL",
                    observacoes_servico = cleaned_data.get('descricao_servico'),
                    cd_empresa = cleaned_data.get('empresa'),
                    nome_empresa = nome_empresa,
                    data_realizado = cleaned_data.get('data'),
                    data_cobranca = cleaned_data.get('data_cobranca'),
                    quantidade = cleaned_data.get('quantidade'),
                    hora_trabalho = self.validar_tempo_execucao(cleaned_data.get('execucao')),
                    valor = cleaned_data.get('valor'),
                    autorizado_pelo_cliente = cleaned_data.get('autorizacao'),
                    type_solicitacao = cleaned_data.get('solicitacaoLocal'),
                    solicitado = cleaned_data.get('solicitacao'),
                    executado = cleaned_data.get('executado'),
                    criador_os = user
                )
                if cleaned_data.get('typeCreate') == 'DEBITADO':
                    ordem.debitar = True
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
                    'empresa': f"{ordem.cd_empresa} - {ordem.nome_empresa}",
                    'servico': ordem.servico,
                    'ds_servico': ordem.ds_servico,
                    'cobranca': ordem.data_cobranca.strftime("%d/%m/%Y"),
                    'valor': preco_final,
                    'quantidade': ordem.quantidade,
                })
        finally:
            self.manager.disconnect()
            
    def validar_tempo_execucao(self, execucao):
        if not ':' in execucao:
            return execucao.zfill(2)+':00'
        else:
            hora, minuto = execucao.split(":")
            return hora.zfill(2)+':'+minuto.zfill(2)
    
    def debitar_or_delete_ordem_servico(self, id_ordem, debitar, arquivar=False):
        self.manager.connect()
        try:
            ordem = OrdemServico.objects.get(id=id_ordem)
            if debitar:
                if int(ordem.cd_empresa) > 99999:
                    codigo_escritorio = 9505
                else:
                    codigo_escritorio = get_codigo_escritorio(ordem.cd_empresa, self.manager.cursor)
                    
                if not codigo_escritorio:
                    raise Exception("Código do Escritório desta Empresa Não Encontrado")
                sequencia_variavel_empresa = get_sequencia_variavel_empresa(ordem.cd_empresa, ordem.data_cobranca, self.manager.cursor)
                id_ordem_servico = get_id_ordem_servico(self.manager.cursor)
                insert = build_insert_os(id_ordem_servico, ordem, codigo_escritorio, sequencia_variavel_empresa)
                self.manager.cursor.execute(insert)
                returning_id_ordem = self.manager.cursor.fetchone()
                self.manager.connection.commit()
                if returning_id_ordem:
                    ordem.ordem_debitada_id = returning_id_ordem[0] or None
                else:
                    raise Exception("Lançamento não foi realizado")
            elif not ordem.arquivado and ordem.ordem_debitada_id:
                valid = valid_notas_delete(ordem.ordem_debitada_id, self.manager.cursor)
                if not valid['valid']:
                    raise Exception(valid['msg'])
                self.manager.cursor.execute(build_delete_os(ordem.ordem_debitada_id))
                self.manager.connection.commit()
                ordem.ordem_debitada_id = None
            elif ordem.debitar and not ordem.ordem_debitada_id:
                raise Exception("Esta Ordem não pode ser Excluida, Cancelada e nem Arquivada")
            else:
                pass
                
        except Exception as err:
            raise Exception(err)
        else:
            ordem.debitar = debitar
            ordem.arquivado = arquivar
            ordem.save()
        finally:
            self.manager.disconnect()
            
    def debitar_em_lote_ordem_servico(self, orders_list):
        self.manager.connect()
        try:
            ordens = OrdemServico.objects.filter(id__in=orders_list)
            errors = []
            
            for ordem in ordens:
                if int(ordem.cd_empresa) > 99999:
                    codigo_escritorio = 9505
                else:
                    codigo_escritorio = get_codigo_escritorio(ordem.cd_empresa, self.manager.cursor)
                    
                if not codigo_escritorio:
                    errors.append(f"Código do Escritório da Empresa {ordem.cd_empresa} Não Encontrado")
                    continue
                
                sequencia_variavel_empresa = get_sequencia_variavel_empresa(ordem.cd_empresa, ordem.data_cobranca, self.manager.cursor)
                id_ordem_servico = get_id_ordem_servico(self.manager.cursor)
                insert = build_insert_os(id_ordem_servico, ordem, codigo_escritorio, sequencia_variavel_empresa)
                self.manager.cursor.execute(insert)
                returning_id_ordem = self.manager.cursor.fetchone()
                self.manager.connection.commit()
                if returning_id_ordem:
                    ordem.ordem_debitada_id = returning_id_ordem[0] or None
                    ordem.debitar = True
                    ordem.save()
                else:
                    errors.append(f"Lançamento não foi realizado da Empresa {ordem.cd_empresa}, Codigo do Insert não retornado")
                    continue
                
        except Exception as err:
            raise Exception(err)
        else:
            return errors
        finally:
            self.manager.disconnect()