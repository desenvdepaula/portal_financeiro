
from decimal import Decimal

from .utils import numeric_to_string


class Pessoa:

    def __init__(self, pessoa=None, *args, **kwargs):
        if pessoa:
            kwargs.update(pessoa.__dict__)
        self.nome = kwargs.get('nome')
        self.cpf = kwargs.get('cpf')
        self.ddd_telefone = kwargs.get('ddd_telefone')
        self.nr_telefone = kwargs.get('nr_telefone')

    def __repr__(self):
        return f"Pessoa(nome={self.nome}, cpf={self.cpf})"

    @staticmethod
    def instance_from_db_data(db_args):
        kwargs = {
            'nome': db_args.get('NOMEFUNC'),
            'cpf': db_args.get('CPFFUNC'),
            'ddd_telefone': db_args.get('DDDFONE'),
            'nr_telefone': db_args.get('NUMEROFONE')
        }
        return Pessoa(**kwargs)
 
class Endereco:

    def __init__(self, endereco=None, *args, **kwargs):
        if endereco:
            kwargs.update(endereco.__dict__)
        self.uf = kwargs.get('uf')
        self.municipio = kwargs.get('municipio')
        self.cep = kwargs.get('cep')
        self.bairro = kwargs.get('bairro')
        self.rua = kwargs.get('rua')
        self.numero = kwargs.get('numero')
        self.complemento = kwargs.get('complemento')

    def __repr__(self):
        repr_str = f"""
            Endereco(uf={self.uf}, municipio={self.municipio}, cep={self.cep}, bairro={self.bairro}, rua={self.rua}, numero={self.numero}, complemento={self.complemento})
        """
        return repr_str

    @staticmethod
    def instance_from_db_data(db_args):
        kwargs = {
            'uf': db_args.get('SIGLAESTADO'),
            'municipio': db_args.get('NOMEMUNIC'),
            'cep': db_args.get('CEPFUNC'),
            'bairro': db_args.get('BAIRROFUNC'),
            'rua': db_args.get('ENDERFUNC'),
            'numero': db_args.get('NUMEROENDER'),
            'complemento': db_args.get('COMPLENDER')
        }
        return Endereco(**kwargs)
  
class ContaBancaria:

    def __init__(self, conta_bancaria=None, *args, **kwargs):
        if conta_bancaria:
            kwargs.update(conta_bancaria.__dict__)
        self.codigo = kwargs.get('codigo')
        self.nome_banco = kwargs.get('nome_banco')
        self.agencia = kwargs.get('agencia')
        self.conta = kwargs.get('conta')
        self.digito_conta = kwargs.get('digito_conta')

    def __repr__(self):
        return f"ContaBancaria(codigo={self.codigo}, nome_banco={self.nome_banco}, agencia={self.agencia}, conta={self.conta}, digito_conta={self.digito_conta})"

    @staticmethod
    def instance_from_db_data(db_args):
        kwargs = {
            'codigo': db_args.get('CODIGOBANCO'),
            'nome_banco': db_args.get('NOMEBANCO'),
            'agencia': db_args.get('NUMEROAGENCIA'),
            'conta': db_args.get('NUMEROCONTA'),
            'digito_conta': db_args.get('DIGITOCONTA')
        }
        print(kwargs)
        return ContaBancaria(**kwargs)

class Funcionario:

    def __init__(self, *args, **kwargs):
        self.codigo_contrato = kwargs.get('codigo_contrato')
        self.carteira_profissional = kwargs.get('carteira_profissional')
        self.pessoa = Pessoa(**kwargs)
        self.conta_bancaria = ContaBancaria(**kwargs)
        self.endereco = Endereco(**kwargs)

    def __repr__(self):
        return f"Funcionario({self.codigo_contrato}, {self.carteira_profissional}, {self.pessoa}, {self.conta_bancaria}, {self.endereco})"

    @staticmethod
    def instance_from_db_data(db_args, dependencies=False):
        kwargs = {
            'codigo_contrato': db_args.get('CODIGOFUNCCONTR'),
            'carteira_profissional': db_args.get('CARTEIRAPROFISSIONAL')
        }
        if dependencies:
            kwargs.update(Pessoa.instance_from_db_data(db_args).__dict__)
            kwargs.update(ContaBancaria.instance_from_db_data(db_args).__dict__)
            kwargs.update(Endereco.instance_from_db_data(db_args).__dict__)
        return Funcionario(**kwargs)

class Socio:

    def __init__(self, *args, **kwargs):
        self.codigo_empresa = kwargs.get('codigo_empresa')
        self.nome = kwargs.get('nome')
        self.inscricao_federal = kwargs.get('inscricao_federal')
        self.numero_rg = kwargs.get('numero_rg')
        self.uf_rg = kwargs.get('uf_rg')
        self.data_nascimento = kwargs.get('data_nascimento')
        self.estado_civil = kwargs.get('estado_civil')
        self.regime_casamento = kwargs.get('regime_casamento')
        self.descr_cargo = kwargs.get('descr_cargo')
        self.nacionalidade = kwargs.get('nacionalidade')
        self.orgao_emissor = kwargs.get('orgao_emissor')

        self.pessoa = Pessoa(**kwargs)
        self.endereco = EnderecoSocio(**kwargs)

    @staticmethod
    def instance_from_db_data(db_args, dependencies=False):
        kwargs = {
            'codigo_empresa': db_args.get('CODIGOEMPRESA'),
            'numero_rg': db_args.get('NUMERORG'),
            'uf_rg': db_args.get('SIGLAESTADORG'),
            'data_nascimento': db_args.get('DATANASC'),
            'estado_civil': db_args.get('ESTADOCIVIL'),
            'regime_casamento': db_args.get('REGIMECASAMENTO'),
            'descr_cargo': db_args.get('DESCRCARGO'),
            'nacionalidade': db_args.get('NACIONALIDADE'),
            'orgao_emissor': db_args.get('SIGLAORGAOEMISSOR'),
            'nome': db_args.get('NOMESOCIO'),
            'inscricao_federal': db_args.get('INSCRFEDERAL')
        }
        if dependencies:
            kwargs.update(EnderecoSocio.instance_from_db_data(db_args).__dict__)
        return Socio(**kwargs)

class EnderecoSocio:

    def __init__(self, endereco=None, *args, **kwargs):
        if endereco:
            kwargs.update(endereco.__dict__)
        self.uf = kwargs.get('uf')
        self.estado = kwargs.get('estado')
        self.municipio = kwargs.get('municipio')
        self.cep = kwargs.get('cep')
        self.bairro = kwargs.get('bairro')
        self.rua = kwargs.get('rua')
        self.numero = kwargs.get('numero')
        self.complemento = kwargs.get('complemento')
        self.sigla = kwargs.get('sigla')

    def __repr__(self):
        repr_str = f"""
            Endereco(sigla={self.sigla},uf={self.uf}, municipio={self.municipio}, cep={self.cep}, bairro={self.bairro}, rua={self.rua}, numero={self.numero}, complemento={self.complemento})
        """
        return repr_str

    @staticmethod
    def instance_from_db_data(db_args):
        kwargs = {
            'sigla': db_args.get('SIGLA'),
            'uf': db_args.get('SIGLAESTADO'),
            'estado': db_args.get('NOMEESTADO'),
            'municipio': db_args.get('NOMEMUNIC'),
            'cep': db_args.get('CEPENDERSOCIO'),
            'bairro': db_args.get('BAIRROENDERSOCIO'),
            'rua': db_args.get('ENDERECOSOCIO'),
            'numero': db_args.get('NUMENDERSOCIO'),
            'complemento': db_args.get('COMPLENDERSOCIO'),
        }
        return EnderecoSocio(**kwargs)

class Empresa:

    def __init__(self, *args, **kwargs):
        self.codigo_empresa = kwargs['codigo_empresa']
        self.nome = kwargs['nome']
        self.inscricao_federal = kwargs['inscricao_federal']
        
        self.uf = kwargs['uf']
        self.cidade = kwargs['cidade']
        self.cep = kwargs['cep']
        self.bairro = kwargs['bairro']
        self.rua = kwargs['rua']
        self.numero = kwargs['numero']
        self.complemento = kwargs['complemento']
        self.sigla = kwargs['sigla']
        
    def __str__(self):
        return f"{self.nome}"

    @staticmethod
    def instance_from_database_args(db_args):
        obj = Empresa(       
            codigo_empresa = db_args.get('CODIGOEMPRESA'),
            nome = db_args.get('NOMEESTAB'),
            inscricao_federal = db_args.get('INSCRFEDERAL'),
            codigo_estab = db_args.get('CODIGOESTAB'),

            cidade = db_args.get('NOMEMUNIC'),
            uf = db_args.get('SIGLAESTADO'),
            cep = db_args.get('CEPENDERESTAB'),
            bairro = db_args.get('BAIRROENDERESTAB'),
            rua = db_args.get('ENDERECOESTAB'),
            numero = db_args.get('NUMENDERESTAB'),
            complemento = db_args.get('COMPLENDERESTAB'),
            sigla = db_args.get('SIGLA'),
        )
        return obj
        
class SaldoConta:

    def __init__(self, *args, **kwargs):
        self.nome_conta = kwargs['nome_conta']
        self.saldo = kwargs['saldo']  
        self.data_saldo = kwargs['data_saldo']
        self.tipo_saldo = kwargs.get('tipo_saldo')

    def __str__(self):
        return f"{self.nome_conta} - {self.data_saldo}"

    def __repr__(self):
        _repr = "SaldoConta(nome_conta={0}, saldo={1}, data_saldo={2}, tipo_saldo={3})"
        _repr = _repr.format(self.nome_conta, self.saldo, self.data_saldo, self.tipo_saldo)
        return _repr

    @staticmethod
    def instance_from_database_args(db_args):
        kwargs = {
            'nome_conta': db_args['DESCRCONTA'],
            'saldo': db_args['SALDO'],
            'data_saldo': db_args['DATASALDO'],
            'tipo_saldo': db_args.get('TIPOSALDO'),
        }
        return SaldoConta(**kwargs)

    @property
    def saldo(self):
        return self._saldo 

    @saldo.setter 
    def saldo(self, saldo):
        saldo = "{:,.2f}".format(saldo).split('.')
        saldo = "{0},{1}".format(saldo[0].replace(',','.'), saldo[1])
        self._saldo = saldo