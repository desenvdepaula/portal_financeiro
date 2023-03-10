from datetime import datetime, date
from io import BytesIO
import csv
import pandas as pd
from django.http import HttpResponse
from ..models import OrdemServico
from .database import Manager, ManagerTareffa

class Controller():

    def __init__(self, *args, **kwargs):
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)

    #------------------ AUDITORIA 131 ------------------#
    
    def gerarPlanilhasOrdens(self):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                listOrdens = []
                
                for ordem in OrdemServico.objects.all():
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
    
    def update_ordem_servico(self, cleaned_data):
        try:
            self.manager.connect()
            query = self.manager.execute_sql(f"SELECT NOMEEMPRESA FROM EMPRESA WHERE CODIGOEMPRESA = {cleaned_data.get('empresa')}")
            list_nomes = [nome for nome in query]
            if not list_nomes:
                raise Exception(f"Esta Empresa: {cleaned_data.get('empresa')} Não possui nome, Provavelmente não existe, escreva novamente !")
            
            nome_empresa = list(list_nomes[0])[0]
            cd_servico, servicoDesc = cleaned_data.get('servico').split(" * ")
            
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
            ordem.hora_trabalho = cleaned_data.get('execucao').strftime('%H:%M')
            ordem.valor = cleaned_data.get('valor')
            ordem.autorizado_pelo_cliente = cleaned_data.get('autorizacao')
            ordem.type_solicitacao = cleaned_data.get('solicitacaoLocal')
            ordem.solicitado = cleaned_data.get('solicitacao')
            ordem.executado = cleaned_data.get('executado')
            ordem.save()
            
        except Exception as err:
            raise err
        finally:
            self.manager.disconnect()