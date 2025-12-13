from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from http import HTTPStatus
from django.template.loader import render_to_string
from django.shortcuts import render
from django.conf import settings
from django.views import View

from datetime import datetime as dt
import zipfile
import os
import io
from weasyprint import HTML
from .models import LogPID

@login_required
def home(request):
    context = {}
    template = "home.html"
    return render(request, template, context)

def erro404(request):
    template = "erro404.html"
    return render(request, template)

def get_request_to_api_omie(escritorio, call, params):
    empresas = {
        '501': {'app_key': "829724170275", 'app_secret': "a1d06fbf0ae8801964e0d56346527aa9"},   # DE PAULA CONTADORES
        '502': {'app_key': "6645667020993", 'app_secret': "cb13871cfbbd6b401ceeb3a14abc4c50"},   # DE PAULA SOLUCOES CONTABEIS LTDA
        '505': {'app_key': "6646111687215", 'app_secret': "e54bf4e6e255a1a4a2c0a2dd844df485"},   # AR DE PAULA FOZ
        '567': {'app_key': "6646134687192", 'app_secret': "1a78910abf26b0a1787fb0d119a1cdb7"},   # DE PAULA SOLUCOES EMPRESARIAIS LTDA
        '575': {'app_key': "6646142353851", 'app_secret': "60ddd49e3c42214711cbe016ee8aae82"},   # DPC SOLUCOES LTDA
    }
    base_request = {
        "call": call,
        "app_key": empresas[escritorio]['app_key'],
        "app_secret": empresas[escritorio]['app_secret'], 
        "param": [
            params
        ]
    }
    return base_request

def request_project_log(cod_empresa, formData, aplication, username):
    # ---> Escrever na Tabela do Banco de Dados
    data_hoje = dt.now().strftime('%d/%m/%Y %H:%M:%S')
    formData = formData.replace("'", '') if formData else 'NULL'
    cod_empresa = cod_empresa if cod_empresa else '0'
    LogPID.objects.create(
        execucao=data_hoje,
        cd_empresa=cod_empresa,
        descricao=formData,
        aplication=aplication,
        usuario=username
    )

class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


class PDFFileView(View):

    def create_file_zip_instance(self, request, filepath: str, filename: str):
        """
            Método que realiza e retorna a instância de um ZipFile em modo de escrita juntamente com seu caminho
        """
        zip_file = 'temp/files/{0}/{1}_{2}.zip'.format(filepath, filename, request.session.session_key)
        path = str( settings.BASE_DIR / zip_file )
        return zipfile.ZipFile(path, 'w'), path

    def remove_file_zip_instance(self, path):
        os.remove(path)

    def get_file_zip_response(self, path, filename='documento'):
        zip_file = open(path, 'rb')
        response = HttpResponse(zip_file, content_type="application/zip")
        response['Content-Disposition'] = 'filename="{0}.zip"'.format(filename)
        return response


    def get_zipped_file(self, request, filepath: str, filename: str, files: dict ):
        zipfile_name = 'temp/files/{0}/{1}_{2}.zip'.format(filepath, filename, request.session.session_key)
        path = str( settings.BASE_DIR / zipfile_name )
        zip_file = zipfile.ZipFile(path, 'w')

        for file in files:
            zip_file.writestr(file['name'], file['file'])

        zip_file = open(path, 'rb')
        response = HttpResponse(zip_file, content_type="application/zip")
        response['Content-Disposition'] = 'filename="{0}.zip"'.format(filename)
        os.remove(path)
        return response

    def get_pdf_file(self, request, template, context):
        html_string = render_to_string(template, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        return pdf

    def get_file_response(self, file, filename="documento", filetype="pdf"):
        response = HttpResponse(file, content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="{0}.{1}"'.format(filename, filetype)
        return response

    def prepare_zip_file_content(self, dict_data_contains):
        """returns Zip bytes ready to be saved with 
        open('C:/1.zip', 'wb') as f: f.write(bytes)
        @dict_data_contains dict like {'1.txt': 'string', '2.txt": b'bytes'} 
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for file_name, file_data in dict_data_contains.items():
                zip_file.writestr(file_name, file_data)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()