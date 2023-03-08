from datetime import datetime, date
from io import BytesIO
import csv
import pandas as pd
from django.http import HttpResponse
from ..models import RegrasHonorario
from .querys import SqlHonorarios131
from .database import Manager, ManagerTareffa

class Controller():

    def __init__(self, active_database_tareffa=False, *args, **kwargs):
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)
        if active_database_tareffa:
            self.managerTareffa = ManagerTareffa(*args, **kwargs)

    #------------------ AUDITORIA 131 ------------------#
    
    def gerarAuditoria(self):
        try:
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                empresasForaDasRegras = []
                RegrasInvalidas = []
                
                empresas = self.managerTareffa.get_empresa_ativas()
                codigos = [empresa[0] for empresa in empresas]
                
                regrasGeral = RegrasHonorario.objects.filter(calcular=True)
                regrasGeralSomadas = [regra.cd_empresa for regra in regrasGeral if regra.somar_filiais]
                regrasGeralNaoSomadas = [f'{regra.cd_empresa}/{regra.cd_filial}' for regra in regrasGeral if not regra.somar_filiais]
                
                for empresa in empresas:
                    if str(empresa[0]) not in regrasGeralSomadas and f"{empresa[0]}/{empresa[1]}" not in regrasGeralNaoSomadas:
                        empresasForaDasRegras.append(empresa)
                
                for regra in regrasGeral:
                    if int(regra.cd_empresa) not in codigos:
                        RegrasInvalidas.append([
                            regra.cd_financeiro, 
                            regra.cd_empresa, 
                            regra.cd_filial, 
                            regra.razao_social, 
                            "CALCULA", 
                            "SOMA FILIAIS" if regra.somar_filiais else "NÃO SOMA FILIAIS",
                            "Esta Regra se Refere a uma Empresa Não Ativa no Tareffa"
                        ])
                        
                dfEmpresasSemRegras = pd.DataFrame(empresasForaDasRegras, columns=['CD_EMPRESA', 'CD_ESTAB', 'NOME', "CARACTERISTICA"])
                dfEmpresasSemRegras.to_excel(writer, sheet_name='Empresa Sem Regras', index = False)
                writer.sheets['Empresa Sem Regras'].set_column('A:B', 20, alignCenter)
                writer.sheets['Empresa Sem Regras'].set_column('C:C', 80, alignCenter)
                writer.sheets['Empresa Sem Regras'].set_column('D:D', 25, alignCenter)
                
                dfRegrasInvalidadas = pd.DataFrame(RegrasInvalidas, columns=['CD_FIANANCEIRO', 'CD_EMPRESA', "CD_FILIAL",'NOME', "CALCULA ?", "SOMA FILIAIS", "DESCRIÇÃO"])
                dfRegrasInvalidadas.to_excel(writer, sheet_name='Regras Inválidas', index = False)
                writer.sheets['Regras Inválidas'].set_column('A:C', 20, alignCenter)
                writer.sheets['Regras Inválidas'].set_column('D:D', 80, alignCenter)
                writer.sheets['Regras Inválidas'].set_column('E:F', 20, alignCenter)
                writer.sheets['Regras Inválidas'].set_column('G:G', 60, alignCenter)
                
                writer.close()
                
                filename = 'AuditoriaHonorario.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
                
        except Exception as err:
            raise Exception(err)
    
    #------------------ HONORARIO 131 ------------------#

    def responseEmpresas(self, alignCenter, writer, compet):
        listEscritoriosEmpresas = self.retornaListadeEmpresas()
        dicio = {}
        lista = []
        empresasSemEscritorio = []

        empresas = [regra.cd_empresa for regra in RegrasHonorario.objects.filter(calcular=True)]
        empresas = set(empresas)
        response = self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131(tuple(empresas), compet)).fetchall()
        
        for cd_empresa, escritorio in listEscritoriosEmpresas:
            dicio[cd_empresa] = escritorio

        for item in response:
            if item[0] in dicio.keys():
                item = item + (dicio[item[0]],)
                lista.append(item)
            else:
                empresasSemEscritorio.append([item[0], item[2], "Esta Empresa não tem Escritório, por algum motivo que eu não sei =|"])

        df = pd.DataFrame(lista, columns = ["EMPRESA", "QUANTIDADE", "FILIAL", "DATA", "TIPO CONTRATO","ESCRITORIO"])
        
        dfResponse = pd.pivot_table(
            df,
            columns='TIPO CONTRATO',
            index=['EMPRESA','FILIAL','DATA', "ESCRITORIO"],
            values='QUANTIDADE'
        ).reset_index()
        dfResponse.fillna(0, inplace=True)
            
        df = df.drop(columns=['TIPO CONTRATO'])
        df = df.groupby(by=['EMPRESA', 'FILIAL', 'DATA', 'ESCRITORIO'], as_index=False).sum(numeric_only=True)
        
        dfResponse.to_excel(writer, sheet_name='Auditoria Geral', index = False)
        writer.sheets['Auditoria Geral'].set_column('A:E', 15, alignCenter)
        writer.sheets['Auditoria Geral'].set_column('F:F', 22, alignCenter)
        writer.sheets['Auditoria Geral'].set_column('G:I', 15, alignCenter)
        
        dfEmpresas = pd.DataFrame(empresasSemEscritorio, columns=['CODIGO EMPRESA','CODIGO ESTAB','DESCRIÇÃO'])
        dfEmpresas.to_excel(writer, sheet_name='Sem Escritório', index = False)
        writer.sheets['Sem Escritório'].set_column('A:B', 30, alignCenter)
        writer.sheets['Sem Escritório'].set_column('C:C', 60, alignCenter)
        
        return df

    def honorarioEmpresasNaoSomaFilial(self, dataFrame, dictValidationQteLancado, alignCenter, writer, data_lancamento):
        dicionaosomafiliais = [ {
            'empresa': regra.cd_empresa, 
            'filial': regra.cd_filial,
            'cd-financeiro': regra.cd_financeiro, 
            'valor': float(regra.valor), 
            'limite': regra.limite 
        } for regra in RegrasHonorario.objects.filter(calcular=True, somar_filiais=False)]
        
        auditoriaGeralNaoSomaFilial = []
        
        dfRegras = pd.DataFrame(dicionaosomafiliais)
        
        dataFrame = dataFrame.rename(columns={'EMPRESA':'empresa', 'FILIAL': 'filial'})
        dataFrame['empresa'] = dataFrame['empresa'].astype(str)
        dataFrame['filial'] = dataFrame['filial'].astype(str)
        df = pd.merge(dfRegras,dataFrame, on=['empresa', 'filial'], how='left')
        df = df[~df['QUANTIDADE'].isna()]
        
        df['valorCobrado'] = (df['QUANTIDADE'] - df['limite']) * df['valor']
        df['valorCobrado'] = df['valorCobrado'].map('{:.2f}'.format)
        df['valorCobrado'] = df.apply(lambda x : x['valorCobrado'] if float(x['valorCobrado']) >= 0 else 0, axis=1)
        
        for empresa, filial, cd_financeiro, valor, limite, data, escritorio, quantidade, valorCobrado in df.values.tolist():
            diferenca = int(int(quantidade) - int(limite))
            if float(valorCobrado) > 0:
                # VALIDAÇÕES
                if int(cd_financeiro) in dictValidationQteLancado.keys():
                    quantidadeLancada = dictValidationQteLancado[int(cd_financeiro)]
                    if diferenca == quantidadeLancada:
                        auditoriaGeralNaoSomaFilial.append([
                                "Não Realizou o insert, já tem lançamento para esta Empresa e Filial", 
                                empresa,
                                filial,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                escritorio, 
                                quantidade, 
                                "R$ Nenhum Valor Cobrado,99", 
                                0
                            ])
                    else:
                        novaDiferenca = int(diferenca) - int(quantidadeLancada)
                        if novaDiferenca > 0:
                            newValorCobradoFinal = novaDiferenca * float(valor)
                            auditoriaGeralNaoSomaFilial.append([
                                f"Feito novo insert com as diferenças, já tinham lançamentos, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
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
                            self.insertNaBase(int(escritorio), int(cd_financeiro), novaDiferenca, valor, newValorCobradoFinal, int(quantidade), data, data_lancamento)
                        else:
                            auditoriaGeralNaoSomaFilial.append([
                                f"Não foi realizado Insert, a Diferença é negativa ou nula, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                filial,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data,
                                escritorio,
                                quantidade,
                                "R$ Nenhum Valor Cobrado,99",
                                novaDiferenca
                            ])
                else:
                    auditoriaGeralNaoSomaFilial.append([
                        "Foi realizado o lançamento com sucesso !", 
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
                    self.insertNaBase(int(escritorio), int(cd_financeiro), diferenca, valor, valorCobrado, int(quantidade), data, data_lancamento)
                    
        dfAuditoria = pd.DataFrame(auditoriaGeralNaoSomaFilial, columns=['DESCRIÇÂO DA VALIDAÇÃO', 'EMPRESA','FILIAL','CD-FINANCEIRO', 'VALOR', 'LIMITE', 'DATA', "ESCRITORIO", 'QUANTIDADE','VALOR-COBRADO-FINAL', 'DIFERENCA'])
        dfAuditoria.to_excel(writer, sheet_name='Auditoria Não Soma Filiais', index = False)
        writer.sheets['Auditoria Não Soma Filiais'].set_column('A:A', 90, alignCenter)
        writer.sheets['Auditoria Não Soma Filiais'].set_column('B:I', 17, alignCenter)
        writer.sheets['Auditoria Não Soma Filiais'].set_column('J:J', 26, alignCenter)
        writer.sheets['Auditoria Não Soma Filiais'].set_column('K:K', 17, alignCenter)

    def honorarioEmpresasSomaFilial(self, dataFrame, dictValidationQteLancado, alignCenter, writer, data_lancamento):
        diciosomafiliais = [ {
            'empresa': regra.cd_empresa, 
            'cd-financeiro': regra.cd_financeiro, 
            'valor': float(regra.valor), 
            'limite': regra.limite 
        } for regra in RegrasHonorario.objects.filter(calcular=True, somar_filiais=True)]
        
        auditoriaGeralSomaFilial = []
        
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

        for empresa, cd_financeiro,  valor,  limite,  data,  escritorio,  quantidade, valorCobrado in df.values.tolist():
            if float(valorCobrado) > 0:
                diferenca = int(quantidade - limite)
                if int(cd_financeiro) in dictValidationQteLancado.keys():
                    quantidadeLancada = dictValidationQteLancado[int(cd_financeiro)]
                    if diferenca == quantidadeLancada:
                        auditoriaGeralSomaFilial.append([
                            "Não Realizou o insert, já possui lançamentos em todas as Filiais", 
                            empresa,
                            cd_financeiro, 
                            "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                            limite, 
                            data, 
                            int(escritorio), 
                            int(quantidade), 
                            "R$ Nenhum Valor Cobrado,99", 
                            0
                        ])
                    else:
                        novaDiferenca = int(diferenca) - int(quantidadeLancada)
                        if novaDiferenca > 0:
                            newValorCobradoFinal = novaDiferenca * float(valor)
                            auditoriaGeralSomaFilial.append([
                                f"Feito novo insert com as diferenças, já tinham Lançamentos, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
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
                            self.insertNaBase(int(escritorio), int(cd_financeiro), novaDiferenca, valor, newValorCobradoFinal, int(quantidade), data, data_lancamento)
                        else:
                            auditoriaGeralSomaFilial.append([
                                f"Não foi realizado Insert, a Diferença é negativa ou nula, Diferença atual: {diferenca}, Valor lançado: {quantidadeLancada}",
                                empresa,
                                cd_financeiro, 
                                "R$ {:_.2f}".format(float(valor)).replace('.', ',').replace('_', '.'), 
                                limite, 
                                data, 
                                int(escritorio), 
                                int(quantidade), 
                                "R$ Nenhum Valor Cobrado,99", 
                                novaDiferenca
                            ])
                            
                else:
                    auditoriaGeralSomaFilial.append([
                        "Foi realizado o lançamento Normalmente !!",
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
                    self.insertNaBase(int(escritorio), int(cd_financeiro), diferenca, valor, valorCobrado, int(quantidade), data, data_lancamento)
                    
        dfAuditoria = pd.DataFrame(auditoriaGeralSomaFilial, columns=['DESCRIÇÂO DA VALIDAÇÃO', 'EMPRESA','CD-FINANCEIRO','VALOR','LIMITE','DATA', "ESCRITORIO", 'QUANTIDADE', 'VALOR-COBRADO-FINAL', 'DIFERENCA'])
        dfAuditoria.to_excel(writer, sheet_name='Auditoria Soma Filiais', index = False)
        writer.sheets['Auditoria Soma Filiais'].set_column('A:A', 90, alignCenter)
        writer.sheets['Auditoria Soma Filiais'].set_column('B:H', 17, alignCenter)
        writer.sheets['Auditoria Soma Filiais'].set_column('I:I', 26, alignCenter)
        writer.sheets['Auditoria Soma Filiais'].set_column('J:J', 17, alignCenter)

    def retornaListadeEmpresas(self):
        response = self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131Find()).fetchall()
        return response

    def retornaListadeEmpresasValidation(self, data):
        response = self.manager.execute_sql(SqlHonorarios131.getSqlValidador131(data)).fetchall()
        return response

    def insertNaBase(self, cd_escritorio, cd_financeiro, direfenca_quantidade, valor, valor_multiplicado, quantidade, data, data_lancamento):
        self.manager.connection.begin()
        self.manager.execute_sql(SqlHonorarios131.getSqlHonorarios131Insert(cd_escritorio, cd_financeiro, direfenca_quantidade, valor, valor_multiplicado, quantidade, data, data_lancamento))
        self.manager.commit_changes()

    def returnCompetToValidation(self, compet):
        _, mes, ano = compet.split('.')
        mes = int(mes)
        return f"{mes}/{ano}"
    
    def gerarHonorarios(self, compet, data_lancamento):
        try:
            
            with BytesIO() as b:
                self.manager.connect()
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                
                dataValidation = self.returnCompetToValidation(compet)
                validation = self.retornaListadeEmpresasValidation(dataValidation)
                dictValidation = {}
                
                for cd_financeiro, _, quantidade in validation:
                    dictValidation[cd_financeiro] = int(quantidade)
                    
                dataFrameSql = self.responseEmpresas(alignCenter, writer, compet)
                self.honorarioEmpresasSomaFilial(dataFrameSql, dictValidation, alignCenter, writer, data_lancamento.strftime('%d.%m.%Y'))
                self.honorarioEmpresasNaoSomaFilial(dataFrameSql, dictValidation, alignCenter, writer, data_lancamento.strftime('%d.%m.%Y'))
                
                writer.close()
                
                filename = 'ConferenciaHonorario.xlsx'
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
                'competencia': listEmpresas[int(empresa)]['competencia'],
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
        listEmpresas = [list(item) for item in response]
        dicio = {}

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
                    'competencia': linha[5],
                    'filial': {
                        linha[3]: {
                            'custo': {f"{linha[2]}/{linha[4]}": {'name': linha[2], 'type': linha[4], 'quantid': linha[1]}},
                            'funcionariosFilial': linha[1]
                        }
                    },
                }

        return dicio