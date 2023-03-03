from Database.models import Connection, TareffaConnection

class Manager(Connection):
    def __init__(self, *args, **kwargs):
        self.codigo_empresa = kwargs.get('codigo_empresa')

    def get_empresa(self):
        sql = """
            SELECT CODIGOEMPRESA,
                INSCRFEDERAL,
                NOMEESTAB
            FROM ESTAB WHERE CODIGOEMPRESA = {0}
        """.format( self.codigo_empresa )
        return sql
    
class ManagerTareffa(TareffaConnection):
    def __init__(self, codigo_empresa):
        self.codigo_empresa = codigo_empresa
        self.default_connect()

    def get_empresa(self):
        try:
            self.connect()
            sql = f"""
                select
                    cast(
                        case
                            when position('/' in codigoquestor) = 0 then '1'
                            else right(codigoquestor, position('/' in reverse(codigoquestor))-1)
                        end as int) filial,	
                    e.razaosocial
                from 
                    depaula.view_empresas e
                where
                    cast(
                        case
                            when position('/' in e.codigoquestor) <> 0 then left(e.codigoquestor, (position('/' in e.codigoquestor))-1)
                            when position('-' in e.codigoquestor) <> 0 then left(e.codigoquestor, (position('-' in e.codigoquestor))-1)
                            else e.codigoquestor
                        end as int) = {self.codigo_empresa} and
                        estaativa = true
            """
            self.execute_sql(sql)
            result = [list(i) for i in self.cursor.fetchall()]
        except Exception as err:
            raise Exception(err)
        else:
            return result
        finally:
            self.disconnect()
        
    