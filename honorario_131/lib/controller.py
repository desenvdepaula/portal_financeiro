from datetime import datetime, date
from io import BytesIO
import csv
import pandas as pd
from django.http import HttpResponse
from ..models import RegrasHonorario
from .querys import SqlHonorarios131
from .database import Manager

class Controller():

    def __init__(self, *args, **kwargs):
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)

    #------------------ HONORARIO 131 ------------------#

    def responseEmpresas(self):
        listEscritoriosEmpresas = self.retornaListadeEmpresas()
        dicio = {}
        lista = []

        empresas = [regra.cd_empresa for regra in RegrasHonorario.objects.filter(calcular=True)]
        empresas = set(empresas)
        response = self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131(tuple(empresas))).fetchall()
        
        for cd_empresa, escritorio in listEscritoriosEmpresas:
            dicio[cd_empresa] = escritorio

        for item in response:
            if item[0] in dicio.keys():
                item = item + (dicio[item[0]],)
                lista.append(item)
            else:
                self.writer.writerow([item[0], item[1], "Esta Empresa não tem Escritorio"])

        df = pd.DataFrame(lista, columns = ["EMPRESA", "QUANTIDADE", "FILIAL", "DATA", "TIPO CONTRATO","ESCRITORIO"])
        
        dfResponse = pd.pivot_table(
            df,
            columns='TIPO CONTRATO',
            index=['EMPRESA','FILIAL','DATA', "ESCRITORIO"],
            values='QUANTIDADE'
        ).reset_index()
        
        dfResponse.fillna(0, inplace=True)

        self.writer.writerow(dfResponse.columns)
        for linha in dfResponse.values.tolist():
            self.writer.writerow(linha)
            
        df = df.drop(columns=['TIPO CONTRATO'])
        df = df.groupby(by=['EMPRESA', 'FILIAL', 'DATA', 'ESCRITORIO'], as_index=False).sum(numeric_only=True)
        return df

    def honorarioEmpresasNaoSomaFilial(self, dataFrame, dictValidationQteLancado):
        dicionaosomafiliais = [ {
            'empresa': regra.cd_empresa, 
            'filial': regra.cd_filial,
            'cd-financeiro': regra.cd_financeiro, 
            'valor': float(regra.valor), 
            'limite': regra.limite 
        } for regra in RegrasHonorario.objects.filter(calcular=True, somar_filiais=False)]
        
        dfRegras = pd.DataFrame(dicionaosomafiliais)
        
        dataFrame = dataFrame.rename(columns={'EMPRESA':'empresa', 'FILIAL': 'filial'})
        dataFrame['empresa'] = dataFrame['empresa'].astype(str)
        dataFrame['filial'] = dataFrame['filial'].astype(str)
        df = pd.merge(dfRegras,dataFrame, on=['empresa', 'filial'], how='left')
        df = df[~df['QUANTIDADE'].isna()]
        
        df['valorCobrado'] = (df['QUANTIDADE'] - df['limite']) * df['valor']
        df['valorCobrado'] = df['valorCobrado'].map('{:.2f}'.format)
        df['valorCobrado'] = df.apply(lambda x : x['valorCobrado'] if float(x['valorCobrado']) >= 0 else 0, axis=1)
        
        self.writer.writerow(["VALIDAÇÃO DAS REGRAS DE EMPRESAS QUE NÃO SOMAM FILIAIS...",'********************','********************','********************','********************','********************','********************','********************','********************','********************','********************'])
        self.writer.writerow(['DESCRIÇÂO DA VALIDAÇÃO', 'EMPRESA','FILIAL','CD-FINANCEIRO', 'VALOR', 'LIMITE', 'DATA', "ESCRITORIO", 'QUANTIDADE','VALOR-COBRADO-FINAL', 'DIFERENCA'])
        for empresa, filial, cd_financeiro, valor, limite, data, escritorio, quantidade, valorCobrado in df.values.tolist():
            diferenca = int(int(quantidade) - int(limite))
            if float(valorCobrado) > 0:
                # VALIDAÇÕES
                if int(cd_financeiro) in dictValidationQteLancado.keys():
                    quantidadeLancada = dictValidationQteLancado[int(cd_financeiro)]
                    if diferenca == quantidadeLancada:
                        self.writer.writerow([
                                "Não Realizou o insert pois já tem lançamento para esta Empresa e Filial", 
                                empresa,
                                filial,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                escritorio, 
                                quantidade, 
                                "********************", 
                                0
                            ])
                    else:
                        novaDiferenca = int(diferenca) - int(quantidadeLancada)
                        if novaDiferenca > 0:
                            newValorCobradoFinal = novaDiferenca * float(valor)
                            self.writer.writerow([
                                f"Feito novo insert com as diferenças, pois, Tinham Lançamentos, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                filial,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                escritorio, 
                                quantidade, 
                                "R$ {:_.2f}".format(float(newValorCobradoFinal)).replace('.', ',').replace('_', '.'), 
                                novaDiferenca 
                            ])
                            self.insertNaBase(int(escritorio), int(cd_financeiro), novaDiferenca, valor, newValorCobradoFinal, int(quantidade), data)
                        else:
                            self.writer.writerow([
                                f"Não foi realizado Insert, pois a Diferença é negativa ou nula, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                filial,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data,
                                escritorio,
                                quantidade,
                                "********************",
                                novaDiferenca
                            ])
                else:
                    self.writer.writerow([
                        "Foi realizado o lançamento, pois Não tinham lançamentos nesta empresa e Filial", 
                        empresa, 
                        filial, 
                        cd_financeiro, 
                        "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'),
                        limite,
                        data,
                        escritorio,
                        quantidade,
                        "R$ {:_.2f}".format(float(valorCobrado)).replace('.', ',').replace('_', '.'), 
                        diferenca
                    ])
                    self.insertNaBase(int(escritorio), int(cd_financeiro), diferenca, valor, valorCobrado, int(quantidade), data)

    def honorarioEmpresasSomaFilial(self, dataFrame, dictValidationQteLancado):
        diciosomafiliais = [ {
            'empresa': regra.cd_empresa, 
            'cd-financeiro': regra.cd_financeiro, 
            'valor': float(regra.valor), 
            'limite': regra.limite 
        } for regra in RegrasHonorario.objects.filter(calcular=True, somar_filiais=True)]
        
        dataFrameTratamento = dataFrame.drop(columns=['FILIAL'])
        dataFrameTratamento = dataFrameTratamento.groupby(by=['EMPRESA','DATA', 'ESCRITORIO'], as_index=False).sum(numeric_only=True)
        dataFrameTratamento = dataFrameTratamento.rename(columns={'EMPRESA':'empresa'})
        dataFrameTratamento['empresa'] = dataFrameTratamento['empresa'].astype(str)
        df = pd.DataFrame(diciosomafiliais)
        df = pd.merge(df,dataFrameTratamento, on=['empresa'], how='left')
        df = df[~df.isna().any(axis=1)]
        df['QUANTIDADE'] = df['QUANTIDADE'].astype(int)
        df['ESCRITORIO'] = df['ESCRITORIO'].astype(int)
        df['valorCobrado'] = (df['QUANTIDADE'] - df['limite']) * df['valor']
        df['valorCobrado'] = df['valorCobrado'].map('{:.2f}'.format)
        df['valorCobrado'] = df.apply(lambda x : x['valorCobrado'] if float(x['valorCobrado']) >= 0 else 0, axis=1)

        self.writer.writerow(["VALIDAÇÃO DAS REGRAS DE EMPRESAS QUE SOMAM TODAS AS FILIAIS...",'********************','********************','********************','********************','********************','********************','********************','********************','********************'])
        self.writer.writerow(['DESCRIÇÂO DA VALIDAÇÃO', 'EMPRESA','CD-FINANCEIRO','VALOR','LIMITE','DATA', "ESCRITORIO", 'QUANTIDADE', 'VALOR-COBRADO-FINAL', 'DIFERENCA'])
        for empresa, cd_financeiro,  valor,  limite,  data,  escritorio,  quantidade, valorCobrado in df.values.tolist():
            if float(valorCobrado) > 0:
                diferenca = int(quantidade - limite)
                if int(cd_financeiro) in dictValidationQteLancado.keys():
                    quantidadeLancada = dictValidationQteLancado[int(cd_financeiro)]
                    if diferenca == quantidadeLancada:
                        self.writer.writerow([
                            "Não Realizou o insert pois Ja foi feito insert em todas as filiais desta Empresa", 
                            empresa,
                            cd_financeiro, 
                            "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                            limite, 
                            data, 
                            int(escritorio), 
                            int(quantidade), 
                            "********************", 
                            0
                        ])
                    else:
                        novaDiferenca = int(diferenca) - int(quantidadeLancada)
                        if novaDiferenca > 0:
                            newValorCobradoFinal = novaDiferenca * float(valor)
                            self.writer.writerow([
                                f"Feito novo insert com as diferenças, pois, Tinham Lançamentos, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                int(escritorio), 
                                int(quantidade), 
                                "R$ {:_.2f}".format(float(newValorCobradoFinal)).replace('.', ',').replace('_', '.'), 
                                novaDiferenca 
                            ])
                            self.insertNaBase(int(escritorio), int(cd_financeiro), novaDiferenca, valor, newValorCobradoFinal, int(quantidade), data)
                        else:
                            self.writer.writerow([
                                f"Não foi realizado Insert, pois a Diferença é negativa ou nula, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                int(escritorio), 
                                int(quantidade), 
                                "********************", 
                                novaDiferenca
                            ])
                            
                else:
                    self.writer.writerow([
                        "Foi realizado o lançamento, pois Não tinham lançamentos nas Filiais desta Empresa",
                        empresa, 
                        cd_financeiro, 
                        "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                        limite, 
                        data, 
                        int(escritorio), 
                        int(quantidade), 
                        "R$ {:_.2f}".format(float(valorCobrado)).replace('.', ',').replace('_', '.'), 
                        diferenca
                    ])
                    self.insertNaBase(int(escritorio), int(cd_financeiro), diferenca, valor, valorCobrado, int(quantidade), data)

    def retornaListadeEmpresas(self):
        response = self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131Find()).fetchall()
        return response

    def retornaListadeEmpresasValidation(self):
        mes = datetime.today().strftime('%m')
        response = self.manager.execute_sql(SqlHonorarios131.getSqlValidador131(mes)).fetchall()
        return response

    def insertNaBase(self, cd_escritorio, cd_financeiro, direfenca_quantidade, valor, valor_multiplicado, quantidade, data):
        self.manager.connection.begin()
        self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131Insert(cd_escritorio, cd_financeiro, direfenca_quantidade, valor, valor_multiplicado, quantidade, data))
        self.manager.commit_changes()

    def gerarHonorarios(self):
        try:
            self.manager.connect()
            validation = self.retornaListadeEmpresasValidation()
            dictValidation = {}
            
            for cd_financeiro, _, quantidade in validation:
                dictValidation[cd_financeiro] = int(quantidade)
                
            dataFrameSql = self.responseEmpresas()
            
            self.honorarioEmpresasSomaFilial(dataFrameSql, dictValidation)
            self.honorarioEmpresasNaoSomaFilial(dataFrameSql, dictValidation)
        except Exception as err:
            raise Exception(err)
        else:
            self.response['Content-Disposition'] = "filename=ConferenciaHonorario.csv"
            return self.response
        finally:
            self.manager.disconnect()


    #------------------ RELATORIO HONORARIO 131 ------------------#


    def gerarRelatorioHonorarios(self, empresa):
        try:
            self.manager.connect()
            listEmpresas = self.retornaListadeEmpresasParaRelatorio(f"({empresa})")
            nome = self.retornaNomeEmpresa(int(empresa))

            for filial in listEmpresas[int(empresa)]['filial']:
                porcentagemFuncionarioPorFilial = listEmpresas[int(empresa)]['filial'][filial]['funcionariosFilial'] / listEmpresas[int(empresa)]['quantidade']
                porcentagemFinal = "{:_.2f} %".format(float(porcentagemFuncionarioPorFilial)*100)
                listEmpresas[int(empresa)]['filial'][filial]['porcentagemFuncionarioPorFilial'] = porcentagemFinal
                for custo in listEmpresas[int(empresa)]['filial'][filial]['custo']:
                    porcentagemFuncionarioPorCusto = listEmpresas[int(empresa)]['filial'][filial]['custo'][custo]['quantid'] / listEmpresas[int(empresa)]['filial'][filial]['funcionariosFilial']
                    porcentagemFinalCusto = "{:_.2f} %".format(float(porcentagemFuncionarioPorCusto)*100)
                    listEmpresas[int(empresa)]['filial'][filial]['custo'][custo]['porcentagemFuncionarioPorCusto'] = porcentagemFinalCusto
                
            context = {
                'nome_empresa': nome[0][0],
                'nr_empresa': int(empresa),
                'totalFuncionarios': listEmpresas[int(empresa)]['quantidade'],
                'filiais': listEmpresas[int(empresa)]['filial'],
            }
        except Exception as err:
            raise Exception(err)
        else:
            return context
        finally:
            self.manager.disconnect()

    def retornaNomeEmpresa(self, empresa):
        response = self.manager.execute_sql(SqlHonorarios131.getSqlNomeEmpresa(empresa)).fetchall()
        return response

    def retornaListadeEmpresasParaRelatorio(self, empresas):
        response = self.manager.execute_sql(SqlHonorarios131.getSqlSelectHonorarios131(empresas)).fetchall()
        listEmpresas = []
        dicio = {}

        for item in response:
            listEmpresas.append(list(item))

        for linha in listEmpresas:
            if linha[0] in dicio:
                dicio[linha[0]]['quantidade'] += linha[1]
                if linha[3] in dicio[linha[0]]['filial']:
                    dicio[linha[0]]['filial'][linha[3]]['funcionariosFilial'] += linha[1]

                else:
                    dicio[linha[0]]['filial'][linha[3]] = {
                        'custo': {},
                        'funcionariosFilial': linha[1]
                    }

                if f"{linha[2]}/{linha[4]}" in dicio[linha[0]]['filial'][linha[3]]['custo']:
                    dicio[linha[0]]['filial'][linha[3]]['custo'][f"{linha[2]}/{linha[4]}"]['quantid'] += linha[1]
                    
                else:
                    dicio[linha[0]]['filial'][linha[3]]['custo'][f"{linha[2]}/{linha[4]}"] = {
                        'name': linha[2],
                        'type': linha[4],
                        'quantid': linha[1]
                    }

            else:
                dicio[linha[0]] = {
                    'quantidade': linha[1],
                    'filial': {
                        linha[3]: {
                            'custo': {f"{linha[2]}/{linha[4]}": {'name': linha[2], 'type': linha[4], 'quantid': linha[1]}},
                            'funcionariosFilial': linha[1]
                        }
                    }
                }

        return dicio