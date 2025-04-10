from Database.models import PostgreSQLConnection

class Manager(PostgreSQLConnection):
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
    
class ManagerTareffa(PostgreSQLConnection):
    def __init__(self, codigo_empresa=0):
        self.codigo_empresa = codigo_empresa
        self.default_connect_tareffa()

    def get_empresa(self):
        self.connect()
        try:
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
            result = [list(i) for i in self.run_query_for_select(sql)]
        except Exception as err:
            raise Exception(err)
        else:
            return result
        finally:
            self.disconnect()
            
    def get_empresa_ativas(self):
        self.connect()
        try:
            sql = """
                select distinct
                    cast(case	
                        when position('/' in e.codigoquestor) <> 0 then left(e.codigoquestor, (position('/' in e.codigoquestor))-1)
                        when position('-' in e.codigoquestor) <> 0 then left(e.codigoquestor, (position('-' in e.codigoquestor))-1)
                        else e.codigoquestor
                    end as int) codigoquestor,
                    cast(case
                        when position('/' in e.codigoquestor) <> 0 then right(e.codigoquestor, position('/' in reverse(e.codigoquestor))-1)
                        when position('-' in e.codigoquestor) <> 0 then right(e.codigoquestor, position('-' in reverse(e.codigoquestor))-1)
                        when position('-' in e.codigoquestor) = 0 and position('/' in e.codigoquestor) = 0 then '1' 
                    end as int) filial,	
                    razaosocial, 
                    regimetributario 
                from
                    depaula.view_empresas e
                where
                    estaativa = true
            """
            result = [list(i) for i in self.run_query_for_select(sql)]
        except Exception as err:
            raise Exception(err)
        else:
            return result
        finally:
            self.disconnect()
        
    