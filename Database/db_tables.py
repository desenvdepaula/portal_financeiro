
class TBL_FUNCCONTRATO:
    db_table = "FUNCCONTRATO"

    def get_funcionario_codigo_matricula(self, cd_empresa, cd_matricula):
        sql = f"""
            select
                fp.nomefunc,
                fc.codigofunccontr, 
                fp.cpffunc,
                banco.nomebanco, 
                fc.codigobanco,
                fc.numeroagencia,
                fc.numeroconta,
                fc.digitoconta,
                cast(ft.numeroctps as varchar(12)) || cast('/' as varchar(12)) || cast(ft.seriectps as varchar(12)) carteiraprofissional,
                fp.enderfunc, 
                fp.complender,
                fp.numeroender,
                fp.bairrofunc,
                fp.siglaestado,
                m.nomemunic,
                fp.codigopostal,
                fp.cepfunc,
                fp.dddfone,
                fp.numerofone 
            from
                funccontrato fc
            join
                funcpessoa fp on
                fc.codigofuncpessoa = fp.codigofuncpessoa
            left join 
                banco on
                fc.codigobanco = banco.codigobanco
            join
                municipio m on
                m.codigomunic = fp.codigomunic
                and m.siglaestado = fp.siglaestado  
            join
                funcctps ft on
                fc.codigoempresa = ft.codigoempresa 
                and fc.codigofunccontr = ft.codigofunccontr
                and ft.datainicial = (select max(ft1.datainicial) from funcctps ft1 where ft1.codigoempresa = ft.codigoempresa and ft1.codigofunccontr = ft.codigofunccontr) 
            where
                fc.codigoempresa = {cd_empresa}
                and fc.codigofunccontr = {cd_matricula}
        """
        return sql

class TBL_ESTAB:
    db_table = "ESTAB"

    def get_estabelecimento(self, cd_empresa, cd_estab = 1):
        sql = """
                SELECT CODIGOEMPRESA,
                    INSCRFEDERAL,
                    TL.SIGLA ,
                    ENDERECOESTAB,
                    NUMENDERESTAB,
                    BAIRROENDERESTAB,
                    NOMEMUNIC,
                    INSCRMUNIC,
                    E.SIGLAESTADO,
                    CEPENDERESTAB,
                    NOMEESTAB,
                    DDDFONE,
                    NUMEROFONE,
                    COMPLENDERESTAB
                FROM {db_table} E
                    INNER JOIN TIPOLOGRADOURO as TL ON TL.CODIGOTIPOLOGRAD = E.CODIGOTIPOLOGRAD
                    JOIN MUNICIPIO M ON E.CODIGOMUNIC = M.CODIGOMUNIC AND
                    E.SIGLAESTADO = M.SIGLAESTADO WHERE CODIGOEMPRESA = {cd_empresa} AND CODIGOESTAB = {cd_estab}
            """.format(
                cd_empresa = cd_empresa,
                cd_estab = cd_estab,
                db_table = self.db_table
            )
        return sql

class TBL_SOCIO:
    db_table = "SOCIO"

    def get_socio_administrador(self, cd_empresa):
        sql = """
        SELECT CFG.CODIGOEMPRESA,
            S.NOMESOCIO, 
            S.INSCRFEDERAL,
            TL.SIGLA,
            S.ENDERECOSOCIO,
            S.NUMENDERSOCIO,
            S.COMPLENDERSOCIO,
            S.BAIRROENDERSOCIO,
            S.CEPENDERSOCIO,
            S.SIGLAESTADO,
            E.NOMEESTADO,
            M.NOMEMUNIC,
            S.NUMERORG,
            S.SIGLAESTADORG,            
            S.DATANASC,
            S.ESTADOCIVIL,
            S.REGIMECASAMENTO,
            S.MAIORMENORIDADE,
            S.DESCRCARGO,
            S.CODIGOORGAOEMISSORRG,
            S.NACIONALIDADE, 
            OE.SIGLAORGAOEMISSOR 
        FROM CFGEMPRESAGEM as CFG 
            INNER JOIN SOCIO AS S ON S.CODIGOEMPRESA=CFG.CODIGOEMPRESA
            INNER JOIN MUNICIPIO as M ON M.CODIGOMUNIC = S.CODIGOMUNIC AND M.SIGLAESTADO = S.SIGLAESTADO
            INNER JOIN TIPOLOGRADOURO as TL ON TL.CODIGOTIPOLOGRAD = S.CODIGOTIPOLOGRAD
            INNER JOIN ESTADO as E ON E.SIGLAESTADO = S.SIGLAESTADO
            LEFT JOIN ORGAOEMISSOR AS OE ON OE.CODIGOORGAOEMISSOR = S.CODIGOORGAOEMISSORRG OR OE.CODIGOORGAOEMISSOR IS NULL
            AND CFG.SOCIORESPCNPJ = S.CODIGOSOCIO 
        WHERE CFG.CODIGOEMPRESA = {0} AND CFG.SOCIORESPCNPJ = S.CODIGOSOCIO
            """.format(cd_empresa)
        return sql

class TBL_SALDOCTB:

    def get_lancamento_conta_empresa_por_periodo(self, cd_empresa, cd_conta, inicio_periodo, fim_periodo):
        sql = f"""
        SELECT 
            DESCRCONTA,
            SUM(VALORDEB-VALORCRED) AS SALDO,
            DATASALDO
        FROM SALDOCTBMENSAL S
            JOIN PLANOESPEC P ON P.CODIGOEMPRESA = S.CODIGOEMPRESA 
                AND P.CONTACTB = S.CONTACTB
        WHERE S.CODIGOEMPRESA = {cd_empresa}
            AND S.CONTACTB = {cd_conta} 
            AND DATASALDO BETWEEN '{inicio_periodo}' AND '{fim_periodo}'
        GROUP BY 1,3
        """
        return sql

    def get_saldo_conta_empresa_por_periodo(self, cd_empresa, cd_conta, inicio_periodo, fim_periodo):
        sql = f"""
        SELECT
            P.DESCRCONTA,
            SUM(VALORDEB-VALORCRED) SALDO,
            CAST('{fim_periodo}' AS DATE) AS DATASALDO,
            'FINAL' TIPOSALDO
        FROM
            SALDOCTBMENSAL S
        JOIN PLANOESPEC P ON
            S.CODIGOEMPRESA = P.CODIGOEMPRESA
            AND S.CONTACTB = P.CONTACTB
        WHERE
            EXTRACT(YEAR FROM DATASALDO) <= EXTRACT(YEAR FROM CAST('{fim_periodo}' AS DATE))
            AND S.CODIGOEMPRESA = {cd_empresa}
            AND S.CONTACTB = {cd_conta}
        GROUP BY
            1,3
        UNION
        SELECT
            P.DESCRCONTA,
            SUM(VALORDEB-VALORCRED) SALDO,
            CAST('{inicio_periodo}' AS DATE) AS DATASALDO,
            'INICIAL' TIPOSALDO
        FROM
            SALDOCTBMENSAL S
        JOIN PLANOESPEC P ON
            S.CODIGOEMPRESA = P.CODIGOEMPRESA
            AND S.CONTACTB = P.CONTACTB
        WHERE
            EXTRACT(YEAR FROM DATASALDO) <= EXTRACT(YEAR FROM CAST('{inicio_periodo}' AS DATE))
            AND S.CODIGOEMPRESA = {cd_empresa}
            AND S.CONTACTB = {cd_conta}
        GROUP BY
            1,3
        """
        return sql

class TBL_CONTARECEBER:
    db_table = 'CONTARECEBER'

    def get_inadimplentes(self):
        sql = """
            SELECT SUM(VALORCR), 
	            'RECEB. APOS PRAZO' TIPO,
	            CAST('NOW' AS DATE)- extract(day from cast('now' as date)) AS DATA
                FROM CONTARECEBER CR
                LEFT JOIN CONTARECEBIDA CD ON CR.CODIGOESCRIT = CD.CODIGOESCRIT AND
                CR.NUMERODCTOCR = CD.NUMERODCTOCR
                WHERE CR.CODIGOESCRIT IN (9501,9502,9505,9567) AND
                DATAEMISSAOCR BETWEEN dateadd(-2 month to CAST('NOW' AS DATE)) - extract(day from cast('now' as date))+1 AND
                dateadd(-1 month to CAST('NOW' AS DATE)) - extract(day from dateadd(-1 month to cast('now' as date))) AND
                STATUSCR = 3 and
                DATARCTOCR > CAST('NOW' AS DATE)- extract(day from cast('now' as date)) AND
                DATAVCTOCR <= CAST('NOW' AS DATE)- extract(day from cast('now' as date)) AND
                (CR.NUMERODCTOCR NOT LIKE 'X%' OR CD.NUMERODCTOCR NOT LIKE 'X%')
                UNION
                SELECT SUM(VALORCR), 'ABERTO', dateadd(-2 month to CAST('NOW' AS DATE)) - extract(day from cast('now' as date))+1 AS DATA
                FROM CONTARECEBER CR
                LEFT JOIN CONTARECEBIDA CD ON CR.CODIGOESCRIT = CD.CODIGOESCRIT AND
                CR.NUMERODCTOCR = CD.NUMERODCTOCR
                WHERE CR.CODIGOESCRIT IN (9501,9502,9505,9567) AND
                DATAEMISSAOCR BETWEEN dateadd(-2 month to CAST('NOW' AS DATE)) - extract(day from cast('now' as date))+1 AND
                dateadd(-1 month to CAST('NOW' AS DATE)) - extract(day from dateadd(-1 month to cast('now' as date))) AND
                STATUSCR = 1 AND
                DATAVCTOCR <= CAST('NOW' AS DATE)- extract(day from cast('now' as date)) AND
                (CR.NUMERODCTOCR NOT LIKE 'X%' OR CD.NUMERODCTOCR NOT LIKE 'X%')
                UNION
                SELECT SUM(VALORLIQUIDO), 'FATURADO', dateadd(-1 month to CAST('NOW' AS DATE)) - extract(day from dateadd(-1 month to cast('now' as date))) AS DATA
                FROM SERVICONOTA S
                WHERE S.SERIENS = 'F' AND
                DATAEMISSAONS BETWEEN dateadd(-2 month to CAST('NOW' AS DATE)) - extract(day from cast('now' as date))+1 AND
                dateadd(-1 month to CAST('NOW' AS DATE)) - extract(day from dateadd(-1 month to cast('now' as date))) AND
                CANCELADANS = 0
        """
        return sql
