from datetime import date, datetime
from django.conf import settings
import pandas as pd
import re
import csv
from django.http import HttpResponse
import zipfile
import os
from PyPDF2 import PdfWriter, PdfReader, PdfMerger
from io import BytesIO
from Database.models import Connection, PostgreSQLConnection
from .sql import SQLSNFManual, SQLSNotasAntecipadas, SQLSNFRetorno, BoletosSQL

class Controller(PostgreSQLConnection):

    def __init__(self, *args, **kwargs):
        self.default_connect()
        self.inicio_periodo = date(2020, 1, 31)
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)
        
    def lancar_nota_antecipada(self, origem, destino, list_nota, codigos_do_usuario):
        try:
            connection = Connection().default_connect()
            connection.connect()
            servico = 200 if destino in [505,567,575] else 0
            notas = tuple(list_nota) if len(list_nota) > 1 else f"({tuple(list_nota)[0]})"
            cd_usuario = codigos_do_usuario if codigos_do_usuario else 0
            svariavel = SQLSNotasAntecipadas.sqlNotasAntecipadas(servico, origem, destino, notas, cd_usuario)
            connection.execute_sql(svariavel)
            connection.commit_changes()
        except Exception as error:
            print(error)
        finally:
            connection.disconnect()
            
    # ---------- EMISSAO NF RETORNO ---------- #
    def gerar_emissao_NF(self, empresas, data):
        try:
            connection = Connection().default_connect()
            connection.connect()
            sqls = SQLSNFRetorno()
            
            dictEmpresas = { 9501:[[501,78,0], [501,51,0]], 9502:[[502,76,0], [502,15,0]], 9505:[[505,80,200], [505,55,200]], 9567:[[567,77,200], [567,67,200]], 9575:[[575,79,200], [575,75,200]] }
            self.writer.writerow(['CODIGOESCRIT','CODIGOCLIENTE','CODIGOSERVICOESCRIT','DATASERVVAR','SEQSERVVAR','SERIENS','NUMERONS','SEQSERVNOTAITEM','QTDADESERVVAR','VALORUNITSERVVAR','VALORTOTALSERVVAR','OBSERVSERVVAR','SITANTECIPACAO','SEQLCTO','CODIGOUSUARIO','DATAHORALCTO','ORIGEMDADO','CHAVEPGTOANTECIP','VALORANTERIORUNITSERVVAR','SEQUENCIACAIXA','CHAVEORIGEM'])
            listaInserts = []

            for i in dictEmpresas:
                for insert, servico, codigo in dictEmpresas[i]:
                    queries = connection.execute_sql(sqls.get_inserts(i,insert,codigo,servico,data, empresas))
                    for result in queries:
                        listaInserts.append(list(result))
            
            for i in listaInserts:
                i[3] = i[3].strftime('%d.%m.%Y')
                i[15] = "CAST('NOW' AS TIMESTAMP)"
                valid = self.sql_verificar(i[0], i[1], i[2], i[3], sqls, connection)
                cod = self.sql_codigos(i[2], sqls, connection)
                if cod:
                    if valid:
                        if i[11] not in [r[4] for r in valid]:
                            seq = max(r[5] for r in valid if r[0] == i[0] and r[1] == i[1] and r[2] == i[2])+1                
                            servicovarivel = f"INSERT INTO SERVICOVARIAVEL (CODIGOESCRIT, CODIGOCLIENTE, CODIGOSERVICOESCRIT, DATASERVVAR, SEQSERVVAR, SERIENS, NUMERONS, SEQSERVNOTAITEM, QTDADESERVVAR, VALORUNITSERVVAR, VALORTOTALSERVVAR, OBSERVSERVVAR, SITANTECIPACAO, SEQLCTO, CODIGOUSUARIO, DATAHORALCTO, ORIGEMDADO, CHAVEPGTOANTECIP, VALORANTERIORUNITSERVVAR, SEQUENCIACAIXA, CHAVEORIGEM) VALUES({i[0]}, {i[1]}, {i[2]}, '{i[3]}', {seq}, {i[5]}, {i[6]}, {i[7]}, {i[8]}, {i[9]}, {i[10]}, '{i[11]}', {i[12]}, {i[13]}, {i[14]}, {i[15]}, {i[16]}, {i[17]}, {i[18]}, {i[19]}, {i[20]})"
                            connection.execute_sql(servicovarivel)
                            connection.commit_changes()
                        else:
                            if i[4] not in [r[5] for r in valid]:
                                servicovarivel = f"INSERT INTO SERVICOVARIAVEL (CODIGOESCRIT, CODIGOCLIENTE, CODIGOSERVICOESCRIT, DATASERVVAR, SEQSERVVAR, SERIENS, NUMERONS, SEQSERVNOTAITEM, QTDADESERVVAR, VALORUNITSERVVAR, VALORTOTALSERVVAR, OBSERVSERVVAR, SITANTECIPACAO, SEQLCTO, CODIGOUSUARIO, DATAHORALCTO, ORIGEMDADO, CHAVEPGTOANTECIP, VALORANTERIORUNITSERVVAR, SEQUENCIACAIXA, CHAVEORIGEM) VALUES({i[0]}, {i[1]}, {i[2]}, '{i[3]}', {i[4]}, {i[5]}, {i[6]}, {i[7]}, {i[8]}, {i[9]}, {i[10]}, '{i[11]}', {i[12]}, {i[13]}, {i[14]}, {i[15]}, {i[16]}, {i[17]}, {i[18]}, {i[19]}, {i[20]})"
                                connection.execute_sql(servicovarivel)
                                connection.commit_changes()
                            else:
                                self.writer.writerow(i)
                    else:
                        servicovarivel = f"INSERT INTO SERVICOVARIAVEL (CODIGOESCRIT, CODIGOCLIENTE, CODIGOSERVICOESCRIT, DATASERVVAR, SEQSERVVAR, SERIENS, NUMERONS, SEQSERVNOTAITEM, QTDADESERVVAR, VALORUNITSERVVAR, VALORTOTALSERVVAR, OBSERVSERVVAR, SITANTECIPACAO, SEQLCTO, CODIGOUSUARIO, DATAHORALCTO, ORIGEMDADO, CHAVEPGTOANTECIP, VALORANTERIORUNITSERVVAR, SEQUENCIACAIXA, CHAVEORIGEM) VALUES({i[0]}, {i[1]}, {i[2]}, '{i[3]}', {i[4]}, {i[5]}, {i[6]}, {i[7]}, {i[8]}, {i[9]}, {i[10]}, '{i[11]}', {i[12]}, {i[13]}, {i[14]}, {i[15]}, {i[16]}, {i[17]}, {i[18]}, {i[19]}, {i[20]})"
                        connection.execute_sql(servicovarivel)
                        connection.commit_changes()
                else:
                    self.writer.writerow(i)
        except Exception as ex:
            raise Exception(ex)
        else:
            self.response['Content-Disposition'] = f"filename=RegistrosNaoImportados_NaoLancados.csv"
            return self.response
        finally:
            connection.disconnect()
            
    def sql_verificar(self, escritorio,cliente,servico,data, sqls, connection):
        query = connection.execute_sql(sqls.verificar(escritorio,cliente,servico,data)).fetchall()
        lista = [list(i) for i in query]
        return lista

    def sql_codigos(self, codigo, sqls, connection):
        query = connection.execute_sql(sqls.codigos(codigo)).fetchall()
        lista = [list(i) for i in query]
        return lista

    # ---------- EMISSAO NF MANUAL ---------- #
    def gerar_emissao_NF_Manual(self, empresas, acoes, data):
        bytIO = BytesIO()
        connection = Connection().default_connect()
        try:
            connection.connect()
            dfHeader = ['CODIGOESCRIT','CODIGOCLIENTE','CODIGOSERVICOESCRIT','DATASERVVAR','SEQSERVVAR','SERIENS','NUMERONS','SEQSERVNOTAITEM','QTDADESERVVAR','VALORUNITSERVVAR','VALORTOTALSERVVAR','OBSERVSERVVAR','SITANTECIPACAO','SEQLCTO','CODIGOUSUARIO','DATAHORALCTO','ORIGEMDADO','CHAVEPGTOANTECIP','VALORANTERIORUNITSERVVAR','SEQUENCIACAIXA','CHAVEORIGEM']
            dictEmpresas = { 9501:[501,0], 9502:[502,0], 9505:[505,200], 9567:[567,200], 9575: [575,200] }
            listaInserts = []

            queries = connection.execute_sql(SQLSNFManual.get_inserts_manual(int(acoes), dictEmpresas[int(acoes)][0], dictEmpresas[int(acoes)][1], data, empresas))
            for i in queries:
                listaInserts.append(list(i))

            df = pd.DataFrame(listaInserts,columns=dfHeader)        
            df['DATASERVVAR'] = pd.to_datetime(df['DATASERVVAR']).dt.strftime('%d/%m/%Y')
            df['DATAHORALCTO'] = pd.to_datetime(df['DATAHORALCTO']).dt.strftime('%d/%m/%Y')
            df['VALORTOTALSERVVAR'] = df['VALORTOTALSERVVAR'].astype(str).str.replace('.',',')
            newDFlist = []

            for row in df.values.tolist():
                if "," not in row[10]:
                    row[10] = row[10] + ",00"
                newDFlist.append(row)
                
            newDF = pd.DataFrame(newDFlist,columns=dfHeader)
            newDF.to_csv(bytIO, sep='|', index=False, line_terminator='\r\n', encoding="utf8")

        except Exception as ex:
            raise Exception(ex)
        else:
            response = HttpResponse(bytIO.getvalue(), content_type='application/txt')
            response['Content-Disposition'] = 'attachment; filename="%s"' % "arquivoManual.txt"
            return response
        finally:
            connection.disconnect()
    
    # ---------- BOLETOS ---------- #
    def getPdfs(self, path, data, nameArquivo):
        self.connect()
        try:
            zip_file = zipfile.ZipFile( settings.BASE_DIR / 'temp/files/separador_boletos/Boletos.zip', 'w')
            
            pathFolder = settings.BASE_DIR / 'temp/files/separador_boletos/'
            array = []
            inputpdf = PdfReader(open(path, "rb"))
            for i in range(len(inputpdf.pages)):
                page = inputpdf.pages[i]
                codigo_empresa = page.extract_text().split('Ag./')[0].split("\n")[-1].strip()
                dados_sql = BoletosSQL.sqlCodigoEmpresa(int(codigo_empresa))
                
                if nameArquivo == 'encerramento unico':
                    if len(codigo_empresa) > 4:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2]
                        fileName = f"{cd_empresa}{' - ' if cd_estab > 1 else ''}{cd_estab if cd_estab > 1 else ''} - honorario unico encerramento {data}"
                    elif int(codigo_empresa) >= 5000 and int(codigo_empresa) <= 5999:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2] if dados[2] > 1 else ''
                        fileName = f"{cd_empresa}{'-' if cd_estab else ''}{cd_estab} - honorario unico encerramento {data}"
                    else:
                        fileName = f"{codigo_empresa.zfill(3)} - honorario unico encerramento {data}"

                elif nameArquivo == 'encerramento':
                    if len(codigo_empresa) > 4:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2] if dados[2] > 1 else ''
                        fileName = f"{cd_empresa}-{cd_estab} - honorario encerramento parcelado {data}"
                    elif int(codigo_empresa) >= 5000 and int(codigo_empresa) <= 5999:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2] if dados[2] > 1 else ''
                        fileName = f"{cd_empresa}{'-' if cd_estab else ''}{cd_estab} - honorario encerramento parcelado {data}"
                    else:
                        fileName = f"{codigo_empresa.zfill(3)} - honorario encerramento parcelado {data}"
                        
                else:
                    if len(codigo_empresa) > 4:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2]
                        fileName = f"{cd_empresa}-{cd_estab} - honorario contabil {data}"
                    elif int(codigo_empresa) >= 5000 and int(codigo_empresa) <= 5999:
                        dados = self.run_query_for_select(dados_sql)[0]
                        cd_empresa = dados[1]
                        cd_estab = dados[2] if dados[2] > 1 else ''
                        fileName = f"{cd_empresa}{'-' if cd_estab else ''}{cd_estab} - servico mensal {data}"
                    else:
                        fileName = f"{codigo_empresa.zfill(3)} - honorario contabil {data}"

                output = PdfWriter()
                output.add_page(page)
                existe = os.path.isfile(settings.BASE_DIR / f'temp/files/separador_boletos/{fileName}.pdf')
                
                if existe:
                    with open(settings.BASE_DIR / f"temp/files/separador_boletos/{fileName}_{i}.pdf", "wb") as outputStream:
                        output.write(outputStream)
                    array.append(f"{fileName}.pdf")
                else:
                    with open(settings.BASE_DIR / f"temp/files/separador_boletos/{fileName}.pdf", "wb") as outputStream:
                        output.write(outputStream)

            for pdf in array:
                self.mergeArquivos(pdf, pathFolder)

            for folder, subfolders, files in os.walk(pathFolder):
                for file in files:
                    if file.endswith('.pdf'):
                        zip_file.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), pathFolder), compress_type = zipfile.ZIP_DEFLATED)

            zip_file.close()
            
        except Exception as error:
            raise Exception(error)
        else:
            zip_file = open( settings.BASE_DIR / 'temp/files/separador_boletos/Boletos.zip', 'rb')
            response = HttpResponse(zip_file, content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="%s"' % 'Boletos.zip'
            return response
        finally:
            self.disconnect()
            self.limparArquivos(pathFolder)
            
    def limparArquivos(self, dirpath):
        diretorio = os.listdir(dirpath)
        try:
            for file in diretorio:
                if not ".py" in file and not '.zip' in file:
                    os.remove(f'{dirpath}/{file}')
        except OSError as e:
            print(f"Error:{ e }")
    
    def excluirArquivos(self, path, arquivos):
        diretorio = os.listdir(path)
        try:
            for arquivo in arquivos:
                if arquivo in diretorio:
                    os.remove('{}/{}'.format(path, arquivo))
                else:
                    print('este arquivo nao existe')
        except OSError as e:
            print(f"Error:{ e }")
            
    def mergeArquivos(self, pdf, pathFolder):
        try:
            arquivos = [f for f in os.listdir(pathFolder) if pdf.split(" - ")[0] == f.split(" - ")[0] ]
            merger = PdfMerger()
            for filename in arquivos:
                merger.append(PdfReader(os.path.join(pathFolder, filename), "rb"))

            merger.write(os.path.join(pathFolder, f"{pdf}"))
            arquivos.remove(pdf)
        except Exception as error:
            print(error)
        else:
            self.excluirArquivos(pathFolder, arquivos)