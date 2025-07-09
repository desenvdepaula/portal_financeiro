from datetime import datetime
from Database.models import PostgreSQLConnection, SQLServerConnection
from .src.sql import get_recebimentos, get_max_lancamento, get_lancamentos, get_juros
from .src.dict import get_dicionario, get_filial

class Controller(PostgreSQLConnection):
    
    def __init__(self, *args, **kwargs):
        self.default_connect()
        init_args = {'driver': '{ODBC Driver 17 for SQL Server}', 'server': '192.168.1.28,391', 'database': 'nGestaao3', 'uid': 'sa', 'pwd': 'QER159357XT$'}
        self.sqlserver = SQLServerConnection(**init_args)

    def gerarRecebimentosJuros(self, inicio_periodo, fim_periodo, relacao_empresas):
        self.connect()
        self.sqlserver.connect()
        try:
            self.sqlserver.execute_and_commit("SET IDENTITY_INSERT TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS ON")

            dataini = inicio_periodo.strftime('%d.%m.%Y')
            datafim = fim_periodo.strftime('%d.%m.%Y')
            dicescritorio = get_dicionario()
            dicfilial = get_filial()
            
            for codigo_empresa in relacao_empresas:
                contas = relacao_empresas[codigo_empresa]
                escritorio = int(codigo_empresa)

                datadeHoje = datetime.today().strftime('%d/%m/%Y')
                ano = datafim.split(".")[-1]
                codigos = tuple([int(conta) for conta in contas])
                filial = dicfilial[escritorio][0]
                entidade = dicfilial[escritorio][1]

                dadosempresarial = self.sqlserver.execute_sql(get_lancamentos(filial,dataini,datafim))
                conferencia = []
                for i in dadosempresarial:
                    conferencia.append(i)

                cnpj = dicescritorio[escritorio][0]
                query = self.run_query_for_select(get_juros(escritorio,dataini,datafim,codigos))
                array = []

                for i in query:
                    letra = 'NF' if i[3][0] != 'A' else i[3][0]
                    corrente = dicescritorio[escritorio][1][i[2]][letra]['corrente']
                    historico = dicescritorio[escritorio][1][i[2]][letra]['historico']
                    contabil = dicescritorio[escritorio][1][i[2]][letra]['contabil']

                    if i[5] != 0:
                        responseMaximoLancamento = self.sqlserver.execute_sql(get_max_lancamento())
                        for item in responseMaximoLancamento:
                            maximoLancamento = item

                        numero = str(i[3]).replace('F','').split("-")[0]
                        data = str(i[1])+' 00:00:00.000'
                        dataFormat = i[1].strftime('%Y-%d-%m')+' 00:00:00.000'
                        obs = i[4].replace("'",'')
                        if [int(numero),data[:-4]]  not in [[int(r[0]),str(r[1])] for r in conferencia]: 
                            insert = f"""   
                                INSERT INTO nGestaao3.dbo.TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS(CD_LANCAMENTO,CD_ENTIDADE,CD_CONTA_ENTRADA,CD_CONTA_SAIDA,CD_EMPRESA,CD_FILIAL,CD_CONTA_CORRENTE,CD_PDV,CD_USUARIO,CD_USUARIOAT,CD_HISTORICO,DT_LANCAMENTO,DT_CONTABIL,DT_CADASTRO,DT_ATUALIZACAO,DS_REFERENTE,DS_OBS,NR_DOCUMENTO,NR_CHEQUE,VL_ENTRADA,VL_SAIDA,DT_CONCILIACAO,DT_CONCILIACAO_SERVER,CD_USUARIO_CONCILIACAO,CD_NOTA_FATURAMENTO,CD_ENTRADA_COMPRA,CD_CONTA_GERENCIAL,CD_CHAVE_QUESTOR_TRIBUTARIO,CD_STATUS_INTEGRACAO_QUESTOR,CD_CONHECIMENTO,DS_ESPECIE,CD_LANCAMENTO_STANDALONE,CD_MOEDA,CD_NOTA,CD_PDV_STANDALONE,NR_SERIE_STANDALONE,NR_SERIE_ECF,CD_ORIGEM_DADOS,CD_LANCAMENTO_ORIGEM,CD_ORDEM_SERVICO,DS_MD5_DT_LANCAMENTO,DS_MD5_VL_LANCAMENTO,CD_TABELA_CONTABIL,VL_DESCONTO,CD_CONVERSAO,CD_CAIXA)VALUES({maximoLancamento[0] + 1},{entidade},2860,NULL,1,{filial},{corrente},NULL,0,0,299,'{dataFormat}','{dataFormat}',CAST(GETDATE() AS DATETIME),CAST(GETDATE() AS DATETIME),'{obs[:100]}','{obs}','{numero}',NULL,{i[5]},0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
                            """

                            self.sqlserver.execute_and_commit(insert)
                            txt = f"C|{cnpj}|{corrente}|{historico}|{data}|{data}|{i[5]}||{contabil}||{numero}|{obs}\r\n"
                            array.append(txt)
            
        except Exception as error:
            raise Exception(error)
        finally:
            self.disconnect()
            self.sqlserver.execute_and_commit("SET IDENTITY_INSERT TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS OFF")
            self.sqlserver.disconnect()

    def gerarRecebimentosRecebimentos(self, inicio_periodo, fim_periodo, relacao_empresas):
        self.connect()
        self.sqlserver.connect()
        try:
            self.sqlserver.execute_and_commit("SET IDENTITY_INSERT TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS ON")

            dataini = inicio_periodo.strftime('%d.%m.%Y')
            datafim = fim_periodo.strftime('%d.%m.%Y')
            dicescritorio = get_dicionario()
            dicfilial = get_filial()
            
            for codigo_empresa in relacao_empresas:
                contas = relacao_empresas[codigo_empresa]
                escritorio = int(codigo_empresa)

                datadeHoje = datetime.today().strftime('%d/%m/%Y')
                ano = datafim.split(".")[-1]
                codigos = tuple([int(conta) for conta in contas])
                filial = dicfilial[escritorio][0]
                entidade = dicfilial[escritorio][1]

                dadosempresarial = self.sqlserver.execute_sql(get_lancamentos(filial,dataini,datafim))
                conferencia = []
                for i in dadosempresarial:
                    conferencia.append(i)

                cnpj = dicescritorio[escritorio][0]
                query = self.run_query_for_select(get_recebimentos(escritorio,dataini,datafim,codigos))
                array = []

                for i in query:
                    letra = 'NF' if i[3][0] != 'A' else i[3][0]
                    corrente = dicescritorio[escritorio][1][i[2]][letra]['corrente']
                    historico = dicescritorio[escritorio][1][i[2]][letra]['historico']
                    contabil = dicescritorio[escritorio][1][i[2]][letra]['contabil']

                    if i[5] != 0:
                        responseMaximoLancamento = self.sqlserver.execute_sql(get_max_lancamento())
                        for item in responseMaximoLancamento:
                            maximoLancamento = item

                        numero = str(i[3]).replace('A','').split('-')[0] if str(i[3][0]) == 'A' else str(i[3]).replace(str(i[3][0]),ano).split('-')[0]
                        data = str(i[1])+' 00:00:00.000'
                        dataFormat = i[1].strftime('%Y-%d-%m')+' 00:00:00.000'
                        obs = i[4].replace("'",'')
                        if [int(numero),data[:-4]]  not in [[int(r[0]),str(r[1])] for r in conferencia]:
                            insert = f"""   
                                INSERT INTO nGestaao3.dbo.TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS(CD_LANCAMENTO,CD_ENTIDADE,CD_CONTA_ENTRADA,CD_CONTA_SAIDA,CD_EMPRESA,CD_FILIAL,CD_CONTA_CORRENTE,CD_PDV,CD_USUARIO,CD_USUARIOAT,CD_HISTORICO,DT_LANCAMENTO,DT_CONTABIL,DT_CADASTRO,DT_ATUALIZACAO,DS_REFERENTE,DS_OBS,NR_DOCUMENTO,NR_CHEQUE,VL_ENTRADA,VL_SAIDA,DT_CONCILIACAO,DT_CONCILIACAO_SERVER,CD_USUARIO_CONCILIACAO,CD_NOTA_FATURAMENTO,CD_ENTRADA_COMPRA,CD_CONTA_GERENCIAL,CD_CHAVE_QUESTOR_TRIBUTARIO,CD_STATUS_INTEGRACAO_QUESTOR,CD_CONHECIMENTO,DS_ESPECIE,CD_LANCAMENTO_STANDALONE,CD_MOEDA,CD_NOTA,CD_PDV_STANDALONE,NR_SERIE_STANDALONE,NR_SERIE_ECF,CD_ORIGEM_DADOS,CD_LANCAMENTO_ORIGEM,CD_ORDEM_SERVICO,DS_MD5_DT_LANCAMENTO,DS_MD5_VL_LANCAMENTO,CD_TABELA_CONTABIL,VL_DESCONTO,CD_CONVERSAO,CD_CAIXA)VALUES({maximoLancamento[0] + 1},{entidade},{contabil},NULL,1,{filial},{corrente},NULL,0,0,{historico},'{dataFormat}','{dataFormat}',CAST(GETDATE() AS DATETIME),CAST(GETDATE() AS DATETIME),'{obs[:100]}','{obs}','{numero}',NULL,{i[5]},0.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
                            """

                            self.sqlserver.execute_and_commit(insert)
                            txt = f"C|{cnpj}|{corrente}|{historico}|{data}|{data}|{i[5]}||{contabil}||{numero}|{obs}\r\n"
                            array.append(txt)
            
        except Exception as error:
            raise Exception(error)
        finally:
            self.disconnect()
            self.sqlserver.execute_and_commit("SET IDENTITY_INSERT TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS OFF")
            self.sqlserver.disconnect()