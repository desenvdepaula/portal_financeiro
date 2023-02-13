from datetime import date
import zipfile
import os
import re

from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from http import HTTPStatus
from django.shortcuts import render
from django.conf import settings
from django.views import View

# from weasyprint import HTML

@login_required
def home(request):
    context = {}
    template = "home.html"
    return render(request, template, context)

def erro404(request):
    template = "erro404.html"
    return render(request, template)


class HttpResponseNoContent(HttpResponse):
    status_code = HTTPStatus.NO_CONTENT


# class PDFFileView(View):

#     def create_file_zip_instance(self, request, filepath: str, filename: str):
#         """
#             Método que realiza e retorna a instância de um ZipFile em modo de escrita juntamente com seu caminho
#         """
#         zip_file = 'temp/files/{0}/{1}_{2}.zip'.format(filepath, filename, request.session.session_key)
#         path = str( settings.BASE_DIR / zip_file )
#         return zipfile.ZipFile(path, 'w'), path

#     def remove_file_zip_instance(self, path):
#         os.remove(path)

#     def get_file_zip_response(self, path, filename='documento'):
#         zip_file = open(path, 'rb')
#         response = HttpResponse(zip_file, content_type="application/zip")
#         response['Content-Disposition'] = 'filename="{0}.zip"'.format(filename)
#         return response


#     def get_zipped_file(self, request, filepath: str, filename: str, files: dict ):
#         zipfile_name = 'temp/files/{0}/{1}_{2}.zip'.format(filepath, filename, request.session.session_key)
#         path = str( settings.BASE_DIR / zipfile_name )
#         zip_file = zipfile.ZipFile(path, 'w')

#         for file in files:
#             zip_file.writestr(file['name'], file['file'])

#         zip_file = open(path, 'rb')
#         response = HttpResponse(zip_file, content_type="application/zip")
#         response['Content-Disposition'] = 'filename="{0}.zip"'.format(filename)
#         os.remove(path)
#         return response

#     def get_pdf_file(self, request, template, context):
#         html_string = render_to_string(template, context)
#         html = HTML(string=html_string, base_url=request.build_absolute_uri())
#         pdf = html.write_pdf()
#         return pdf

#     def get_file_response(self, file, filename="documento", filetype="pdf"):
#         response = HttpResponse(file, content_type="application/pdf")
#         response['Content-Disposition'] = 'filename="{0}.{1}"'.format(filename, filetype)
#         return response
