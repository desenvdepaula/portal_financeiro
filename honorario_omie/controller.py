from io import BytesIO
from dataclasses import dataclass
import base64
import pandas as pd
from pathlib import Path
from typing import ClassVar, Dict

def gerar_arquivo_excel_auditoria_debitos(df):
    try:
        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            pd.set_option('max_colwidth', None)
            workbook = writer.book
            alignLeft = workbook.add_format({'align': 'left'})
            
            df.to_excel(writer, sheet_name='Faturamentos', index=False)
            writer.sheets['Faturamentos'].set_column('A:D', 10, alignLeft)
            writer.sheets['Faturamentos'].set_column('E:E', 16, alignLeft)
            writer.sheets['Faturamentos'].set_column('F:F', 50, alignLeft)
            writer.sheets['Faturamentos'].set_column('G:K', 16, alignLeft)
            writer.sheets['Faturamentos'].set_column('L:L', 60, alignLeft)
            writer.sheets['Faturamentos'].set_column('M:M', 50, alignLeft)
            writer.sheets['Faturamentos'].set_column('N:U', 18, alignLeft)

            writer.close()
            
            b.seek(0)
            excel_base64 = base64.b64encode(b.read()).decode('utf-8')
            return {
                'filename': "Relatório OS Faturadas",
                'file': excel_base64
            }
    except Exception as err:
        raise Exception(err)
    
@dataclass
class AnaliseRelatorio:
    file_report: Path
    file_report_omie: Path
    
    _de_para_escritorio: ClassVar[Dict[str, int]] = {
        "DE PAULA CONTADORES LTDA": 501,
        "DE PAULA SOLUCOES CONTABEIS LTDA": 502,
        "DE PAULA ESCOLA DE NEGOCIOS E COWORKING LTDA": 505,
        "DE PAULA SOLUCOES EMPRESARIAIS LTDA": 567,
        "DPC SOLUCOES LTDA": 575,
    }

    def get_dataframe_received_api(self) -> pd.DataFrame:
        df_report = pd.read_excel(self.file_report)

        df_report = (
            df_report.drop(
                df_report.columns.difference([
                    "escritorio", "num_os", "razao_social", "valor_juros", "valor_multa", "valor_retencoes", "valor_total_serv"
                ]), axis=1
            )
        )

        total_recebimentos = (
            df_report.copy(deep=True)
            .groupby(["escritorio", "num_os", "razao_social"], as_index=False)[["valor_total_serv", "valor_retencoes"]].sum()
            .assign(total_liquido=lambda x: x["valor_total_serv"] - x["valor_retencoes"])
        )

        total_juros_multa = (
            df_report.copy(deep=True)
            .query("valor_juros > 0 or valor_multa > 0")
            .drop_duplicates(subset=["escritorio", "num_os", "valor_juros", "valor_multa"])
            .assign(total_juros_multa=lambda x: x["valor_juros"] + x["valor_multa"])
            .drop(columns=["valor_juros", "valor_multa", "valor_retencoes", "valor_total_serv", "razao_social"])
        )

        df_received = (
            pd.merge(total_recebimentos, total_juros_multa, how="left", on=["escritorio", "num_os"])
            .assign(
                total_juros_multa=lambda x: x["total_juros_multa"].fillna(0.00),
                total_recebido=lambda x: round(x["total_liquido"] + x["total_juros_multa"], 2),
                valor_total_serv=lambda x: x["valor_total_serv"].round(2),
                valor_retencoes=lambda x: x["valor_retencoes"].round(2),
                total_liquido=lambda x: x["total_liquido"].round(2)
            )
        )    
        
        return df_received
    
    def get_dataframe_report_omie(self) -> pd.DataFrame:
        df_report = pd.read_excel(self.file_report_omie, header=1)
        df_report = df_report.loc[df_report["Minha Empresa (Razão Social)"].notnull()]
        df_report = (
            df_report.rename(columns={
                    "Minha Empresa (Razão Social)": "escritorio",
                    "Razão Social": "cliente",
                    "A Validar/Em Elaboração": "num_os",
                    "Valor Líquido": "valor_liquido"
            })
            .drop(columns=[
                "Data (No Extrato)", "Categoria", "Conta Corrente", "Valor da Conta"
            ])
            .assign(
                escritorio=lambda x: x["escritorio"].map(self._de_para_escritorio, na_action="ignore"),
                num_os=lambda x: x["num_os"].astype(int),
                valor_liquido=lambda x: x["valor_liquido"].astype(float).round(2)
            )
            .groupby(["escritorio", "num_os", "cliente"], as_index=False)["valor_liquido"].sum()
        )
    
        return df_report
       
    def gerar_analise_relatorio(self) -> None:
        df_received = self.get_dataframe_received_api()
        df_omie = self.get_dataframe_report_omie()
        
        analise = {
            "OS - Relat. API": 0,
            "OS - Relat. Sistema": 0,
            "OS Sem Diferença": 0,
            "OS Com Diferença": 0,
            "OS Faltantes - Relat. API": 0,
            "OS Faltantes - Relat. Sistema": 0,
        }
        
        analise["OS - Relat. API"] = df_received.shape[0]
        analise["OS - Relat. Sistema"] = df_omie.shape[0]
        
        df = (
            pd.merge(df_received, df_omie, how="outer", on=["escritorio", "num_os"], indicator=True)
            .assign(
                diferenca=lambda x: x["total_recebido"] - x["valor_liquido"]
            )
            .rename(
                columns={
                    "escritorio": "Escritório",
                    "num_os": "OS",
                    "razao_social": "Cliente OS",
                    "cliente": "Cliente Recebimento",
                    "valor_total_serv": "Total dos Serviços",
                    "valor_retencoes": "Retenções",
                    "total_liquido": "Total Líquido OS",
                    "total_juros_multa": "Juros e Multa",
                    "total_recebido": "Total Líquido OS com Juros e Multa",
                    "valor_liquido": "Total Recebido",
                    "diferenca": "Diferença"
                }
            )
        )
        
        os_sem_diferenca_valor = df.loc[(df["_merge"] == "both") & (df["Diferença"] == 0)]
        os_com_diferenca_valor = df.loc[(df["_merge"] == "both") & (df["Diferença"] != 0)]
        os_com_diferenca_valor = os_com_diferenca_valor.drop(columns=["_merge", "Cliente Recebimento"])
        os_faltantes_api = df.loc[(df["_merge"] == "left_only") & (df["Total Líquido OS com Juros e Multa"].notnull())]
        os_faltantes_api = os_faltantes_api.drop(columns=["_merge", "Cliente Recebimento", "Total Recebido", "Diferença"])
        os_faltantes_omie = df.loc[(df["_merge"] == "right_only") & (df["Total Recebido"].notnull())]
        os_faltantes_omie = os_faltantes_omie.drop(os_faltantes_omie.columns.difference(["Escritório", "OS", "Cliente Recebimento", "Total Recebido"]), axis=1)
        
        analise["OS Sem Diferença"] = os_sem_diferenca_valor.shape[0]
        analise["OS Com Diferença"] = os_com_diferenca_valor.shape[0]
        analise["OS Faltantes - Relat. API"] = os_faltantes_api.shape[0]
        analise["OS Faltantes - Relat. Sistema"] = os_faltantes_omie.shape[0]
        
        df_analise = (
            pd.DataFrame.from_dict(analise, orient="index", columns=["Quantidade"])
            .assign(
                analise=lambda x: x.index
            )
            .reset_index(drop=True)
            .rename(columns={
                "analise": "Análise",
            })
            .reindex(columns=[
                "Análise", "Quantidade"
            ])
        )
        
        with BytesIO() as b:
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            workbook = writer.book
            num = workbook.add_format({
                "num_format":"#,##0.00",
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri"
            })
            cell_format = workbook.add_format({
                "align": "center",
                "valign": "vcenter",
                "font_name": "Calibri"
            })
            cell_format_left = workbook.add_format({
                "align": "left",
                "valign": "vleft",
                "font_name": "Calibri"
            })            
            
            df_analise.to_excel(writer, sheet_name="Análise", index=False)
            worksheet = writer.sheets["Análise"]
            worksheet.set_column("A:A", 26, cell_format)            
            worksheet.set_column("B:B", 18, cell_format)            
            
            os_com_diferenca_valor.to_excel(writer, sheet_name="OS com Diferença", index=False)
            worksheet = writer.sheets["OS com Diferença"]
            worksheet.set_column("A:B", 14, cell_format) 
            worksheet.set_column("C:C", 50, cell_format_left) 
            worksheet.set_column("D:G", 18, num) 
            worksheet.set_column("H:H", 32, num)
            worksheet.set_column("I:J", 20, num) 
            
            os_faltantes_api.to_excel(writer, sheet_name="OS Faltantes - Relat. API", index=False)
            worksheet = writer.sheets["OS Faltantes - Relat. API"]
            worksheet.set_column("A:B", 14, cell_format) 
            worksheet.set_column("C:C", 50, cell_format_left) 
            worksheet.set_column("D:G", 18, num) 
            worksheet.set_column("H:H", 32, num)
            
            os_faltantes_omie.to_excel(writer, sheet_name="OS Faltantes - Relat. Sistema", index=False)
            worksheet = writer.sheets["OS Faltantes - Relat. Sistema"]
            worksheet.set_column("A:B", 14, cell_format) 
            worksheet.set_column("C:C", 50, cell_format_left) 
            worksheet.set_column("D:D", 18, num)
            
            writer.close()
            
            b.seek(0)
            excel_base64 = base64.b64encode(b.read()).decode('utf-8')
            return {
                'filename': "Análise Recebimentos por Escritório",
                'file': excel_base64
            }