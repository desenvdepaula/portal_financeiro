from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.template import engines
from django.http import HttpResponse
from weasyprint import HTML
from django.conf import settings
from django.template.loader import render_to_string
from Database.models import PostgreSQLConnection
from datetime import date
import os
import pandas as pd
from io import BytesIO

from core.views import PDFFileView
from .lib.controller import Controller
from .lib.sql import InadimplenciaSqls
from .objects import InadimplenciaObj
from .models import Inadimplencia
from .forms import ContratoHonorarioForm

class ContratoHonorarioView(PDFFileView):
    template = "./geradoc/contrato_honorario/request_contrato_honorario.html"
    template_contrato = "./geradoc/contrato_honorario/contrato.html"
    template_contrato_condominio = "./geradoc/contrato_honorario/contrato_cond.html"
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
                contrato_pdf = self.get_pdf_file(request, self.template_contrato, context) if form.cleaned_data['opcoes'] == 'empresa' else self.get_pdf_file(request, self.template_contrato_condominio, context)
                
                return self.get_file_response(contrato_pdf, f"Contrato Honorário - {form.cleaned_data.get('codigo_empresa')}")
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
        return render(request, self.template, {'form': form})

class InadimplentesView(View):
    template_form = "./geradoc/inadimplentes/form.html"

    def get(self, request):
        context = {}
        data = date.today()
        context['inadimplencias'] = Inadimplencia.objects.all()
        
        for inadimplencia in context['inadimplencias']:
            percentual = inadimplencia.percent_inadimplente
            inadimplencia.competencia = inadimplencia.competencia.strftime("%m/%Y")
            inadimplencia.percent_inadimplente = str(inadimplencia.percent_inadimplente)[0:4]
            if inadimplencia.ativo:
                month,year = inadimplencia.competencia.split('/')
                month,year = int(month),int(year)
                old = Inadimplencia.objects.raw(f'select * from geradoc_inadimplencia WHERE MONTH(competencia) = {month-1 if not month == 1 else 12} and YEAR(competencia) = {year if not month == 1 else year-1} and ativo = true LIMIT 1')
                for i in old:
                    if i.percent_inadimplente < percentual:
                        inadimplencia.maior = True
                    else:
                        inadimplencia.menor = True
                        
                
        context['existsInadimplencia'] = Inadimplencia.objects.filter(data_elaboracao__year=data.year, data_elaboracao__month=data.month).count() > 0
        return render(request, self.template_form, context)

    def post(self, request):
        connection = PostgreSQLConnection().default_connect()
        try:
            data = date.today()
            params = [{
                'name': 'inadimplentes',
                'query': InadimplenciaSqls().get_inadimplentes(),
                'many': True
            }]
            dados = connection.run_query(params)
            inadimplencia = InadimplenciaObj.instance_from_database_args(dados['inadimplentes'])
            old_inadimplencia = Inadimplencia.objects.filter(data_elaboracao__year=data.year, data_elaboracao__month=data.month, ativo=True)
            if len(old_inadimplencia) > 0:
                old_inadimplencia = old_inadimplencia.first()
                old_inadimplencia.ativo = False
                old_inadimplencia.save()
            
            Inadimplencia.objects.create(
                competencia = inadimplencia.data,
                vl_pagas_mes_seguinte = inadimplencia._recebido_apos_prazo,
                vl_notas_aberto = inadimplencia._aberto,
                vl_faturado_mes_anterior = inadimplencia._faturado,
                vl_inadimplente = inadimplencia._inadimplencia,
                dt_nota_fiscal1 = inadimplencia._data1,
                dt_nota_fiscal2 = inadimplencia._data2,
                percent_inadimplente = inadimplencia._indice,
                observacoes = request.POST.get('observacoes') if 'observacoes' in request.POST else '',
            )
            return redirect('inadimplentes')
        except Exception as err:
            raise Exception(err)
        finally:
            connection.disconnect()
            
    def export_relatorio_inadimplentes_abertos_detalhados(request):
        connection = PostgreSQLConnection().default_connect()
        connection.connect()
        try:
            with BytesIO() as b:
                data = request.POST.get('data')
                sqls = InadimplenciaSqls()
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                pd.set_option('max_colwidth', None)
                workbook = writer.book
                alignCenter = workbook.add_format({'align': 'left'})
                num = workbook.add_format({'num_format':'#,##0.00', 'align': 'left'})
                        
                dados = connection.run_query_for_select(sqls.get_detalhamento(data))
                if not dados:
                    raise Exception("Nenhum dado encontrado na Data Passada !!")
                print(dados)
                dados_for_df = [ i for i in dados ]
                total = sum([d[0] for d in dados_for_df])
                dados_for_df.append((total, '', '', '', '','TOTAL DAS NOTAS'))
                df = pd.DataFrame(dados_for_df, columns=['VALORCR', 'CODIGOESCRIT', "CODIGOCLIENTE",'NUMERONS', "STATUS", "DATA"])
                df.to_excel(writer, sheet_name='Detalhamento de Notas', index = False)
                writer.sheets['Detalhamento de Notas'].set_column('A:A', 20, num)
                writer.sheets['Detalhamento de Notas'].set_column('B:E', 25, alignCenter)
                writer.sheets['Detalhamento de Notas'].set_column('F:F', 20, alignCenter)
                
                writer.close()
                
                filename = f'Detalhamentos_{data}.xlsx'
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % filename
                return response
        except Exception as err:
            messages.error(request, "Ocorreu um erro: {0}".format(err))
            return redirect('inadimplentes')
        finally:
            connection.disconnect()
    
    def export_relatorio_inadimplentes(request):
        try:
            template_name = "./geradoc/inadimplentes/inadimplentes.html"
            context = {}
            competencia = request.POST.get('compet').split("/")
            context['inadimplencia'] = Inadimplencia.objects.filter(competencia__month=int(competencia[0]), competencia__year=int(competencia[1]), ativo=True).first()
            context['inadimplencia'].percent_inadimplente = str(context['inadimplencia'].percent_inadimplente)[0:4]
            html_string = render_to_string(template_name, context)
            html = HTML(string=html_string, base_url=request.build_absolute_uri())
            pdf = html.write_pdf()
            response = HttpResponse(pdf, content_type="application/pdf")
            response['Content-Disposition'] = 'attachment; filename="inadimplentes.pdf"'
            return response
        except Exception as err:
            raise Exception(err)