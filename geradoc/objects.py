from .lib.utils import numeric_to_string
from decimal import Decimal

class InadimplenciaObj:

    def __init__(self, *args, **kwargs):
        self._recebido_apos_prazo = kwargs['recebido_apos_prazo']
        self._aberto = kwargs['aberto']
        self._faturado = kwargs['faturado']
        self._inadimplencia = self.total_inadimplencia()
        self._indice = self.total_indice()
        self._data = kwargs['data']
        self._data1 = kwargs['data1']
        self._data2 = kwargs['data2']

    def __repr__(self):
        return f"Inadimplencia(_recebido_apos_prazo: {self._recebido_apos_prazo}, _aberto: {self._aberto}, _faturado: {self._faturado}, _inadimplencia: {self._inadimplencia}, _indice: {self._indice}, _data: {self._data}), notas fiscal 1: {self._data1}, notas fiscal 2: {self._data2}"

    @staticmethod
    def instance_from_database_args(db_data):
        kwargs = {
            'recebido_apos_prazo' : '', 
            'aberto' : '', 
            'faturado' : '', 
            'data' : '', 
            'data1' : '', 
            'data2' : '', 
        }
        for idx, row in enumerate(db_data):
            if idx == 0:
                kwargs['recebido_apos_prazo'] = row['TOTAL'] or Decimal(0.0)
                kwargs['data'] = row['PERIODO']
            elif idx == 1:
                kwargs['aberto'] = row['TOTAL'] or Decimal(0.0)
                kwargs['data1'] = row['PERIODO']
            elif idx == 2:
                kwargs['faturado'] = row['TOTAL'] or Decimal(0.0)
                kwargs['data2'] = row['PERIODO']
        return InadimplenciaObj(**kwargs)

    def total_inadimplencia(self):
        return self._recebido_apos_prazo + self._aberto

    def total_indice(self):
        return ( self._inadimplencia / self._faturado ) * 100
    
    @property
    def recebido_apos_prazo(self):
        return numeric_to_string(self._recebido_apos_prazo)

    @property
    def aberto(self):
        return numeric_to_string(self._aberto)

    @property
    def faturado(self):
        return numeric_to_string(self._faturado)

    @property
    def inadimplencia(self):
        return numeric_to_string(self._inadimplencia)

    @property
    def indice(self):
        return numeric_to_string(self._indice)

    @property
    def data(self):
        return self._data

    @property
    def data1(self):
        return self._data1

    @property
    def data2(self):
        return self._data2