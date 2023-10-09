from datetime import date

from decimal import Decimal

class Empresa:
    def __init__(self, *args, **kwargs):
        self.codigo = kwargs['codigo_empresa']
        self.nome_empresa = kwargs['nome_empresa']
        self.inscricao_federal = kwargs['inscricao_federal']
        self.ddd = kwargs.get('ddd')
        self.numero_telefone = kwargs.get('numero_telefone')
        self.endereco = EnderecoEstab(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_empresa} - {self.inscricao_federal}"

    @staticmethod
    def instance_from_database_args(dbData, endereco=True):
        if endereco == True:
            empresa = Empresa(
                codigo_empresa = dbData['CODIGOEMPRESA'],
                nome_empresa = dbData['NOMEESTAB'],
                inscricao_federal = dbData['INSCRFEDERAL'],
                ddd = dbData.get('INSCRFEDERAL'),
                numero_telefone = dbData.get('NUMEROFONE'),
                logradouro = dbData['ENDERECOESTAB'],
                tipo_logradouro = dbData['SIGLA'],
                numero = dbData['NUMENDERESTAB'],
                complemento = dbData['COMPLENDERESTAB'],
                bairro = dbData['BAIRROENDERESTAB'],
                cidade = dbData['NOMEMUNIC'],
                uf = dbData['SIGLAESTADO'],
                cep = dbData['CEPENDERESTAB']
            )
        else:
            empresa = Empresa(
                codigo_empresa = dbData['CODIGOEMPRESA'],
                nome_empresa = dbData['NOMEESTAB'],
                inscricao_federal = dbData['INSCRFEDERAL'],
                ddd = dbData.get('INSCRFEDERAL'),
                numero_telefone = dbData.get('NUMEROFONE'),
            )
        return empresa

class EnderecoEstab:
    def __init__(self, *args, **kwargs):
        self.logradouro = kwargs['logradouro']
        self.tipo_logradouro = kwargs['tipo_logradouro']
        self.numero = kwargs['numero']
        self.complemento = kwargs['complemento']
        self.bairro = kwargs['bairro']
        self.cidade = kwargs['cidade']
        self.uf = kwargs['uf']
        self.cep = kwargs['cep']

    @staticmethod
    def instance_from_database_args(dbData):
        endereco = EnderecoEstab(
            logradouro = dbData['ENDERECOESTAB'],
            tipo_logradouro = dbData['SIGLA'],
            numero = dbData['NUMENDERESTAB'],
            complemento = dbData['COMPLENDERESTAB'],
            bairro = dbData['BAIRROENDERESTAB'],
            cidade = dbData['NOMEMUNIC'],
            uf = dbData['SIGLAESTADO'],
            cep = dbData['CEPENDERESTAB']
        )

class Socio:
    def __init__(self, socio_administrador=False, *args, **kwargs):
        self.codigo_empresa = kwargs['codigo_empresa']
        self.nome = kwargs['nome']
        self.inscricao_federal = kwargs['inscricao_federal']
        self.cargo = kwargs['cargo']
        self.socio_administrador = socio_administrador

        if socio_administrador:
            self.rg = kwargs['rg']
            self.estado_rg = kwargs['estado_rg']
            self.orgao_emissor = kwargs['orgao_emissor']

            self.estado_civil = kwargs['estado_civil']
            self.regime_casamento = kwargs['regime_casamento']
            self.maior_idade = kwargs['maior_idade']
            self.nacionalidade = kwargs['nacionalidade']
            self.data_nascimento = kwargs['data_nascimento']
            self.endereco = EnderecoSocio(*args, **kwargs)

    @staticmethod
    def instance_from_database_args(dbData, socio_administrador=False):
        kwargs = {
            'codigo_empresa': dbData['CODIGOEMPRESA'],
            'nome': dbData['NOMESOCIO'],
            'inscricao_federal': dbData['INSCRFEDERAL'],
            'cargo': dbData['DESCRCARGO'],
            'socio_administrador': socio_administrador,
        }
        if socio_administrador:
            extra_kwargs = {
                'logradouro': dbData['ENDERECOSOCIO'],
                'tipo_logradouro': dbData['SIGLA'],
                'numero': dbData['NUMENDERSOCIO'],
                'complemento': dbData['COMPLENDERSOCIO'],
                'bairro': dbData['BAIRROENDERSOCIO'],
                'cidade': dbData['NOMEMUNIC'],
                'cep': dbData['CEPENDERSOCIO'],
                'uf': dbData['SIGLAESTADO'],
                'estado': dbData['NOMEESTADO'],
                'rg': dbData.get('NUMERORG'),

                'estado_rg': dbData.get('SIGLAESTADORG'),
                'orgao_emissor': dbData.get('SIGLAORGAOEMISSOR'),

                'estado_civil': dbData.get('ESTADOCIVIL'),
                'regime_casamento': dbData.get('REGIMECASAMENTO'),
                'maior_idade': dbData.get('MAIORMENORIDADE'),
                'nacionalidade': dbData.get('NACIONALIDADE'),
                'data_nascimento': dbData.get('DATANASC'),
            }
            kwargs.update(extra_kwargs)
        socio = Socio(**kwargs)
        return socio

class EnderecoSocio:
    def __init__(self, *args, **kwargs):
        self.logradouro = kwargs['logradouro']
        self.tipo_logradouro = kwargs['tipo_logradouro']
        self.numero = kwargs['numero']
        self.complemento = kwargs['complemento']
        self.bairro = kwargs['bairro']
        self.cidade = kwargs['cidade']
        self.cep = kwargs['cep']
        self.uf = kwargs['uf']
        self.estado = kwargs['estado']

    @staticmethod
    def instance_from_database_args(dbData):
        kwargs = {
            'logradouro': dbData['ENDERECOSOCIO'],
            'tipo_logradouro': dbData['SIGLA'],
            'numero': dbData['NUMENDERSOCIO'],
            'complemento': dbData['COMPLENDERSOCIO'],
            'bairro': dbData['BAIRROENDERSOCIO'],
            'cidade': dbData['NOMEMUNIC'],
            'cep': dbData['CEPENDERSOCIO'],
            'uf': dbData['SIGLAESTADO'],
            'estado': dbData['NOMEESTADO'],
            'rg': dbData.get('NUMERORG'),
        }
        endereco = EnderecoSocio(kwargs)
        return endereco