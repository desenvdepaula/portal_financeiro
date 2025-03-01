from datetime import date
import csv
from django.http import HttpResponse
from .database import Manager
from .models import Empresa, Socio

class Controller():

    def __init__(self, *args, **kwargs):
        self.inicio_periodo = date(2020, 1, 31)
        self.manager = Manager(*args, **kwargs).default_connect()
        self.dados = {}
        self.response = HttpResponse(content_type='text/csv')
        self.writer = csv.writer(self.response)
        
    # ---------- RECUPERAÇÃO DE DADOS BRUTOS ---------- #
    def get_dados_empresa(self, codigo_empresa, codigo_estabelecimento=1):
        self.manager.connect()
        try:
            empresa = Empresa.instance_from_database_args(self.manager.fetchmap(self.manager.get_empresa(codigo_empresa, codigo_estabelecimento), True, True))    
            if not empresa:
                raise Exception("A empresa não foi encontrada")
        except Exception as err:
            raise Exception(err)
        else:
            return empresa
        finally:
            self.manager.disconnect()

    def get_dados_socio_administrador(self, codigo_empresa):
        self.manager.connect()
        try:
            socio = self.manager.fetchmap(self.manager.get_socio_administrador(codigo_empresa), True, True) 
            if not socio:
                raise Exception("O sócio administrador não foi encontrado")
            return Socio.instance_from_database_args(socio, True)
        except Exception as err:
            raise Exception(err)
        finally:
            self.manager.disconnect()

    def get_socios(self, codigo_empresa):
        self.manager.connect()
        try:
            socios = self.manager.fetchmap(self.manager.get_socios(codigo_empresa), upperCase=True)
            socios = [ Socio.instance_from_database_args(socio) for socio in socios ]
        except Exception as err:
            raise Exception(err)
        else:
            return socios
        finally:
            self.manager.disconnect()
    
    # ---------- OPERAÇÕES PRINCIPAIS ---------- #

    def get_dados_honorario(self, *args, **kwargs):
        empresa = self.get_dados_empresa(kwargs['codigo_empresa'], kwargs.get('codigo_estab', 1))
        socio_administrador = self.get_dados_socio_administrador(kwargs['codigo_empresa'])
        context = {
            'empresa': empresa,
            'socio_administrador': socio_administrador
        }
        return context
