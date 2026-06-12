from io import BytesIO
import base64
import pandas as pd

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
                'filename': "Auditoria de Faturamentos da Última Atualização",
                'file': excel_base64
            }
    except Exception as err:
        raise Exception(err)