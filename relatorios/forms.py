from django import forms
from core.views import request_project_log
from datetime import date, datetime
from calendar import monthrange
from ordem_servico.models import Servico, DepartamentosControle

class RelatorioFaturamentoServicoForm:
    
    def __init__(self, kwargs):
        self.data_inicio = datetime.strptime(kwargs.get('data_inicio'), '%Y-%m-%d').date()
        self.data_fim = datetime.strptime(kwargs.get('data_fim'), '%Y-%m-%d').date()
        self.classificacoes = kwargs.getlist('classificacoes')
        self.servicos = kwargs.getlist('servicos')
        self.departamentos = kwargs.getlist('departamentos')
    
    def valid_departamentos(self):
        try:
            results = set()
            for depart in DepartamentosControle.objects.filter(id__in=self.departamentos):
                for service in depart.departamentos.all():
                    results.add(int(service.cd_servico))
        except Exception as err:
            raise Exception(err)
        else:
            return list(results)

    def valid_datas(self):
        try:
            if self.data_inicio > self.data_fim:
                raise Exception("Datas Desajustadas !!")
            last_day_month = monthrange(self.data_fim.year, self.data_fim.month)[1]
            data_ini = date(self.data_inicio.year, self.data_inicio.month, 1)
            data_fim = date(self.data_fim.year, self.data_fim.month, last_day_month)
        except Exception as err:
            raise Exception(err)
        else:
            return [data_ini, data_fim]
    
    def valid_classificacoes(self):
        try:
            classificacoes = [int(element) for element in self.classificacoes]
            datas = Servico.objects.filter(tipo_servico__in=classificacoes)
            codigos = [int(servico.cd_servico) for servico in datas ]
        except Exception as err:
            raise Exception(err)
        else:
            return codigos
    
    def valid_servicos(self):
        try:
            servicos = [int(servico) for servico in self.servicos]
        except Exception as err:
            raise Exception(err)
        else:
            return servicos