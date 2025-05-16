from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.template import engines
from django.http import HttpResponse
from weasyprint import HTML # type: ignore
from django.conf import settings
from django.template.loader import render_to_string
from Database.models import PostgreSQLConnection
from Database.db_tables import TBL_ESTAB, TBL_SOCIO
from Database.objects import Socio, Empresa
from datetime import date
import os
import pandas as pd
from io import BytesIO

from core.views import PDFFileView
from .lib.controller import Controller
from .lib.sql import InadimplenciaSqls
from .objects import InadimplenciaObj
from .models import Inadimplencia
from .forms import ContratoHonorarioForm, DistratoForm
import locale
import re
import numero_por_extenso # type: ignore

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
        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
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
        
class DistratoView(View):
    template = "./geradoc/distrato/form.html"
    distrato = "./geradoc/distrato/distrato.html"
    form_class = DistratoForm

    def get(self, request):
        context = {
            'form': self.form_class()
        }
        return render(request, self.template, context)

    def post(self, request):
        context = {
            'form': self.form_class(request.POST or None)
        }
        if context['form'].is_valid():
            connection = PostgreSQLConnection().default_connect()
            try:
                context['form'].clean_log(request.user.username)
                context['boletos'] = self._get_boletos_from_POST(request.POST)
                params = [
                    {
                        'name': 'socio',
                        'query': TBL_SOCIO().get_socio_administrador(context['form'].cleaned_data['codigo_empresa']),
                        'many': False
                    },
                    {
                        'name': 'empresa',
                        'query': TBL_ESTAB().get_estabelecimento( 
                            context['form'].cleaned_data['codigo_empresa'], 
                            context['form'].cleaned_data['codigo_estab'] 
                        ),
                        'many': False
                    }
                ]
                resp = connection.run_query(params)
                context['socio_administrador'] = Socio.instance_from_db_data(resp['socio'], True)
                context['empresa'] = Empresa.instance_from_database_args(resp['empresa'])
                context.update(context['form'].cleaned_data)
                context['nr_obrigacoes'] = len(context['form'].cleaned_data['obrigacoes_anuais'])
                context['nr_obrigacoes_sub'] = context['nr_obrigacoes'] - 1
                singular = True if context['nr_obrigacoes'] == 1 else False

                _clausulas = self._get_clausulas(singular, True if context['boletos'] else False)
                _clausulas = [ self._get_string_as_template(clausula, context) for clausula in _clausulas ]
                context['clausulas'] = _clausulas
                
                pdf = self.get_pdf(request, self.distrato, context)
                response = self.get_file_response(pdf, f"Distrato {context['codigo_empresa']} - {context['codigo_estab']}")
                return response
            except Exception as ex:
                messages.error(request, "Ocorreu um erro ao executar esta operação: {0}".format(ex))
            finally:
                connection.disconnect()

        return render(request, self.template, context)

    def _get_clausulas(self, singular=True, boletos=False):
        clausulas = [
            """
            As partes, de comum acordo, dão por rescindido o instrumento particular 
            “Contrato de Prestação de Serviços Profissionais de Contabilidade”. 
            """,
            """
            A <strong>CONTRATANTE</strong> se compromete, com o presente distrato, a contratar 
            novo profissional para prestar serviços de contabilidade, sendo dever do novo prestador assumir a responsabilidade 
            técnica a partir de {{ data_novo_contador|date:"d" }} ({{diaDataNovoContador}}) de 
            {{ data_novo_contador|date:"F" }} de {{ data_novo_contador|date:"Y"}} ({{anoDataNovoContador}}).
            """,
            """
            A <strong>CONTRATANTE</strong> reconhece que a <strong>CONTRATADA</strong> executou todos os serviços 
            devidos até a competência de {{ data_competencia|date:"d" }} ({{diaDatacompetencia}}) de 
            {{ data_competencia|date:"F" }} de {{ data_competencia|date:"Y"}} ({{anoDatacompetencia}}). 
            """,
            """
            Fica acertado entre as partes que, em razão dos serviços e atividades desenvolvidos até o momento, 
            a <strong>CONTRATADA</strong> entregará à <strong>CONTRATANTE</strong>, todos os arquivos necessários a continuidade dos serviços, tão logo todos serviços sejam concluídos, bem como toda a documentação, livros e arquivos magnéticos das obrigações fiscais entregues ao Fisco, devidamente protocolados.<br>
            <strong>PARÁGRAFO PRIMEIRO:</strong> A entrega da documentação será feita somente após a assinatura do presente instrumento por ambas as partes. <br>
            <strong>PARÁGRAFO SEGUNDO:</strong> As obrigações acessórias, como {{ obrigacoes_anuais.0 }} referentes ano-base {{ano_competencia}} ({{anoCompetencia}}), 
            são de responsabilidade da <strong>CONTRATADA</strong> e já foram ou serão entregues dentro do prazo legal estabelecido.<br>
            <strong>PARÁGRAFO TERCEIRO:</strong> A fim de que a <strong>CONTRATADA</strong> possa satisfazer o compromisso de entregar as obrigações acessórias, 
            a <strong>CONTRATANTE</strong> compromete-se a manter atualizada sua certificação digital e a conservar válidas as procurações 
            eletrônicas substabelecidas à <strong>CONTRATADA</strong> até a execução dos serviços. Além disso, a <strong>CONTRATANTE</strong> garante manter o acesso, através de senhas, 
            ao posto fiscal, prefeitura municipal, conectividade social da Caixa Econômica Federal, 
            FAP (fator acidentário de prevenção) e os demais acessos a órgãos fiscalizadores, até a conclusão dos serviços do período sob a responsabilidade da <strong>CONTRATADA</strong>.
            As providências mencionadas se fazem indispensáveis à entrega das obrigações acessórias e, 
            diante de impedimentos causados pela <strong>CONTRATANTE</strong>, 
            a <strong>CONTRATADA</strong> fica desobrigada de responsabilidade ou encargo decorrente de autuações, 
            multas ou comprometimento fiscal da <strong>CONTRATANTE</strong>.
            """ if singular else """
            Fica acertado entre as partes que, em razão dos serviços e atividades desenvolvidos até o momento, 
            a <strong>CONTRATADA</strong> entregará à <strong>CONTRATANTE</strong>, todos os arquivos necessários a continuidade dos serviços, tão logo todos serviços sejam concluídos, bem como toda a documentação, livros e arquivos magnéticos das obrigações fiscais entregues ao Fisco, devidamente protocolados.<br>
            <strong>PARÁGRAFO PRIMEIRO:</strong> A entrega da documentação será feita somente após a assinatura do presente instrumento por ambas as partes. <br>
            <strong>PARÁGRAFO SEGUNDO:</strong> As obrigações acessórias, como 
            {% for obrigacao in obrigacoes_anuais %}
                {% if forloop.counter == nr_obrigacoes %}
                    {{ obrigacao }}
                {% elif forloop.counter == nr_obrigacoes_sub %}
                    {{ obrigacao }} e
                {% else %}
                    {{ obrigacao }},  
                {% endif %}    
            {% endfor %}
            referentes ano-base {{ano_competencia}} ({{anoCompetencia}}), 
            são de responsabilidade da <strong>CONTRATADA</strong> e já foram ou serão entregues dentro do prazo legal estabelecido.<br>
            <strong>PARÁGRAFO TERCEIRO:</strong> A fim de que a <strong>CONTRATADA</strong> possa satisfazer o compromisso de entregar as obrigações acessórias, 
            a <strong>CONTRATANTE</strong> compromete-se a manter atualizada sua certificação digital e a conservar válidas as procurações 
            eletrônicas substabelecidas à <strong>CONTRATADA</strong> até a execução dos serviços. Além disso, a <strong>CONTRATANTE</strong> garante manter o acesso, através de senhas, 
            ao posto fiscal, prefeitura municipal, conectividade social da Caixa Econômica Federal, 
            FAP (fator acidentário de prevenção) e os demais acessos a órgãos fiscalizadores, até a conclusão dos serviços do período sob a responsabilidade da <strong>CONTRATADA</strong>.
            As providências mencionadas se fazem indispensáveis à entrega das obrigações acessórias e, 
            diante de impedimentos causados pela <strong>CONTRATANTE</strong>, 
            a <strong>CONTRATADA</strong> fica desobrigada de responsabilidade ou encargo decorrente de autuações, 
            multas ou comprometimento fiscal da <strong>CONTRATANTE</strong>.
            """,
            """
            Obriga-se a <strong>CONTRATANTE</strong> a desvincular a responsabilidade profissional e o nome da <strong>CONTRATADA</strong> 
            nos órgãos da administração pública 
            e suas repartições em até 30 (trinta) a partir do cumprimento das obrigações previstas na Cláusula Quarta ou, 
            caso já tenham sido satisfeitas as obrigações, em até 30 (trinta) dias da entrega de todos os serviços até a responsabilidade da <strong>CONTRATADA</strong>.<br>
            <strong>PARÁGRAFO PRIMEIRO:</strong> Após o cumprimento das obrigações da Cláusula Quarta pela <strong>CONTRATADA</strong>, 
            no caso de inércia da <strong>CONTRATANTE</strong>, pode aquela comunicar aos agentes da administração pública solicitando a 
            retirada de sua responsabilidade técnica.
            """,
            """
            <strong>CONTRATADA</strong> e <strong>CONTRATANTE</strong> declaram-se cientes dos direitos, 
            obrigações e penalidades previstas na Lei Geral de Proteção de Dados (LGPD) – Lei 13.709 de 2018 – 
            e assumem o compromisso de zelar pela proteção de dados pessoais e dados pessoais sensíveis em seu poder por meios técnicos e administrativos suficientes e, a todo momento, buscar meios efetivos de resguardar a segurança desses dados, conforme determina a LGPD.<br>
            <strong>PARÁGRAFO PRIMEIRO:</strong> Após a rescisão contratual, a <strong>CONTRATADA</strong> devolverá à <strong>CONTRATANTE</strong> 
            os dados pessoais e pessoais sensíveis os quais recebeu com finalidade de cumprir suas obrigações contratuais. 
            A <strong>CONTRATANTE</strong> fica ciente de que a <strong>CONTRATADA</strong> poderá guardar dados pessoais e informações 
            necessárias à comprovação da correta execução de seus serviços por obrigação legal e 
            prazo estabelecido na legislação brasileira vigente.<br>
            <strong>PARÁGRAFO SEGUNDO:</strong> A <strong>CONTRATANTE</strong> está ciente das obrigações da legislação brasileira vigente 
            para guarda de informações contábeis, trabalhistas, previdenciárias e fiscais, 
            as quais serão repassadas pela <strong>CONTRATADA</strong> no ato da rescisão, cabendo àquela o dever de guarda, respeitando os prazos de prescrição.<br>
            <strong>PARÁGRAFO TERCEIRO:</strong> A <strong>CONTRATADA</strong> transfere as informações e dados pessoais assumindo o 
            compromisso de ter tratados os dados em conformidade com as obrigações contratuais e legais, 
            visando sempre à boa-fé e aos melhores interesses da <strong>CONTRATANTE</strong>, 
            atendendo aos princípios gerais de proteção de dados pessoais e aos direitos dos titulares previstos na LGPD.<br>
            <strong>PARÁGRAFO QUARTO:</strong> A <strong>CONTRATANTE</strong> é responsável pela autenticidade e veracidade das informações e 
            dados repassados à <strong>CONTRATADA</strong> os quais foram utilizados na execução do contrato de prestação de 
            serviços que neste termo é rescindido.<br>
            <strong>PARÁGRAFO QUINTO:</strong> Caso ocorra algum incidente de segurança que possa acarretar risco ou dano relevante a 
            Titular de dados, <strong>CONTRATADA</strong> e <strong>CONTRATANTE</strong> deverão comunicar, em prazo razoável, 
            o Titular e a Autoridade Nacional de Proteção de Dados (ANPD), conforme artigo 48 da Lei nº 13.709/2018.
            """
        ]
        if boletos:
            clausulas = clausulas + [
                """
                Fica ciente a <strong>CONTRATANTE</strong> de que se encontra pendente de pagamento o(s) boleto(s):
                {% for boleto in boletos %}
                    <strong>N.° {{ boleto.nr }}</strong>, com vencimento em {{ boleto.data|date:"d" }} de {{ boleto.data|date:"F" }} de {{ boleto.data|date:"Y" }}, no valor total de R$ {{ boleto.valor }}; 
                {% endfor %}<br>
                <strong>PARÁGRAFO PRIMEIRO:</strong> A partir do presente, é responsabilidade da <strong>CONTRATANTE</strong> a encadernação e 
                registro dos livros diário e razão na junta comercial e guarda dos mesmos.
                """,
                """
                A falta de pagamento da obrigação acima mencionada, no prazo estabelecido no boleto, 
                faculta à <strong>CONTRATADA</strong> a imediata inclusão da <strong>CONTRATANTE</strong> em empresas de proteção ao crédito (SCPC, SPC e/ou SERASA) 
                podendo o título ser protestado junto ao Cartório de Protestos, independente de notificação judicial ou extrajudicial.<br>
                <strong>PARÁGRAFO PRIMEIRO:</strong> O valor devido sofrerá acréscimo de multa de 2% (dois por cento) e de 
                juros moratórios de 1% (um por cento) ao mês ou fração, além da correção monetária, até o efetivo pagamento.<br> 
                <strong>PARÁGRAFO SEGUNDO:</strong> A dívida escrita acima é assumida pelo devedor como líquida, certa e exigível, 
                conforme o disposto no artigo 783 e seguintes do Código de Processo Civil brasileiro, 
                tendo em vista o caráter executivo extrajudicial e ainda, no caso de cobrança judicial, 
                serão suportadas pelo devedor as custas processuais e honorários advocatícios na base de 20% 
                (vinte por cento) sobre o valor total do débito corrigido.
                """
            ]
        clausulas = clausulas + [
            """
            A <strong>CONTRATANTE</strong> declara que todos os serviços objeto da contratação foram prestados pela <strong>CONTRATADA</strong> de forma eficaz e satisfatória, 
            outorgando-a plena, total e irrevogável quitação, para nada mais reclamar, a qualquer tempo e a que título for, 
            em relação à avença distratada, bem como aos serviços profissionais prestados. 
            """,
            """
            O presente distrato é firmado em caráter irrevogável e irretratável, obrigando as partes, 
            seus herdeiros e sucessores.<br> 
            <strong>PARÁGRAFO ÚNICO:</strong> em caso de impasse, as partes submeterão a solução do conflito a 
            procedimento arbitral nos termos da lei n.º 9.307/1996. Ademais, não havendo consenso por meio da arbitragem, 
            é eleito o foro da comarca de Foz do Iguaçu, Paraná, para dirimir qualquer ação oriunda do presente distrato.
            """
        ]     
        return clausulas

    def _get_boletos_from_POST(self, post):
        # -- > nr_boleto_{int} : ^nr_boleto_[0-9]+$
        # -- > data_boleto_{int} : ^data_boleto_[0-9]+$
        # -- > valor_boleto_{int} : ^valor_boleto_[0-9]+$
        keys = post.keys()
        boletos = []
        for key in keys:
            match = re.search("nr_boleto_([0-9]+)", key)
            if match:
                str_data = post['data_boleto_{0}'.format(match.groups()[0])].split('-')
                boletos.append({
                    'nr': post['nr_boleto_{0}'.format(match.groups()[0])],
                    'data': date(int(str_data[0]), int(str_data[1]), int(str_data[2])),
                    'valor': post['valor_boleto_{0}'.format(match.groups()[0])].replace('.',',')
                })

        for boleto in boletos:
            for key in boleto.keys():
                if key == "valor":
                    valorExtenso = numero_por_extenso.monetario(str(boleto[key]))
                    boleto[key] = f"{boleto[key]} ({valorExtenso})"

        return boletos
        

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
        response['Content-Disposition'] = 'attachment; filename="{0}.pdf"'.format(filename)
        return response
