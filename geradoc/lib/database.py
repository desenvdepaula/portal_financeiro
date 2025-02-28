from Database.models import PostgreSQLConnection

class Manager(PostgreSQLConnection):

    def get_empresa(self, empresa, estabelecimento = 1):
        sql = f"""
            SELECT CODIGOEMPRESA,
                NOMEESTAB,
                INSCRFEDERAL,
                TL.SIGLA ,
                ENDERECOESTAB,
                NUMENDERESTAB,
                BAIRROENDERESTAB,
                NOMEMUNIC,
                INSCRMUNIC,
                E.SIGLAESTADO,
                CEPENDERESTAB,
                DDDFONE,
                NUMEROFONE,
                COMPLENDERESTAB
            FROM ESTAB E
                INNER JOIN TIPOLOGRADOURO as TL 
                    ON TL.CODIGOTIPOLOGRAD = E.CODIGOTIPOLOGRAD
                JOIN MUNICIPIO M 
                    ON E.CODIGOMUNIC = M.CODIGOMUNIC 
                    AND E.SIGLAESTADO = M.SIGLAESTADO 
            WHERE CODIGOEMPRESA = {empresa}
                AND CODIGOESTAB = {estabelecimento}
        """
        return sql
    
    def get_socios(self, empresa):
        sql = f"""
            SELECT CFG.CODIGOEMPRESA,
                S.NOMESOCIO, 
                S.INSCRFEDERAL,
                S.DESCRCARGO
            FROM CFGEMPRESAGEM as CFG 
                INNER JOIN SOCIO AS S ON S.CODIGOEMPRESA=CFG.CODIGOEMPRESA
            WHERE CFG.CODIGOEMPRESA = {empresa} AND CFG.SOCIORESPCNPJ != S.CODIGOSOCIO
        """
        return sql

    def get_socio_administrador(self, empresa):
        sql = f"""
            SELECT CFG.CODIGOEMPRESA,
                S.NOMESOCIO, 
                S.INSCRFEDERAL,
                S.DESCRCARGO,
                S.DATANASC,
                S.ENDERECOSOCIO,
                TL.SIGLA,
                S.NUMENDERSOCIO,
                S.COMPLENDERSOCIO,
                S.BAIRROENDERSOCIO,
                S.CEPENDERSOCIO,
                S.SIGLAESTADO,
                E.NOMEESTADO,
                M.NOMEMUNIC,
                S.NUMERORG,
                S.SIGLAESTADORG,
                OE.SIGLAORGAOEMISSOR,
                S.ESTADOCIVIL,
                S.REGIMECASAMENTO,
                S.MAIORMENORIDADE,
                S.NACIONALIDADE, 
                S.CODIGOORGAOEMISSORRG     
            FROM CFGEMPRESAGEM as CFG 
                LEFT JOIN SOCIO AS S ON S.CODIGOEMPRESA=CFG.CODIGOEMPRESA
                LEFT JOIN MUNICIPIO as M ON M.CODIGOMUNIC = S.CODIGOMUNIC AND M.SIGLAESTADO = S.SIGLAESTADO
                LEFT JOIN TIPOLOGRADOURO as TL ON TL.CODIGOTIPOLOGRAD = S.CODIGOTIPOLOGRAD
                LEFT JOIN ESTADO as E ON E.SIGLAESTADO = S.SIGLAESTADO
                LEFT JOIN ORGAOEMISSOR AS OE ON OE.CODIGOORGAOEMISSOR = S.CODIGOORGAOEMISSORRG OR OE.CODIGOORGAOEMISSOR IS NULL
                AND CFG.SOCIORESPCNPJ = S.CODIGOSOCIO 
            WHERE CFG.CODIGOEMPRESA = {empresa} AND CFG.SOCIORESPCNPJ = S.CODIGOSOCIO
        """
        return sql

    