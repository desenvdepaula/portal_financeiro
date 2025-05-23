from datetime import date
import csv
from django.http import HttpResponse
from .database import Manager
from .models import Empresa, Socio
from .sql import RelatorioFaturamentoServicoSqls
import pandas as pd
from io import BytesIO

class Controller():

    def __init__(self, *args, **kwargs):
        self.inicio_periodo = date(2020, 1, 31)
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)
        
    # ---------- RECUPERAÇÃO DE DADOS BRUTOS ---------- #
    def get_dados_empresa(self, codigo_empresa, codigo_estabelecimento=1):
        self.manager.connect()
        try:
            empresa = Empresa.instance_from_database_args(self.manager.fetchmap(self.manager.get_empresa(codigo_empresa, codigo_estabelecimento), True, True))    
            self.manager.disconnect()
            if not empresa:
                raise Exception("A empresa não foi encontrada")
            return empresa
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()

    def get_dados_socio_administrador(self, codigo_empresa):
        self.manager.connect()
        try:
            socio = self.manager.fetchmap(self.manager.get_socio_administrador(codigo_empresa), True, True) 
            self.manager.disconnect()
            if not socio:
                raise Exception("O sócio administrador não foi encontrado")
            return Socio.instance_from_database_args(socio, True)
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()

    def get_socios(self, codigo_empresa):
        self.manager.connect()
        try:
            socios = self.manager.fetchmap(self.manager.get_socios(codigo_empresa), upperCase=True)
            socios = [ Socio.instance_from_database_args(socio) for socio in socios ]
        except Exception as err:
            raise Exception(err)
        else:
            return socios
        finally:
            self.manager.disconnect()

    def build_planilha_faturamento_servico(self, inicio, fim, codigos_servicos):
        self.manager.connect()
        try:
            sqls = RelatorioFaturamentoServicoSqls(inicio, fim, codigos_servicos)
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                num = workbook.add_format({'num_format':'#,##0.00', 'align': 'left'})
                
                df = pd.read_sql(sqls.get_data(), self.manager.connection)
                dfCodigos = sqls.getClassificationDB(df['CÓDIGO SERVIÇO'].values.tolist())
                df.columns = df.columns.str.upper()
                if not dfCodigos.empty:
                    df = df.merge(dfCodigos, how='left', on='CÓDIGO SERVIÇO')
                df['COMPET'] = df['COMPET'].astype('datetime64')
                df['COMPET'] = df['COMPET'].dt.strftime('%d/%m/%Y')
                df.to_excel(writer, sheet_name='Faturamento', index = False)
                writer.sheets['Faturamento'].set_column('A:C', 20, alignCenter)
                writer.sheets['Faturamento'].set_column('D:D', 70, alignCenter)
                writer.sheets['Faturamento'].set_column('E:E', 15, alignCenter)
                writer.sheets['Faturamento'].set_column('F:F', 15, alignCenter)
                writer.sheets['Faturamento'].set_column('G:G', 45, alignCenter)
                writer.sheets['Faturamento'].set_column('H:H', 15, num)
                writer.sheets['Faturamento'].set_column('I:I', 40, alignCenter)
                writer.sheets['Faturamento'].set_column('J:J', 35, alignCenter)
                
                writer.close()
                
                filename = f'FaturamentoServico_{fim.strftime("%m/%Y")}.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
            
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()