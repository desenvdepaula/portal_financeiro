from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views import View
import pandas as pd
from io import BytesIO
import datetime
import base64
import time
import requests
from celery.result import AsyncResult
import os
from django.conf import settings
from pathlib import Path

from .forms import OrdemServicoForm, ServicoForm
from .lib.controller import Controller
from core.views import get_request_to_api_omie
from .models import OrdemServico, DepartamentosControle, Servico, EmpresasOmie, OrdemServicoProvisoria
from relatorios.models import ClassificacaoServicos
from core.views import request_project_log, PDFFileView
    
class Departamento():
    
    def create(request):
        try:
            depart = DepartamentosControle.objects.create(nome_departamento=request.POST.get('text'))
        except Exception as err:
            return JsonResponse({"statusText": str(err)}, status=400)
        else:
            return JsonResponse({"id": depart.id, "name": depart.nome_departamento})
        
    def update(request):
        try:
            depart = DepartamentosControle.objects.get(id=request.POST.get('id'))
            new_name = request.POST.get('new_name')
            depart.nome_departamento = new_name
            depart.save()
        except Exception as err:
            return JsonResponse({"statusText": str(err)}, status=400)
        else:
            return JsonResponse({"name": new_name})

    def delete(request):
        try:
            DepartamentosControle.objects.get(id=request.POST.get('id')).delete()
        except Exception as err:
            return JsonResponse({"statusText": str(err)}, status=400)
        else:
            return JsonResponse({"msg": "Deletado com Sucesso !!"})
                
class EmpresasOmieView(View):
    template = "ordem_servico/empresas.html"

    def get(self, request, *args, **kwargs):
        context = { 'empresas': EmpresasOmie.objects.all() }
        return render(request, self.template, context)
    
    def update_empresa_omie(request):
        try:
            controller = Controller()
            if request.method == "GET":
                empresas_request = None
                escrit_list = None
            else:
                empresas_request = request.POST.getlist("select_empresas") or None
                escrit_list = request.POST.getlist("select_escritorios") or None
                
            empresas = controller.buscar_empresas_ativas_tareffa(empresas_request)
            response = controller.update_empresas_for_omie(empresas_request, escrit_list, empresas)
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            return JsonResponse(response)
        
    def get_status_total_update_empresa(request):
        try:
            path_file = settings.BASE_DIR / f'temp/files/financeiro/boletos/Auditoria Update Empresas.xlsx'
            df = pd.read_excel(path_file)
            return JsonResponse({'errors': df.values.tolist()})
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        
    def get_status_real_time_update_empresa(request, task_id):
        try:
            result = AsyncResult(task_id)
            if result.state == 'FAILURE' or (result.state == 'SUCCESS' and result.get() == 'FAILURE'):
                text_error = str(result.info)
                result.revoke(terminate=True)
                return JsonResponse({
                    "state": "FAILURE",
                    "info": {"message": text_error}
                })
            if not result.info:
                result.revoke(terminate=True)
                raise Exception("Sem INFOMAÇÔES NO RETORNO")
            return JsonResponse({
                "state": result.state,
                "info": result.info
            })
        except Exception as err:
            return JsonResponse({"state": "FAILURE", "info": {"message": str(err)}}, status=500)
            
class ServicosView(View):
    
    template = "ordem_servico/servicos.html"
    form = ServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        context['filters'] = set()
        context['servicos'] = Servico.objects.all()
        context['departamentos'] = DepartamentosControle.objects.all()
        context['classificacoes'] = ClassificacaoServicos.objects.all()
        for classificacao in context['classificacoes']:
            context['filters'].add(classificacao.classificacao)
            
        return render(request, self.template, context)
    
    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            try:
                departments_request = request.POST.getlist('departamentos')
                departments = context['form'].clean_departamentos(departments_request)
                nr_service = context['form'].cleaned_data.get('nr_service')
                tipo_servico = context['form'].cleaned_data.get('tipo_servico')
                if tipo_servico:
                    tipo_servico = ClassificacaoServicos.objects.get(id=tipo_servico)
                    
                if not nr_service:
                    cd_servico, name_servico = context['form'].clean_service(request.POST.get('servico'))
                    servico = Servico.objects.create(
                        cd_servico = cd_servico,
                        name_servico = name_servico,
                        tipo_servico = tipo_servico,
                        considera_custo = context['form'].cleaned_data.get('considera_custo'),
                        ativo = context['form'].cleaned_data.get('regra_ativa'),
                        classificacao = context['form'].cleaned_data.get('classificacao'),
                        observacoes = context['form'].cleaned_data.get('obs'),
                    )
                    for depart in departments:
                        servico.departamentos.add(depart)
                else:
                    service = Servico.objects.get(cd_servico=nr_service)
                    service.tipo_servico = tipo_servico
                    service.considera_custo = context['form'].cleaned_data.get('considera_custo')
                    service.ativo = context['form'].cleaned_data.get('regra_ativa')
                    service.classificacao = context['form'].cleaned_data.get('classificacao')
                    service.observacoes = context['form'].cleaned_data.get('obs')
                    
                    departments_service = [i.nome_departamento for i in service.departamentos.all()]
                    departments_to_add = departments.exclude(nome_departamento__in=departments_service)
                    departments_to_remove = service.departamentos.exclude(nome_departamento__in=departments_request)
                    for department_add in departments_to_add:
                        service.departamentos.add(department_add)
                    for department_remove in departments_to_remove:
                        service.departamentos.remove(department_remove)
                        
                    service.save()
                    
            except Exception as ex:
                messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
            else:
                messages.success(request, "Executado com Sucesso !!")
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            
        return redirect('controle_servicos_OS')
    
    def buscar_servico(request, nr_servico):
        try:
            service = Servico.objects.get(cd_servico=nr_servico)
            departamentos = [i.nome_departamento for i in service.departamentos.all()]
            service = vars(service)
            del service['_state']
            service['observacoes'] = "\n".join(service['observacoes'].split("\r\n")) if service['observacoes'] else ''
            service['departamentos'] = departamentos
            service['tipo_servico'] = ""
            classificacao = service.get('tipo_servico_id')
            if classificacao:
                classificacao = ClassificacaoServicos.objects.get(id=classificacao)
                service['tipo_servico'] = classificacao.classificacao
            return JsonResponse(service)
        except Exception as err:
            return JsonResponse({"statusText": str(err)}, status=400)
        
    def delete_service(request):
        try:
            Servico.objects.get(cd_servico=request.POST.get('id_service')).delete()
        except Exception as err:
            return JsonResponse({"statusText": str(err)}, status=400)
        else:
            return JsonResponse({"msg": "Deletado com Sucesso !!"})
        
    def dowload_relatorio_servicos_classificacoes(request):
        try:
            servicos_classificados = []
            for raw in Servico.objects.all():
                departamentos_service = " | ".join([depart.nome_departamento for depart in raw.departamentos.all()])
                servicos_classificados.append([
                    int(raw.escritorio),
                    int(raw.cd_servico),
                    raw.name_servico,
                    raw.tipo_servico.classificacao if raw.tipo_servico else '',
                    departamentos_service,
                    "ATIVO" if raw.ativo else "INATIVO",
                    "SIM" if raw.considera_custo else "NÃO",
                    raw.classificacao,
                    raw.observacoes
                ])
            
            df = pd.DataFrame(servicos_classificados, columns=['ESCRITÓRIO', 'CODIGO', 'SERVIÇO', 'CLASSIFICAÇÃO DO SERVIÇO', 'DEPARTAMENTOS', 'STATUS', 'CONSIDERA NO CUSTO', 'CLASSIFICAÇÃO NO CUSTO', 'OBSERVAÇÕES'])
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                df.to_excel(writer, sheet_name='Comparação', index = False)
                writer.sheets['Comparação'].set_column('A:B', 15, alignCenter)
                writer.sheets['Comparação'].set_column('C:C', 75, alignCenter)
                writer.sheets['Comparação'].set_column('D:E', 60, alignCenter)
                writer.sheets['Comparação'].set_column('F:H', 30, alignCenter)
                writer.sheets['Comparação'].set_column('I:I', 120, alignCenter)
                writer.close()
                filename = 'Relatório Serviços e Classificações.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
        except Exception as err:
            messages.error(request, f"Erro ao Baixar O Relatório: {str(err)}")
            return redirect('controle_servicos_OS')

    def request_update_all_services_omie(request):
        if request.method == 'GET':
            escritorios = ['501', '502', '505', '567', '575']
        else:
            escritorios = ['501', '502', '505', '567', '575'] if request.POST.get("escritorio") == 'all' else request.POST.getlist("escritorio")
        try:
            for escrit in escritorios:
                page = 1
                while True:
                    data_get_service = get_request_to_api_omie(escrit, "ListarCadastroServico", {"nPagina": page, "nRegPorPagina": 500, "inativo": "N", "cExibirProdutos": "N"})
                    result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/servico/", json=data_get_service, headers={'content-type': 'application/json'})
                    json_contrato = result_contrato.json()
                    if result_contrato.status_code == 200:
                        for serv in json_contrato.get("cadastros"):
                            servico, _ = Servico.objects.get_or_create( cd_servico = serv['intListar'].get("nCodServ") )
                            servico.name_servico = serv['descricao'].get("cDescrCompleta")
                            servico.escritorio = escrit
                            servico.save()
                        if json_contrato.get("nTotPaginas") == page:
                            break
                    else:
                        raise Exception(f"Erro ao Buscar os Serviços da {escrit} página {page}: {json_contrato}")
                    
                    page += 1
                    time.sleep(0.7)
        except Exception as err:
            return JsonResponse({"message": f"Erro na Operação: {err}"}, status=400)
        else:
            return JsonResponse({})
    
class OrdemServicoView(View):
    
    template = "ordem_servico/index.html"
    form = OrdemServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        context['ordens'] = OrdemServico.objects.all()
        context['empresas'] = EmpresasOmie.objects.all()
            
        for ordem in context['ordens']:
            ordem.data_cobranca = ordem.data_cobranca.strftime('%d/%m/%Y')
            preco = float(ordem.valor)
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem.valor = preco_final
            if ordem.cod_os_omie == 'OS AVULSA':
                ordem.os_avulsa = True
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        try:
            file = request.FILES.get("file_obrigacoes").temporary_file_path() if "file_obrigacoes" in request.FILES else None
            if file:
                response_file = []
                extention_file = "ods" if ".ods" in request.FILES.get("file_obrigacoes").name else "xlsx"
                if extention_file == "ods":
                    df = pd.read_excel(file, engine="odf")
                else:
                    df = pd.read_excel(file)
                df.fillna(0, inplace=True)
                controller = Controller()
                codigos_servicos = {
                    '501': {'DMED': "11019827066 * DMED - DECLARACAO DE SERVICOS MEDICOS", 'DIMOB': "11019827043 * DIMOB - ATIVIDADES IMOBILIARIA", 'ECD': "11019827085 * ECD - ESCRITURACAO CONTABIL DIGITAL", 'ECF': "11019827091 * ECF - ESCRITURACAO CONTABIL FISCAL", 'DEFIS': "11019827037 * DEFIS - DECLARACAO INFORMACOES SOCIOECONOMICAS E FISCAIS", 'IBGE': "11019827196 * IBGE - DECLARACAO PERIODO - ESCRITA FISCAL", 'CBE': "11019826974 * CBE - DECLARACAO DE CAPITAL BR NO EXTERIOR - OBRIGACOES ACESSORIAS", 'INATIVA': "11019827016 * DECLARACAO INATIVA - OBRIGACOES ACESSORIAS", 'ATA': "11019826883 * ATA DE REUNIAO SOCIOS - DEMONSTRACOES CONTABEIS - IMPLANTACAO", 'DIRPF': "11019827061 * DIRPF - DECLARACAO IMPOSTO DE RENDA PESSOA FISICA"},
                    '502': {'DMED': "4423461903 * DMED - DECLARACAO DE SERVICOS MEDICOS", 'DIMOB': "4423461885 * DIMOB - ATIVIDADES IMOBILIARIA", 'ECD': "4423461912 * ECD - ESCRITURACAO CONTABIL DIGITAL", 'ECF': "4423461916 * ECF - ESCRITURACAO CONTABIL FISCAL", 'DEFIS': "4423461878 * DEFIS - DECLARACAO INFORMACOES SOCIOECONOMICAS E FISCAIS", 'IBGE': "4423462116 * IBGE - DECLARACAO PERIODO - ESCRITA FISCAL", 'CBE': "4423461781 * CBE - DECLARACAO DE CAPITAL BR NO EXTERIOR - OBRIGACOES ACESSORIAS", 'INATIVA': "4423461860 * DECLARACAO INATIVA - OBRIGACOES ACESSORIAS", 'ATA': "4423461652 * ATA DE REUNIAO SOCIOS - DEMONSTRACOES CONTABEIS - IMPLANTACAO", 'DIRPF': "4423461899 * DIRPF - DECLARACAO IMPOSTO DE RENDA PESSOA FISICA"},
                    '505': {'DMED': "8601960788 * DMED - DECLARACAO DE SERVICOS MEDICOS", 'DIMOB': "8601960765 * DIMOB - ATIVIDADES IMOBILIARIA", 'ECD': "8601960808 * ECD - ESCRITURACAO CONTABIL DIGITAL", 'ECF': "8601960813 * ECF - ESCRITURACAO CONTABIL FISCAL", 'DEFIS': "8601960761 * DEFIS - DECLARACAO INFORMACOES SOCIOECONOMICAS E FISCAIS", 'IBGE': "8601960931 * IBGE - DECLARACAO PERIODO - ESCRITA FISCAL", 'CBE': "8601960537 * CBE - DECLARACAO DE CAPITAL BR NO EXTERIOR - OBRIGACOES ACESSORIAS", 'INATIVA': "8601960722 * DECLARACAO INATIVA - OBRIGACOES ACESSORIAS", 'ATA': "8601960390 * ATA DE REUNIAO SOCIOS - DEMONSTRACOES CONTABEIS - IMPLANTACAO", 'DIRPF': "8601960783 * DIRPF - DECLARACAO IMPOSTO DE RENDA PESSOA FISICA"},
                    '567': {'DMED': "2641525825 * DMED - DECLARACAO DE SERVICOS MEDICOS", 'DIMOB': "2641525806 * DIMOB - ATIVIDADES IMOBILIARIA", 'ECD': "2641525835 * ECD - ESCRITURACAO CONTABIL DIGITAL", 'ECF': "2641525845 * ECF - ESCRITURACAO CONTABIL FISCAL", 'DEFIS': "2641525800 * DEFIS - DECLARACAO INFORMACOES SOCIOECONOMICAS E FISCAIS", 'IBGE': "2641525965 * IBGE - DECLARACAO PERIODO - ESCRITA FISCAL", 'CBE': "2641525708 * CBE - DECLARACAO DE CAPITAL BR NO EXTERIOR - OBRIGACOES ACESSORIAS", 'INATIVA': "2641525777 * DECLARACAO INATIVA - OBRIGACOES ACESSORIAS", 'ATA': "2641525592 * ATA DE REUNIAO SOCIOS - DEMONSTRACOES CONTABEIS - IMPLANTACAO", 'DIRPF': "2641525820 * DIRPF - DECLARACAO IMPOSTO DE RENDA PESSOA FISICA"},
                    '575': {'DMED': "3838357573 * DMED - DECLARACAO DE SERVICOS MEDICOS", 'DIMOB': "3838357533 * DIMOB - ATIVIDADES IMOBILIARIA", 'ECD': "3838357593 * ECD - ESCRITURACAO CONTABIL DIGITAL", 'ECF': "3838357600 * ECF - ESCRITURACAO CONTABIL FISCAL", 'DEFIS': "3838357527 * DEFIS - DECLARACAO INFORMACOES SOCIOECONOMICAS E FISCAIS", 'IBGE': "3838357735 * IBGE - DECLARACAO PERIODO - ESCRITA FISCAL", 'CBE': "3838357276 * CBE - DECLARACAO DE CAPITAL BR NO EXTERIOR - OBRIGACOES ACESSORIAS", 'INATIVA': "3838357504 * DECLARACAO INATIVA - OBRIGACOES ACESSORIAS", 'ATA': "3838357022 * ATA DE REUNIAO SOCIOS - DEMONSTRACOES CONTABEIS - IMPLANTACAO", 'DIRPF': "3838357565 * DIRPF - DECLARACAO IMPOSTO DE RENDA PESSOA FISICA"},
                }
                
                for cd_empresa, name, servico, obs_servico, valor in df.values.tolist():
                    if servico == 0 or servico == '0':
                        continue 
                    hoje = datetime.date.today()
                    try:
                        type_service = controller.get_type_file_obrigacoes(servico)
                    except Exception as ex:
                        response_file.append(str(ex))
                        continue
                    obs_servico = obs_servico.replace("–","-")
                    emp = EmpresasOmie.objects.filter(cd_empresa=int(cd_empresa)).first()
                    if emp:
                        obj_os = {'descricao': obs_servico, 'descricao_servico': obs_servico, 'data': hoje, 'data_cobranca': hoje, 'quantidade': 1, 'execucao': '00:08', 'valor': valor, 'autorizacao': True, 'solicitacaoLocal': 'INTERNA', 'solicitacao': request.user.username, 'executado': request.user.username, 'servico': codigos_servicos[emp.escritorio][type_service]}
                        os_return = controller.update_ordem_servico(obj_os, request.user.username, emp, True)
                        if os_return['status'] != 200:
                            response_file.append(os_return['obj']['message'])
                    else:
                        response_file.append(f"Empresa: {int(cd_empresa)} - {name}, Não Consta na Base de Dados OMIE")
                return JsonResponse({'list_erros': response_file})
            else:
                if context['form'].is_valid():
                    empresa_db = EmpresasOmie.objects.get(codigo_cliente_omie=request.POST.get("id_empresa"))
                    context['form'].clean_log(request.user.username, empresa_db.cd_empresa)
                    controller = Controller()
                    os_return = controller.update_ordem_servico(context['form'].cleaned_data, request.user.username, empresa_db)
                    return JsonResponse(os_return['obj'], status=os_return['status'])
                else:
                    raise Exception("Ocorreu um erro no Formulário, Verifique Novamente")
        except Exception as ex:
            return JsonResponse({"message": str(ex)}, status=500)
        
    def request_get_services_escritorio(request):
        try:
            response = {'servicos': []}
            for service in Servico.objects.filter(escritorio=request.POST.get("escritorio")):
                response['servicos'].append([service.cd_servico, service.name_servico])
        except Exception as err:
            return JsonResponse({"message": f"Erro na Operação: {err}"}, status=400)
        else:
            return JsonResponse(response)
        
    def debitar_em_lote(request):
        try:
            request_project_log(0, "", "ORDEM DE SERVIÇO / DEBITAR ORDEM EM LOTE", request.user.username)
            response_data = {}
            type_lanc = request.POST.get('select_lanc')
            list_ordens = request.POST.getlist('orders[]')
            file = request.FILES.get("arquivo_os").temporary_file_path() if "arquivo_os" in request.FILES else None
            datas = [request.POST.get('data_inicio_debito') or None, request.POST.get('data_final_debito') or None]
            escritorio_lote = request.POST.getlist('select_escritorio_lote') if request.POST.get('select_escritorio_lote') else ['501', '502', '505', '567', '575']
            controller = Controller()
            sucessos, errors, erros_gerais = controller.debitar_em_lote_ordem_servico(type_lanc, list_ordens, file, datas, escritorio_lote)
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            dfSucessos = pd.DataFrame(sucessos, columns=['OS', 'ESCRITORIO'])
            dfErros = pd.DataFrame(errors, columns=['ID OS', 'CÓDIGO EMPRESA', 'NOME', 'CNPJ', 'ESCRIT.','DESCRIÇÃO DO ERRO'])
            dfErrosGerais = pd.DataFrame(erros_gerais, columns=['ESCRITORIO', 'DESCRIÇÃO DO ERRO'])
            response_data['auditoria'] = controller.gerar_arquivo_excel_auditoria_debitos(dfSucessos, dfErros, dfErrosGerais)
            return JsonResponse(response_data)
        
    def delete(request):
        try:
            ordem = OrdemServico.objects.get(id=int(request.POST.get('id_ordem')))
            cd_empresa = ordem.empresa.cd_empresa if ordem.empresa else 0
            text = f"Serviço: {ordem.servico}, Realizado: {ordem.data_realizado}, Executado: {ordem.executado}, Quantidade: {ordem.quantidade}, Valor: {ordem.valor}"
            ordem.delete()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            request_project_log(cd_empresa, text, "ORDEM DE SERVIÇO / DELETAR ORDEM", request.user.username)
            return JsonResponse({'msg': 'correto'})
        
    def buscar_ordem_servico(request, id_ordem):
        try:
            ordem_db = OrdemServico.objects.get(id=id_ordem)
            ordem = vars(ordem_db)
            if ordem_db.empresa:
                empresa = vars(ordem_db.empresa)
                del empresa['_state']
                ordem['empresa'] = empresa
            del ordem['_state']
            ordem['data_cobranca'] = ordem['data_cobranca'].strftime('%d/%m/%Y')
            ordem['data_realizado'] = ordem['data_realizado'].strftime('%d/%m/%Y')
            preco = float(ordem['valor'])
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem['valor'] = preco_final
            return JsonResponse(ordem)
        except Exception as err:
            raise Exception(err)
        
    def request_debitar_ordem_servico(request, id_ordem):
        try:
            controller = Controller()
            controller.debitar_omie_ordem_servico(id_ordem)
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
            
    def request_aprovar_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=int(id_ordem))
            ordem.aprovado = not ordem.aprovado
            ordem.save()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
        
    def request_arquivar_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=int(id_ordem))
            ordem.arquivado = not ordem.arquivado
            ordem.aprovado = False
            ordem.save()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
        
    def request_avulso_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=int(id_ordem))
            ordem.cod_os_omie = 'OS AVULSA'
            ordem.save()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
        
    def request_download_boletos_escritorio(request):
        try:
            compet_atual = datetime.date.today().strftime("%m%Y")
            escritorio = request.POST.get("select_escritorio")
            file = request.FILES.get("arquivo_os")
            filename = request.POST.get("select_filename").replace("/", "").replace("MESANO", compet_atual).replace("mesano", compet_atual)
            controller = Controller()
            controller.delete_pdf_os(escritorio)
            response = controller.gerar_boletos_por_escritorio(escritorio, file, filename)
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            return JsonResponse(response, status=200)

    def request_download_planilha(request):
        try:
            controller = Controller()
            return controller.gerarPlanilhasOrdens(request.POST)
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
        return redirect('list_ordem_servico')
    
    def request_download_pdfs_boletos(request, escritorio):
        zip_view = PDFFileView()
        try:
            response = {}
            tmpdir = settings.BASE_DIR / f'temp/files/financeiro/boletos/{escritorio}'
            files = os.listdir(tmpdir)
            if not files:
                raise Exception(f"Nenhum PDF foi gerado no Escritório: {escritorio}")
            else:
                list_files = {}
                for file in files:
                    product_file = Path(os.path.join(tmpdir, file))
                    with open(product_file, 'rb') as f:
                        list_files[file] = f.read()
                zip_file = zip_view.prepare_zip_file_content(list_files)
                response['files_zip'] = base64.b64encode(zip_file).decode('utf-8')
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            return JsonResponse(response, status=200)
    
    def status_task(request, task_id):
        try:
            result = AsyncResult(task_id)
            if result.state == 'FAILURE' or (result.state == 'SUCCESS' and result.get() == 'FAILURE'):
                text_error = str(result.info)
                result.revoke(terminate=True)
                return JsonResponse({
                    "state": "FAILURE",
                    "info": {"message": text_error}
                })
            if not result.info:
                result.revoke(terminate=True)
                raise Exception("Sem INFOMAÇÔES NO RETORNO")
            return JsonResponse({
                "state": result.state,
                "info": result.info
            })
        except Exception as err:
            return JsonResponse({"state": "FAILURE", "info": {"message": str(err)}}, status=500) 
    
    def verify_pdf_os(request, escritorio):
        try:
            tmpdir = settings.BASE_DIR / f'temp/files/financeiro/boletos/{escritorio}'
            files = os.listdir(tmpdir)
            return JsonResponse({'files': len(files)}, status=200)
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        
class OrdensProvisoriasView(View):
    
    template = "ordem_servico/provisorias.html"
    form = OrdemServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        context['ordens'] = OrdemServicoProvisoria.objects.all()
        context['empresas'] = EmpresasOmie.objects.all()
            
        for ordem in context['ordens']:
            ordem.data_cobranca = ordem.data_cobranca.strftime('%d/%m/%Y')
            preco = float(ordem.valor)
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem.valor = preco_final
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        try:
            ordem = OrdemServicoProvisoria.objects.get(id=int(request.POST.get('id_ordem')))
            try:
                controller = Controller()
                cd_serv, name_serv = request.POST.get("servico").split(" * ")
                ordem.departamento = request.POST.get("id_departamento")
                ordem.cd_servico = cd_serv
                ordem.servico = name_serv
                ordem.ds_servico = request.POST.get("descricao")
                ordem.observacoes_servico = request.POST.get("descricao_servico")
                ordem.cd_empresa = request.POST.get("id_empresa")
                ordem.nome_empresa = request.POST.get("name_empresa")
                ordem.data_realizado = request.POST.get("data")
                ordem.data_cobranca = request.POST.get("data_cobranca")
                ordem.quantidade = request.POST.get("quantidade")
                ordem.hora_trabalho = controller.validar_tempo_execucao(request.POST.get('execucao'))
                ordem.valor = float(request.POST.get("valor").replace('.','').replace(',','.'))
                ordem.autorizado_pelo_cliente = True if request.POST.get("autorizacao") == 'SIM' else False
                ordem.type_solicitacao = request.POST.get("solicitacaoLocal")
                ordem.solicitado = request.POST.get("solicitacao")
                ordem.executado = request.POST.get("executado")
                ordem.save()
                return JsonResponse({"message": "Alterado"})
            except Exception as ex:
                raise Exception(ex)
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        
    def delete_provisoria(request):
        try:
            ordem = OrdemServicoProvisoria.objects.get(id=int(request.POST.get('id_ordem')))
            text = f"Serviço: {ordem.servico}, Realizado: {ordem.data_realizado}, Executado: {ordem.executado}, Quantidade: {ordem.quantidade}, Valor: {ordem.valor}"
            ordem.delete()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            request_project_log(0, text, "ORDEM DE SERVIÇO PROVISÓRIO / DELETAR ORDEM", request.user.username)
            return JsonResponse({'msg': 'correto'})
        
    def criar_os_real(request, id_ordem):
        try:
            order_db = OrdemServicoProvisoria.objects.get(id=id_ordem)
            ordem = vars(order_db).copy()
            del ordem['_state']
            del ordem['os_criada']
            del ordem['arquivado']
            del ordem['id']
            if ordem.get("cd_empresa") == '0':
                raise Exception("Nenhuma EMPRESA foi Selecionada Nesta Ordem de Serviço")
            if ordem.get("cd_servico") == '0':
                raise Exception("Nenhuma SERVIÇO foi Selecionado Nesta Ordem de Serviço")
            empresa_db = EmpresasOmie.objects.get(codigo_cliente_omie=ordem['cd_empresa'])
            new_order = OrdemServico(**ordem)
            new_order.empresa = empresa_db
            new_order.save()
            order_db.os_criada = True
            order_db.save()
        except Exception as err:
            return JsonResponse({'error': str(err)}, status=500)
        else:
            return JsonResponse({'message': "OS CRIADA COM SUCESSO !!"})
        
    def buscar_ordem_servico_provisoria(request, id_ordem):
        try:
            ordem = OrdemServicoProvisoria.objects.get(id=id_ordem)
            ordem = vars(ordem)
            del ordem['_state']
            ordem['data_cobranca'] = ordem['data_cobranca'].strftime('%d/%m/%Y')
            ordem['data_realizado'] = ordem['data_realizado'].strftime('%d/%m/%Y')
            preco = float(ordem['valor'])
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem['valor'] = preco_final
            return JsonResponse(ordem)
        except Exception as err:
            raise Exception(err)
            
    def request_arquivar_ordem_servico_provisoria(request, id_ordem):
        try:
            ordem = OrdemServicoProvisoria.objects.get(id=int(id_ordem))
            ordem.arquivado = not ordem.arquivado
            ordem.save()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)