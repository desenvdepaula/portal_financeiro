from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views import View

from .forms import OrdemServicoForm, ServicoForm
from .lib.controller import Controller
from .models import OrdemServico, DepartamentosControle, Servico
from .lib.database import ManagerTareffa
from core.views import request_project_log
    
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
                
class ServicosView(View):
    
    template = "ordem_servico/servicos.html"
    form = ServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        controller = Controller()
        context['servicos_questor'] = controller.get_servicos_questor()
        context['departamentos'] = DepartamentosControle.objects.all()
        context['servicos'] = Servico.objects.all()
        return render(request, self.template, context)
    
    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            try:
                departments_request = request.POST.getlist('departamentos')
                departments = context['form'].clean_departamentos(departments_request)
                nr_service = context['form'].cleaned_data.get('nr_service')
                if not nr_service:
                    cd_servico, name_servico = context['form'].clean_service(request.POST.get('servico'))
                    servico = Servico.objects.create(
                        cd_servico = cd_servico,
                        name_servico = name_servico,
                        tipo_servico = context['form'].cleaned_data.get('tipo_servico'),
                        considera_custo = context['form'].cleaned_data.get('considera_custo'),
                        classificacao = context['form'].cleaned_data.get('classificacao'),
                        observacoes = context['form'].cleaned_data.get('obs'),
                    )
                    for depart in departments:
                        servico.departamentos.add(depart)
                else:
                    service = Servico.objects.get(cd_servico=nr_service)
                    service.tipo_servico = context['form'].cleaned_data.get('tipo_servico')
                    service.considera_custo = context['form'].cleaned_data.get('considera_custo')
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
    
class OrdemServicoView(View):
    
    template = "ordem_servico/index.html"
    form = OrdemServicoForm

    def get(self, request, *args, **kwargs):
        context = { 'form': self.form() }
        context['ordens'] = OrdemServico.objects.all()
        for ordem in context['ordens']:
            ordem.data_cobranca = ordem.data_cobranca.strftime('%d/%m/%Y')
            preco = float(ordem.valor)
            preco_convertido = f"R$ {preco:_.2f}"
            preco_final = preco_convertido.replace('.',',').replace('_','.')
            ordem.valor = preco_final
            
        return render(request, self.template, context)

    def post(self, request, *args, **kwargs):
        context = { 'form': self.form(request.POST or None) }
        if context['form'].is_valid():
            context['form'].clean_log(request.user.username)
            try:
                controller = Controller()
                if request.POST.get('id_ordem'):
                    return controller.update_ordem_servico(context['form'].cleaned_data, request.user.username)
                else:
                    controller.update_ordem_servico(context['form'].cleaned_data, request.user.username)
                    messages.success(request, "Cadastrado com sucesso")
                    return redirect('list_ordem_servico') 
            except Exception as ex:
                messages.error(request, f"Ocorreu um erro durante a operação: {ex}")
                raise Exception(ex)
        else:
            messages.error(request, "Ocorreu um erro no Formulário, Verifique Novamente")
            return redirect('list_ordem_servico') 
    
    def delete(request):
        try:
            ordem = OrdemServico.objects.get(id=int(request.POST.get('id_ordem')))
            controller = Controller()
            if ordem.ordem_debitada_id:
                controller.delete_ordem_servico_debitada(ordem)
            cd_empresa = ordem.cd_empresa
            text = f"Serviço: {ordem.servico}, Realizado: {ordem.data_realizado}, Executado: {ordem.executado}, Quantidade: {ordem.quantidade}, Valor: {ordem.valor}"
            ordem.delete()
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            request_project_log(cd_empresa, text, "ORDEM DE SERVIÇO / DELETAR ORDEM", request.user.username)
            return JsonResponse({'msg': 'correto'})
        
    def buscar_ordem_servico(request, id_ordem):
        try:
            ordem = OrdemServico.objects.get(id=id_ordem)
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
        
    def request_debitar_ordem_servico(request, id_ordem):
        try:
            controller = Controller()
            controller.debitar_or_delete_ordem_servico(id_ordem, request.GET.get('debitar') == 'True')
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)
            
    def request_arquivar_ordem_servico(request, id_ordem):
        try:
            controller = Controller()
            controller.debitar_or_delete_ordem_servico(id_ordem, False, arquivar=request.GET.get('arquivar') == 'True')
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=500)
        else:
            return JsonResponse({"msg": 'sucesso'}, status=200)

    def request_download_planilha(request):
        try:
            controller = Controller()
            return controller.gerarPlanilhasOrdens(request.POST)
        except Exception as err:
            messages.error(request, f"Ocorreu um erro: {err}, Verifique Novamente")
        return redirect('list_ordem_servico')