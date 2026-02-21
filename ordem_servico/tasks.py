from celery import shared_task
import requests
import time
from django.conf import settings
from .models import EmpresasOmie

@shared_task(bind=True)
def baixar_pdfs_e_processar(self, list_os, escritorio, filename):    
    list_clients_db = EmpresasOmie.objects.all()
    total = len(list_os)

    for i, url in enumerate(list_os):
        print(url)
        time.sleep(2)
        # response = requests.get(url)

        # with open(f"/caminho/pdfs/arquivo_{i}.pdf", "wb") as f:
        #     f.write(response.content)
            
        # with open(settings.BASE_DIR / f'temp/files/financeiro/Boletos das OS {escritorio}.zip', 'wb') as f:
        #     f.write(zip_file)
        
        # dfErros = pd.DataFrame(response['errors'], columns=['OS', 'NUM OS', 'TITULO', 'CLIENTE', 'DESCRIÇÃO DO ERRO'])
        # auditoria_file = controller.gerar_arquivo_excel_auditoria_download_boletos(dfErros)
        # response['files']["Auditoria de Boletos.xlsx"] = auditoria_file
        
        # Atualiza progresso
        self.update_state(
            state='PROGRESS',
            meta={'current': i + 1, 'total': total}
        )
        
    # for os in list_os:
    #     obj_os = list_os[os]
    #     num_os = obj_os['numOS']
    #     print(obj_os)
    #     if 'cd_titulo' not in obj_os:
    #         response_data['errors'].append([os, num_os, "", "", "Não foi Encontrado o Código do Título (Sem Conta a Receber) para Gerar o Boleto"])
    #         continue
    #     cd_titulo = obj_os['cd_titulo']
    #     cd_cliente = obj_os['cd_cliente']
    #     cliente = list_clients_db.filter(codigo_cliente_omie=cd_cliente).first()
    #     if not cliente:
    #         response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, "Cliente Não Encontrado na nossa Base de Bados, Atualize !!"])
    #         continue
        
    #     filename_os = str(cliente.cd_empresa).zfill(3) + f"{f'-{cliente.estab}' if int(cliente.estab) > 1 else ''}" + f" - {filename}.pdf"
    #     new_pdf = fitz.open()
    #     try:
    #         url_boleto = ""
    #         # TENTAR OBTER BOLETO
    #         data_get_boleto = get_request_to_api_omie(escritorio, "ObterBoleto", {"nCodTitulo": cd_titulo})
    #         result_obter_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_get_boleto, headers={'content-type': 'application/json'})
    #         json_obter_boleto = result_obter_boleto.json()
    #         if result_obter_boleto.status_code == 200:
    #             if json_obter_boleto['cCodStatus'] == "0":
    #                 url_boleto = json_obter_boleto['cLinkBoleto']
    #         else:
    #             raise Exception(f"Erro na API, rota de ObterBoleto: {json_obter_boleto}")
            
    #         if "https" not in url_boleto:
    #             # GERAR BOLETO
    #             data_gerar_boleto = get_request_to_api_omie(escritorio, "GerarBoleto", {"nCodTitulo": cd_titulo})
    #             result_gerar_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_gerar_boleto, headers={'content-type': 'application/json'})
    #             json_gerar_boleto = result_gerar_boleto.json()
    #             if result_gerar_boleto.status_code == 200:
    #                 if json_gerar_boleto['cCodStatus'] == "0":
    #                     if "https" not in json_gerar_boleto['cLinkBoleto']:
    #                         raise Exception(f"Não Veio a URL na ROTA GERANDO O BOLETO: {json_gerar_boleto['cDesStatus']}")
    #                     else:
    #                         url_boleto = json_gerar_boleto['cLinkBoleto']
    #                 else:
    #                     raise Exception(f"Erro na API, rota de GERAR BOLETO, Não Gerou o Boleto pelo Motivo: {json_gerar_boleto['cDesStatus']}")
    #             else:
    #                 raise Exception(f"Erro na API, rota de GERAR BOLETO: {json_gerar_boleto}")
            
    #         if "https" in url_boleto:
    #             r = requests.get(url_boleto, timeout=25)
    #             if r.status_code == 200:
    #                 try:
    #                     pdf_doc = fitz.open(stream=r.content, filetype="pdf")
    #                     try:
    #                         new_pdf.insert_pdf(pdf_doc)
    #                     except Exception as err:
    #                         raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
    #                     finally:
    #                         pdf_doc.close()
    #                 except Exception as err:
    #                     raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
    #             else:
    #                 raise Exception(f"Erro no momento de requisitar o PDF")
    #         else:
    #             raise Exception(f"Por algum motivo mesmo depois de buscar ou gerar, está sem URL")
            
    #         if new_pdf.page_count > 0:
    #             data_get_pdf_os = get_request_to_api_omie(escritorio, "ObterOS", {"nIdOs": os})
    #             result_obter_pdf_os = requests.post("https://app.omie.com.br/api/v1/servicos/osdocs/", json=data_get_pdf_os, headers={'content-type': 'application/json'})
    #             json_obter_pdf_os = result_obter_pdf_os.json()
    #             if result_obter_pdf_os.status_code == 200:
    #                 if json_obter_pdf_os['cCodStatus'] == "0" and "https" in json_obter_pdf_os['cPdfOs']:
    #                     r = requests.get(json_obter_pdf_os['cPdfOs'], timeout=25)
    #                     if r.status_code == 200:
    #                         try:
    #                             pdf_doc = fitz.open(stream=r.content, filetype="pdf")
    #                             try:
    #                                 new_pdf.insert_pdf(pdf_doc)
    #                             except Exception as err:
    #                                 raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
    #                             finally:
    #                                 pdf_doc.close()
    #                         except Exception as err:
    #                             raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
    #                     else:
    #                         raise Exception(f"Erro no momento de requisitar o PDF da OS")
    #                 else:
    #                     raise Exception(f"Rota de ObterOS, Erro pelo Código: {json_obter_pdf_os}")
    #             else:
    #                 raise Exception(f"Erro na API, rota de ObterOS: {json_obter_pdf_os}")
    #         else:
    #             raise Exception(f"Não Gerou PDF da OS, pois Não gerou o Boleto para")
            
    #     except Exception as err:
    #         response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, f"Erro ao Gerar o PDF: {str(err)}"])
    #     else:
    #         if new_pdf.page_count > 0:
    #             response_data['files'][filename_os] = new_pdf.write()
    #         else:
    #             response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, "PDF VAZIO !!"])
    #     finally:
    #         new_pdf.close()

    return {"status": "concluido"}
