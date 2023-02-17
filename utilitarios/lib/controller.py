from datetime import date, datetime
from django.conf import settings
import pandas as pd
import re
import csv
from django.http import HttpResponse
import zipfile
import os
from Database.models import Connection
from .sql import get_inserts, get_inserts_manual, verificar, codigos, sqlNotasAntecipadas

class Controller():

    def __init__(self, *args, **kwargs):
        self.inicio_periodo = date(2020, 1, 31)
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)

    # ---------- EMISSAO NF MANUAL ---------- #
    def gerar_emissao_NF_Manual(self, empresas, acoes, data):
        try:
            connection = Connection().default_connect()
            connection.connect()
            dictEmpresas = { 9501:[501,0], 9502:[502,0], 9505:[505,200], 9567:[567,200], 9575: [575,200] }
            listaInserts = []

            queries = connection.execute_sql(get_inserts_manual(int(acoes), dictEmpresas[int(acoes)][0], dictEmpresas[int(acoes)][1], data, empresas))
            for i in queries:
                listaInserts.append(list(i))

            df = pd.DataFrame(listaInserts,columns=['CODIGOESCRIT','CODIGOCLIENTE','CODIGOSERVICOESCRIT','DATASERVVAR','SEQSERVVAR','SERIENS','NUMERONS','SEQSERVNOTAITEM','QTDADESERVVAR','VALORUNITSERVVAR','VALORTOTALSERVVAR','OBSERVSERVVAR','SITANTECIPACAO','SEQLCTO','CODIGOUSUARIO','DATAHORALCTO','ORIGEMDADO','CHAVEPGTOANTECIP','VALORANTERIORUNITSERVVAR','SEQUENCIACAIXA','CHAVEORIGEM'])        
            df['DATASERVVAR'] = pd.to_datetime(df['DATASERVVAR']).dt.strftime('%d/%m/%Y')
            df['DATAHORALCTO'] = pd.to_datetime(df['DATAHORALCTO']).dt.strftime('%d/%m/%Y')
            df['VALORTOTALSERVVAR'] = df['VALORTOTALSERVVAR'].astype(str).str.replace('.',',')
            newDFlist = []

            for row in df.values.tolist():
                if "," not in row[10]:
                    row[10] = row[10] + ",00"
                newDFlist.append(row)
                
            newDF = pd.DataFrame(newDFlist,columns=['CODIGOESCRIT','CODIGOCLIENTE','CODIGOSERVICOESCRIT','DATASERVVAR','SEQSERVVAR','SERIENS','NUMERONS','SEQSERVNOTAITEM','QTDADESERVVAR','VALORUNITSERVVAR','VALORTOTALSERVVAR','OBSERVSERVVAR','SITANTECIPACAO','SEQLCTO','CODIGOUSUARIO','DATAHORALCTO','ORIGEMDADO','CHAVEPGTOANTECIP','VALORANTERIORUNITSERVVAR','SEQUENCIACAIXA','CHAVEORIGEM'])        
            newDF.to_csv(f'temp/files/emissao_nf_manual/arquivoManual.txt', sep='|', index=False, lineterminator='\r\n', encoding="utf8")

        except Exception as ex:
            print("Ocorreu um erro ao executar esta operação: {0}".format(ex))
        else:
            file = open( settings.BASE_DIR / f'temp/files/emissao_nf_manual/arquivoManual.txt', 'rb')
            response = HttpResponse(file, content_type='application/txt')
            response['Content-Disposition'] = 'attachment; filename="%s"' % 'ArquivoValidacaoEmissaoNFManual.txt'
            file.close()
            return response
        finally:
            connection.disconnect()