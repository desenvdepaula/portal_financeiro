from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views import View
import pandas as pd
from io import BytesIO
import datetime
import base64
import requests

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
    
    def post(self, request, *args, **kwargs):
        try:
            controller = Controller()
            empresas = request.POST.getlist("select_empresas") or None
            response = controller.update_empresas_for_omie(empresas)
            # response = {'errors': ['Este CNPJ/CPF não se encontra em nosso Banco: 00.304.148/0001-10 Escritório: 501 Cliente: 11017049475','Este CNPJ/CPF não se encontra em nosso Banco: 650.040.948-53 Escritório: 502 Cliente: 4421084722','Este CNPJ/CPF não se encontra em nosso Banco: 45.372.763/0001-00 Escritório: 502 Cliente: 4421082417','Este CNPJ/CPF não se encontra em nosso Banco: 81.506.842/0001-11 Escritório: 502 Cliente: 4421085603','Este CNPJ/CPF não se encontra em nosso Banco: 59.564.932/0001-00 Escritório: 505 Cliente: 8596021541','Este CNPJ/CPF não se encontra em nosso Banco: 55.257.460/0001-91 Escritório: 505 Cliente: 8596020152','Erro ao Buscar este Cliente (8596016064) do Escritório: 505 | Erro: SOAP-ERROR: Broken response from Application Server (BG)','Erro ao Buscar este Cliente (8596019650) do Escritório: 505 | Erro: SOAP-ERROR: Broken response from Application Server (BG)','Este CNPJ/CPF não se encontra em nosso Banco: 175.788.769-53 Escritório: 575 Cliente: 3835127619','Este CNPJ/CPF não se encontra em nosso Banco: 089.376.289-02 Escritório: 575 Cliente: 3830611943']}
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            return JsonResponse(response)
            
class ServicosView(View):
    
    template = "ordem_servico/servicos.html"
    form = ServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        controller = Controller()
        context['filters'] = set()
        context['servicos'] = Servico.objects.all()
        context['servicos_questor'] = controller.get_servicos_questor(context['servicos'])
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
            service['observacoes'] = "\n".join(service['observacoes'].split("\r\n"))
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
            controller = Controller()
            servicos = controller.get_servicos_questor()
            dfServicos = pd.DataFrame(servicos, columns=['CODIGO', 'DESCRICAO']).sort_values(by=['CODIGO'])
            
            servicos_classificados = []
            for raw in Servico.objects.all():
                departamentos_service = " | ".join([depart.nome_departamento for depart in raw.departamentos.all()])
                servicos_classificados.append([
                    int(raw.cd_servico),
                    raw.tipo_servico.classificacao if raw.tipo_servico else '',
                    departamentos_service,
                    "ATIVO" if raw.ativo else "INATIVO",
                    "SIM" if raw.considera_custo else "NÃO",
                    raw.classificacao
                ])
            
            dfClassificacoes = pd.DataFrame(servicos_classificados, columns=['CODIGO', 'CLASSIFICAÇÃO DO SERVIÇO', 'DEPARTAMENTOS', 'STATUS', 'CONSIDERA NO CUSTO', 'CLASSIFICAÇÃO NO CUSTO'])
            
            df = dfServicos.merge(dfClassificacoes, how='left', on='CODIGO')
            df.fillna(" ", inplace=True)
            with BytesIO() as b:
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                df.to_excel(writer, sheet_name='Comparação', index = False)
                writer.sheets['Comparação'].set_column('A:A', 15, alignCenter)
                writer.sheets['Comparação'].set_column('B:C', 60, alignCenter)
                writer.sheets['Comparação'].set_column('D:D', 50, alignCenter)
                writer.sheets['Comparação'].set_column('E:G', 30, alignCenter)
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
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        try:
            if context['form'].is_valid():
                empresa_db = EmpresasOmie.objects.get(codigo_cliente_omie=request.POST.get("id_empresa"))
                context['form'].clean_log(request.user.username, empresa_db.cd_empresa)
                controller = Controller()
                return controller.update_ordem_servico(context['form'].cleaned_data, request.user.username, empresa_db)
            else:
                raise Exception("Ocorreu um erro no Formulário, Verifique Novamente")
        except Exception as ex:
            return JsonResponse({"error": str(ex)}, status=500)
        
    def request_get_services_escritorio(request):
        escrit = request.POST.get("escritorio")
        try:
            response = {'servicos': []}
            data_get_service = get_request_to_api_omie(escrit, "ListarCadastroServico", {"nPagina": 1, "nRegPorPagina": 1000})
            result_contrato = requests.post("https://app.omie.com.br/api/v1/servicos/servico/", json=data_get_service, headers={'content-type': 'application/json'})
            json_contrato = result_contrato.json()
            if result_contrato.status_code == 200:
                for serv in json_contrato.get("cadastros"):
                    response['servicos'].append([serv['intListar'].get("nCodServ"), serv['descricao'].get("cDescrCompleta")])
            else:
                raise Exception(f"{json_contrato}")
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
            
    def request_arquivar_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=int(id_ordem))
            ordem.arquivado = not ordem.arquivado
            ordem.save()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
        
    def request_download_boletos_escritorio(request):
        zip_view = PDFFileView()
        response_data = {}
        try:
            compet_atual = datetime.date.today().strftime("%m%Y")
            controller = Controller()
            escritorio = request.POST.get("select_escritorio")
            file = request.FILES.get("arquivo_os")
            filename = request.POST.get("select_filename").replace("/", "").replace("MESANO", compet_atual).replace("mesano", compet_atual)
            
            response = controller.gerar_boletos_por_escritorio(escritorio, file, filename)
            dfSucessos = pd.DataFrame(response['success'], columns=['OS', 'DESCRIÇÃO DA REQUISIÇÃO'])
            dfErros = pd.DataFrame(response['errors'], columns=['OS', 'TITULO', 'CLIENTE', 'DESCRIÇÃO DO ERRO'])
            auditoria_file = controller.gerar_arquivo_excel_auditoria_download_boletos(dfSucessos, dfErros)
            response['files']["Auditoria de Boletos.xlsx"] = auditoria_file
            zip_file = zip_view.prepare_zip_file_content(response.get("files"))
            response_data['escritorio'] = escritorio
            response_data['files_zip'] = base64.b64encode(zip_file).decode('utf-8')
        except Exception as err:
            return JsonResponse({"message": str(err)}, status=500)
        else:
            return JsonResponse(response_data, status=200)

    def request_download_planilha(request):
        try:
            controller = Controller()
            return controller.gerarPlanilhasOrdens(request.POST)
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
        return redirect('list_ordem_servico')
    
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