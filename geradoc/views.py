from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.template import engines
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
from django.template.loader import render_to_string
from Database.models import Connection
import os

from .lib.controller import Controller
from .lib.sql import InadimplenciaSqls
from .objects import Inadimplencia
from .forms import ContratoHonorarioForm

class ContratoHonorarioView(View):
    template = "./geradoc/contrato_honorario/request_contrato_honorario.html"
    template_contrato = "./geradoc/contrato_honorario/contrato.html"
    template_contrato_condominio = "./geradoc/contrato_honorario/contrato_cond.html"
    template_planilha = "./geradoc/contrato_honorario/planilha.html"
    template_termo_aditivo = "./geradoc/contrato_honorario/termo_aditivo.html"

    form_class = ContratoHonorarioForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            # form.clean_log(request.user.username)
            try:
                controller = Controller()
                context = controller.get_dados_honorario(**form.cleaned_data)
                context.update(form.cleaned_data)
                context['data_inicio_contrato'] = context['data_inicio_contrato'].strftime('%d/%m/%Y')
                
                contrato_pdf = self.get_pdf_contrato(request, context) if form.cleaned_data['opcoes'] == 'empresa' else self.get_pdf_contrato_condominio(request, context)

                pathContrato = str( settings.BASE_DIR / 'temp/files/financeiro/contrato_honorario_{0}.pdf'.format(request.session.session_key) )

                file = open(pathContrato, 'wb')
                file.write(contrato_pdf)
                file.close()

                response = self.get_merged_file(request, pathContrato)

                return response
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
        return render(request, self.template, {'form': form})

    def get_merged_file(self,request, pathContrato):
        file = open(pathContrato, 'rb')
        response = HttpResponse(file, content_type="application/pdf")
        response['Content-Disposition'] = 'filename="%s"' % 'honorario.pdf'
        os.remove(pathContrato)
        return response

    def get_pdf_contrato(self, request, context):
        html_string = render_to_string(self.template_contrato, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        return pdf

    def get_pdf_contrato_condominio(self, request, context):
        html_string = render_to_string(self.template_contrato_condominio, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        return pdf

class InadimplentesView(View):
    template_name = "./geradoc/inadimplentes/inadimplentes.html"
    template_form = "./geradoc/inadimplentes/form.html"

    def get(self, request):
        return render(request, self.template_form, {})

    def post(self, request):
        try:
            connection = Connection().default_connect()
            params = [{
                'name': 'inadimplentes',
                'query': InadimplenciaSqls().get_inadimplentes(),
                'many': True
            }]
            dados = connection.run_query(params)
            context = {
                'inadimplencia': Inadimplencia.instance_from_database_args(dados['inadimplentes'])
            }

            pdf = self.get_pdf(request, self.template_name, context)
            response = self.get_file_response(pdf, "inadimplentes.pdf")
            return response
        except Exception as err:
            print(err)
            raise Exception(err)
        finally:
            connection.disconnect()
    
    def _get_string_as_template(self, string, context={}):
        template = engines['django'].from_string(string)
        return template.render(context=context)

    def get_pdf(self, request, template, context={}):
        html_string = render_to_string(template, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        return pdf

    def get_file_response(self, file, filename):
        response = HttpResponse(file)
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = 'filename="{0}.pdf"'.format(filename)
        return response
