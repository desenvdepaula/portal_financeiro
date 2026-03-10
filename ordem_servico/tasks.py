from celery import shared_task
from .lib.querys import gerar_arquivo_excel_auditoria_download_boletos
import requests
import time
import fitz
import pandas as pd
from django.conf import settings
from .models import EmpresasOmie
from core.views import get_request_to_api_omie

@shared_task(bind=True)
def update_empresas_omie(self, empresas_request, escrit_list, empresas):
    total = 0
    response = []
    try:
        escritorios = escrit_list if escrit_list else ['501', '502', '505', '567', '575']
        if empresas_request:
            total = len(empresas)
            for i, cnpj_empresa_req in enumerate(empresas):
                for escrit in escritorios:
                    data_get_contrato_omie = get_request_to_api_omie(escrit, "ListarContratos", { "pagina": 1, "registros_por_pagina": 5, "cExibeObs": "N", "cExibirProdutos": "N", "cExibirInfoCadastro": "N", "filtrar_cnpj_cpf": cnpj_empresa_req })
                    result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/contrato/", json=data_get_contrato_omie, headers={'content-type': 'application/json'})
                    json_contrato = result_contrato.json()
                    if result_contrato.status_code == 200:
                        contrato = json_contrato.get("contratoCadastro")[0]
                        if contrato['cabecalho']['cCodSit'] == '10':
                            time.sleep(0.2)
                            data_get_client_omie = get_request_to_api_omie(escrit, "ConsultarCliente", {"codigo_cliente_omie": contrato['cabecalho']['nCodCli']})
                            result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                            json_client = result_client.json()
                            empresa, razaosocial, estab, cnpj = empresas[cnpj_empresa_req]
                            if result_client.status_code == 200:
                                email = json_client['email'] if 'email' in json_client else ""
                                cd_omie_empresa = json_client.get("codigo_cliente_omie")
                                try:
                                    enterprise, _ = EmpresasOmie.objects.get_or_create( cnpj_cpf = cnpj )
                                    enterprise.escritorio = escrit
                                    enterprise.cd_empresa = empresa
                                    enterprise.estab = estab
                                    enterprise.name_empresa = razaosocial
                                    enterprise.codigo_cliente_omie = cd_omie_empresa
                                    enterprise.email = email
                                    enterprise.save()
                                except Exception as err:
                                    response.append(f"Erro ao Criar a Empresa: ({cnpj}) Cliente: {cd_omie_empresa} Empresa: {empresa}/{estab} | Erro:{str(err)}")
                                finally:
                                    break
                            else:
                                error_text = json_client.get('message') or json_client.get('faultstring')
                                response.append(f"Erro ao Buscar este Cliente ({empresa} - {estab}) do Escritório: {escrit} | Erro: {error_text}")
                                break
                    time.sleep(0.7)
                self.update_state(
                    state='PROGRESS',
                    meta={'current': i + 1, 'total': total}
                )
        else:
            for escrit in escritorios:
                page = 1
                while True:
                    data_get_contrato_omie = get_request_to_api_omie(escrit, "ListarContratos", { "pagina": page, "registros_por_pagina": 500, "cExibeObs": "N", "cExibirProdutos": "N", "cExibirInfoCadastro": "N" })
                    result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/contrato/", json=data_get_contrato_omie, headers={'content-type': 'application/json'})
                    json_contrato = result_contrato.json()
                    if result_contrato.status_code == 200:
                        codigos_client = set([i['cabecalho']['nCodCli'] for i in json_contrato['contratoCadastro'] if i['cabecalho']['cCodSit'] == '10'])
                        total = len(codigos_client)
                        for i, client in enumerate(codigos_client):
                            time.sleep(0.2)
                            data_get_client_omie = get_request_to_api_omie(escrit, "ConsultarCliente", {"codigo_cliente_omie": client})
                            result_client = requests.post("https://app.omie.com.br/api/v1/geral/clientes/", json=data_get_client_omie, headers={'content-type': 'application/json'})
                            json_client = result_client.json()
                            if result_client.status_code == 200:
                                email = json_client['email'] if 'email' in json_client else ""
                                cnpj_cpf = json_client['cnpj_cpf']
                                if cnpj_cpf in empresas:
                                    try:
                                        empresa, razaosocial, estab, cnpj = empresas[cnpj_cpf]
                                        enterprise, _ = EmpresasOmie.objects.get_or_create( cnpj_cpf = cnpj )
                                        enterprise.escritorio = escrit
                                        enterprise.cd_empresa = empresa
                                        enterprise.estab = estab
                                        enterprise.name_empresa = razaosocial
                                        enterprise.codigo_cliente_omie = client
                                        enterprise.email = email
                                        enterprise.save()
                                    except Exception as err:
                                        response.append(f"Erro ao Criar a Empresa: ({cnpj}) Cliente: {client} Empresa: {empresa}/{estab} | Erro:{str(err)}")
                                else:
                                    response.append(f"Este CNPJ/CPF não se encontra em nosso Banco: {cnpj_cpf} Escritório: {escrit} Cliente: {client} - {json_client['razao_social']}")
                            else:
                                error_text = json_client.get('message') or json_client.get('faultstring')
                                response.append(f"Erro ao Buscar este Cliente ({client}) do Escritório: {escrit} | Erro: {error_text}")
                                
                            self.update_state(
                                state='PROGRESS',
                                meta={'current': i + 1, 'total': total, 'escritorio': escrit, 'pag': page }
                            )
                            
                        if json_contrato.get("total_de_paginas") == page:
                            break
                    else:
                        error_text = json_contrato.get('message') or json_contrato.get('faultstring')
                        response.append(f"Erro ao Buscar os Contratos deste Escritório: {escrit}, Página: {page} | Erro: {error_text}")
                        break
                    
                    page += 1
                    time.sleep(0.5)
        dfErros = pd.DataFrame(response, columns=['Erro'])
        path_file = settings.BASE_DIR / f'temp/files/financeiro/boletos/Auditoria Update Empresas.xlsx'
        dfErros.to_excel(path_file, index=False)
    except Exception as err:
        raise Exception(err)
    else:
        return {"status": "concluido"}

@shared_task(bind=True)
def baixar_pdfs_e_processar(self, list_os, escritorio, filename):
    response_data = { 'errors': [] }
    try:
        list_clients_db = EmpresasOmie.objects.all()
        total = len(list_os)

        for i, os in enumerate(list_os):
            obj_os = list_os[os]
            num_os = obj_os['numOS']
            if 'cd_titulo' not in obj_os:
                response_data['errors'].append([os, num_os, "", "", "Não foi Encontrado o Código do Título (Sem Conta a Receber) para Gerar o Boleto"])
                continue
            cd_titulo = obj_os['cd_titulo']
            cd_cliente = obj_os['cd_cliente']
            cliente = list_clients_db.filter(codigo_cliente_omie=cd_cliente).first()
            if not cliente:
                response_data['errors'].append([os, num_os, cd_titulo, cd_cliente, "Cliente Não Encontrado na nossa Base de Bados, Atualize !!"])
                continue

            filename_os = str(cliente.cd_empresa).zfill(3) + f"{f'-{cliente.estab}' if int(cliente.estab) > 1 else ''}" + f" - {filename}.pdf"
            new_pdf = fitz.open()
            try:
                url_boleto = ""
                # TENTAR OBTER BOLETO
                data_get_boleto = get_request_to_api_omie(escritorio, "ObterBoleto", {"nCodTitulo": cd_titulo})
                result_obter_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_get_boleto, headers={'content-type': 'application/json'})
                json_obter_boleto = result_obter_boleto.json()
                if result_obter_boleto.status_code == 200:
                    if json_obter_boleto['cCodStatus'] == "0":
                        url_boleto = json_obter_boleto['cLinkBoleto']
                else:
                    raise Exception(f"Erro na API, rota de ObterBoleto: {json_obter_boleto}")
                
                if "https" not in url_boleto:
                    # GERAR BOLETO
                    data_gerar_boleto = get_request_to_api_omie(escritorio, "GerarBoleto", {"nCodTitulo": cd_titulo})
                    result_gerar_boleto = requests.post("https://app.omie.com.br/api/v1/financas/contareceberboleto/", json=data_gerar_boleto, headers={'content-type': 'application/json'})
                    json_gerar_boleto = result_gerar_boleto.json()
                    if result_gerar_boleto.status_code == 200:
                        if json_gerar_boleto['cCodStatus'] == "0":
                            if "https" not in json_gerar_boleto['cLinkBoleto']:
                                raise Exception(f"Não Veio a URL na ROTA GERANDO O BOLETO: {json_gerar_boleto['cDesStatus']}")
                            else:
                                url_boleto = json_gerar_boleto['cLinkBoleto']
                        else:
                            raise Exception(f"Erro na API, rota de GERAR BOLETO, Não Gerou o Boleto pelo Motivo: {json_gerar_boleto['cDesStatus']}")
                    else:
                        raise Exception(f"Erro na API, rota de GERAR BOLETO: {json_gerar_boleto}")
                    
                if "https" in url_boleto:
                    r = requests.get(url_boleto, timeout=25)
                    if r.status_code == 200:
                        try:
                            pdf_doc = fitz.open(stream=r.content, filetype="pdf")
                            try:
                                new_pdf.insert_pdf(pdf_doc)
                            except Exception as err:
                                raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
                            finally:
                                pdf_doc.close()
                        except Exception as err:
                            raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
                    else:
                        raise Exception(f"Erro no momento de requisitar o PDF")
                else:
                    raise Exception(f"Por algum motivo mesmo depois de buscar ou gerar, está sem URL")
                
                if new_pdf.page_count > 0:
                    data_get_pdf_os = get_request_to_api_omie(escritorio, "ObterOS", {"nIdOs": os})
                    result_obter_pdf_os = requests.post("https://app.omie.com.br/api/v1/servicos/osdocs/", json=data_get_pdf_os, headers={'content-type': 'application/json'})
                    json_obter_pdf_os = result_obter_pdf_os.json()
                    if result_obter_pdf_os.status_code == 200:
                        if json_obter_pdf_os['cCodStatus'] == "0" and "https" in json_obter_pdf_os['cPdfOs']:
                            r = requests.get(json_obter_pdf_os['cPdfOs'], timeout=25)
                            if r.status_code == 200:
                                try:
                                    pdf_doc = fitz.open(stream=r.content, filetype="pdf")
                                    try:
                                        new_pdf.insert_pdf(pdf_doc)
                                    except Exception as err:
                                        raise Exception(f"Erro no momento de Montar o PDF: {str(err)}")
                                    finally:
                                        pdf_doc.close()
                                except Exception as err:
                                    raise Exception(f"Erro no momento de requisitar o PDF: {str(err)}")
                            else:
                                raise Exception(f"Erro no momento de requisitar o PDF da OS")
                        else:
                            raise Exception(f"Rota de ObterOS, Erro pelo Código: {json_obter_pdf_os}")
                    else:
                        raise Exception(f"Erro na API, rota de ObterOS: {json_obter_pdf_os}")
                else:
                    raise Exception(f"Não Gerou PDF da OS, pois Não gerou o Boleto para")
                
            except Exception as err:
                response_data['errors'].append([os, num_os, cd_titulo, f"{cliente.cd_empresa} / {cliente.estab} - {cliente.name_empresa}", f"Erro ao Gerar o PDF: {str(err)}"])
            else:
                if new_pdf.page_count > 0:
                    path_file_pdf = settings.BASE_DIR / f'temp/files/financeiro/boletos/{escritorio}/{filename_os}'
                    new_pdf.save(path_file_pdf)
                else:
                    response_data['errors'].append([os, num_os, cd_titulo, f"{cliente.cd_empresa} / {cliente.estab} - {cliente.name_empresa}", "PDF VAZIO !!"])
            finally:
                new_pdf.close()
            
            # Atualiza progresso
            self.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': total}
            )
        gerar_arquivo_excel_auditoria_download_boletos(response_data['errors'], escritorio)
    except Exception as e:
        raise Exception(str(e))
    else:
        return {"status": "concluido"}