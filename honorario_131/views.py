from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.conf import settings
import zipfile
import os
from django.contrib import messages
from django.views import View
from weasyprint import HTML

from .forms import RelatorioHonorariosForm, RegrasHonorariosForm, RegrasHonorariosUpdateForm, RealizarCalculoForm

from .lib.controller import Controller
from .models import RegrasHonorario
from .lib.database import ManagerTareffa

def request_realizar_calculo_honorario_131(request):
    context = {'form': RealizarCalculoForm(request.POST or None)}
    if context['form'].is_valid():
        try:
            controller = Controller()
            return controller.gerarHonorarios(
                context['form'].cleaned_data['compet'],
                context['form'].cleaned_data['data'],
            )
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
    else:
        messages.error(request, "Erro no Formulário, tente Novamente !")
        
    return redirect('regras_honorario_131')

def request_realizar_auditoria_honorario_131(request):
    pass
    
class RegrasHonorarioView(View):
    
    template = "honorario_131/regras_honorario.html"
    form = RegrasHonorariosForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        context['regras'] = RegrasHonorario.objects.all()
        for regra in context['regras']:
            regra.calcular = "CALCULAR" if regra.calcular else "SEM USO"
            regra.somar_filiais = "SOMAR FILIAIS" if regra.somar_filiais else "NÃO SOMAR"
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            try:
                RegrasHonorario.objects.create(
                    cd_financeiro = context['form'].cleaned_data['cd_financeiro'],
                    cd_empresa = context['form'].cleaned_data['cd_empresa'],
                    cd_filial = context['form'].cleaned_data['cd_filial'],
                    razao_social = context['form'].cleaned_data['razao_social'],
                    calcular = True if 'calcular' in request.POST else False,
                    somar_filiais = True if 'somar_filiais' in request.POST else False,
                    limite = context['form'].cleaned_data['limite'],
                    valor = context['form'].cleaned_data['valor']
                )
            except Exception as ex:
                messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
            else:
                messages.success(request, "Criado com sucesso")
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            
        return redirect('regras_honorario_131')
    
    def validarCreateRegraHonorario(request):
        try:
            cd_financeiro = request.POST.get('cd_financeiro')
            cd_empresa = request.POST.get('cd_empresa')
            cd_filial = request.POST.get('cd_filial')
            somar_filiais = True if request.POST.get('somar_filiais') == 'true' else False
            
            listFilterCodFinanceiro = RegrasHonorario.objects.filter(cd_financeiro=cd_financeiro)
            listFilterCodEmpresa = RegrasHonorario.objects.filter(cd_empresa=cd_empresa)
            
            if len(listFilterCodFinanceiro) > 0:
                return JsonResponse({'msg': f'Já existe uma Regra com o Número Financeiro: {cd_financeiro}, Tente Novamente'}, status=400)
            
            if len(listFilterCodEmpresa) > 0:
                regrasFiliaisIguais = []
                regrasSomaFiliais = []
                regrasNaoSomaFiliais = []
                for regra in listFilterCodEmpresa:
                    if regra.cd_filial == cd_filial:
                        regrasFiliaisIguais.append(regra)
                    if regra.somar_filiais:
                        regrasSomaFiliais.append(regra)
                    if not regra.somar_filiais:
                        regrasNaoSomaFiliais.append(regra)
                
                if regrasFiliaisIguais:
                    return JsonResponse({'msg': f'Já existe uma Regra com Esta Filial: {cd_filial}'}, status=400)
                
                if regrasSomaFiliais:
                    return JsonResponse({'msg': f'Existe uma Regra que Soma todas as Filiais desta Empresa'}, status=400)
                
                if somar_filiais and len(regrasNaoSomaFiliais) > 0:
                    msg = 'Existe mais Regras Para Filiais com Esta Empresa. <br>'
                    for rule in regrasNaoSomaFiliais:
                        msg += f"Empresa: <b>{rule.cd_empresa}</b> Filial: <b>{rule.cd_filial}</b> | Soma Filiais: {'SIM' if rule.somar_filiais else 'NÃO'} |Calcula: {'SIM' if rule.calcular else 'NÃO'} <br>"
                    return JsonResponse({'msg': msg}, status=400)
            
            return JsonResponse({'msg': 'Valido'})
        except Exception as err:
            return JsonResponse({'msg': err}, status=400)
    
    def delete(request):
        try:
            RegrasHonorario.objects.get(cd_financeiro=int(request.POST.get('cd_financeiro'))).delete()
            return JsonResponse({'msg': 'correto'})
        except Exception as err:
            raise Exception(err)
        
    def update(request):
        context = { 'form': RegrasHonorariosUpdateForm(request.POST or None) }
        if context['form'].is_valid():
            try:
                regrasCalculadas = []
                regra = RegrasHonorario.objects.get(cd_financeiro=int(context['form'].cleaned_data['cd_financeiro_update']))
                if 'somar_filiais_update' in request.POST: 
                    for rule in RegrasHonorario.objects.filter(cd_empresa=regra.cd_empresa):
                        if rule.calcular and rule.cd_filial != regra.cd_filial:
                            regrasCalculadas.append(rule)
                
                if regrasCalculadas:
                    messages.error(request, f'Existem Regras Calculadas na Empresa {regra.cd_empresa} nas Filiais: {[int(row.cd_filial) for row in regrasCalculadas]}')
                else:
                    regra.calcular = True if 'calcular_update' in request.POST else False
                    regra.somar_filiais = True if 'somar_filiais_update' in request.POST else False
                    regra.limite = context['form'].cleaned_data['limite_update']
                    regra.valor = float(context['form'].cleaned_data['valor_update'].replace('.', '').replace(',', '.'))
                    regra.save()
                    messages.success(request, "Alterado com sucesso")
                    
            except Exception as err:
                messages.error(request, err)
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            
        return redirect('regras_honorario_131')
    
    def buscar_empresa(request, cd_empresa):
        try:
            manager = ManagerTareffa(cd_empresa)
            list_empresa = manager.get_empresa()
            if isinstance(list_empresa, list):
                response = {
                    'nome_empresa': list_empresa[0][1],
                    'filiais': [empresa[0] for empresa in list_empresa],
                }
                return JsonResponse({'response': response, 'status': 200})
            else:
                return JsonResponse({'msg': 'Ocorreu um Erro no Servidor', 'status': 400})
        except:
            raise Exception('Invalid')
            
class RelatorioHonorarioView(View):

    template = "./honorario_131/relatorioHonorario.html"
    template_contrato = "./honorario_131/contrato.html"
    form = RelatorioHonorariosForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None), 'validation_errors': [] }
        empresas = request.POST.getlist('cod_emp')
        if context['form'].is_valid():
            if len(empresas) == 0 or empresas == None:
                context['validation_errors'].append("Ao menos o código de uma empresa deve ser informado.")
            else:
                try:
                    controller = Controller(True)
                    lista = list(filter(None, empresas))
                    pdfs = {}

                    for empresa in lista:
                        context = controller.gerarRelatorioHonorarios(empresa)
                        contrato_pdf = self.get_pdf_contrato(request, context)
                        pdfs[empresa] = contrato_pdf

                    if len(lista) > 1:
                        response = self.get_zipped_file(request, pdfs)
                    else:
                        pdf = self.get_pdf_contrato(request, context)
                        response = self.get_file_response(pdf, f"Relatorio Numero de Empregados - {lista[0]}")

                    return response

                except Exception as ex:
                    messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
        return render(request, self.template, context)

    def get_zipped_file(self,request, listPdf):
        zipfile_name = 'temp/files/honorario131.zip'
        path = str( settings.BASE_DIR / zipfile_name )
        zip_file = zipfile.ZipFile(path, 'w')

        for empresa in listPdf.keys():
            zip_file.writestr(f'Relatorio Numero de Empregados - {empresa}.pdf', listPdf[empresa])

        zip_file = open(path, 'rb')
        response = HttpResponse(zip_file, content_type="application/zip")
        response['Content-Disposition'] = 'filename="%s"' % 'honorario.zip'
        os.remove(path)
        return response

    def get_pdf_contrato(self, request, context):
        html_string = render_to_string(self.template_contrato, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        return pdf

    def get_file_response(self, file, filename):
        response = HttpResponse(file)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'filename="{0}.pdf"'.format(filename)
        return response

