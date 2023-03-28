class SqlHonorarios131:

    @staticmethod
    def getSqlHonorarios131(empresa, compet):
        sql = '''
                SELECT 
                    H.CODIGOEMPRESA EMPRESA,
                    COUNT(H.CODIGOFUNCCONTR) NUMERO,
                    FL.CODIGOESTAB FILIAL,
                    EXTRACT(MONTH FROM COMPET)|| '/' || EXTRACT(YEAR FROM COMPET) COMPET,
                    CASE
                        FC.CODIGOTIPOCONTR
                        WHEN 2 THEN 'DIRETOR/PRÓ-LABORE'
                        WHEN 5 THEN 'ESTAGIARIO'
                        WHEN 7 THEN 'APRENDIZ'
                        ELSE 'FOLHA'
                    END TIPOCONTRATO
                FROM
                    HISTCALCULOMENSAL H
                JOIN CALCULOEVENTO CE ON
                    H.CODIGOEMPRESA = CE.CODIGOEMPRESA AND
                    H.CODIGOFUNCCONTR = CE.CODIGOFUNCCONTR AND
                    H.CODIGOPERCALCULO = CE.CODIGOPERCALCULO
                JOIN FUNCCONTRATO FC ON
                    H.CODIGOEMPRESA = FC.CODIGOEMPRESA AND
                    H.CODIGOFUNCCONTR = FC.CODIGOFUNCCONTR
                JOIN FUNCLOCAL FL ON
                    H.CODIGOEMPRESA = FL.CODIGOEMPRESA AND
                    H.CODIGOFUNCCONTR = FL.CODIGOFUNCCONTR AND
                    H.DATALOCAL = FL.DATATRANSF
                JOIN ORGANOGRAMA O ON
                    FL.CODIGOEMPRESA = O.CODIGOEMPRESA AND
                    FL.CODIGOESTAB = O.CODIGOESTAB AND
                    FL.CLASSIFORGAN = O.CLASSIFORGAN
                JOIN PERIODOCALCULO P ON
                    P.CODIGOEMPRESA = H.CODIGOEMPRESA AND
                    H.CODIGOPERCALCULO = P.CODIGOPERCALCULO
                WHERE
                    H.CODIGOEMPRESA IN {0} AND
                    P.COMPET = '{1}' AND
                    ((CODIGOTIPOCONTR <> 5 AND CODIGOEVENTO = 5021) OR 
                    (CODIGOTIPOCONTR = 5 AND CODIGOEVENTO = 5022)) AND
                    P.CODIGOTIPOCALC = 1
                GROUP BY
                    1,3,4,5
                UNION
                SELECT
                    T.CODIGOEMPRESA,
                    COUNT(CODIGOTERC),
                    T.CODIGOESTAB,
                    EXTRACT(MONTH FROM COMPET)|| '/' || EXTRACT(YEAR FROM COMPET),
                    'TERCEIRO' TIPOCONTRATO
                FROM
                    TERCEIROPGTO T
                JOIN ORGANOGRAMA O ON
                    T.CODIGOEMPRESA = O.CODIGOEMPRESA AND
                    T.CODIGOESTAB = O.CODIGOESTAB AND
                    T.CLASSIFORGAN = O.CLASSIFORGAN
                WHERE
                    COMPET = '{1}' AND
                    T.CODIGOEMPRESA IN {0} AND
                    T.GPSORIGEM IN (1, 3, 9, 5)
                GROUP BY
                    1,3,4,5
                ORDER BY
                    1,4,2
            '''.format(empresa, compet)
        return sql

    @staticmethod
    def getSqlHonorarios131Insert(cd_escritorio, cd_financeiro, direfenca_quantidade, valor, valor_multiplicado, quantidade, data, data_lancamento, codigo_sequencial):
        sql = f'''
                INSERT INTO SERVICOVARIAVEL (CODIGOESCRIT, CODIGOCLIENTE, CODIGOSERVICOESCRIT, DATASERVVAR, SEQSERVVAR, SERIENS, NUMERONS, SEQSERVNOTAITEM, QTDADESERVVAR, VALORUNITSERVVAR, VALORTOTALSERVVAR, OBSERVSERVVAR, SITANTECIPACAO, SEQLCTO, CODIGOUSUARIO, DATAHORALCTO, ORIGEMDADO, CHAVEPGTOANTECIP, VALORANTERIORUNITSERVVAR, SEQUENCIACAIXA, CHAVEORIGEM) 
                VALUES({cd_escritorio}, {cd_financeiro}, 131, '{data_lancamento}', {codigo_sequencial}, NULL, NULL, NULL, {direfenca_quantidade}, {valor}, {valor_multiplicado}, '{quantidade} - {'FOLHAS' if quantidade > 1 else 'FOLHA'} {data}', 1, NULL, 0, CAST('now' as timestamp), 3, NULL, NULL, NULL, NULL);
            '''
        return sql
    
    @staticmethod
    def getSqlHonorariosSequencialInsert(cd_escritorio, cd_financeiro, data):
        sql = f"""
                SELECT
                    MAX(SEQSERVVAR)+ 1
                FROM
                    SERVICOVARIAVEL
                WHERE
                    CODIGOESCRIT = {cd_escritorio}
                    AND CODIGOCLIENTE = {cd_financeiro}
                    AND CODIGOSERVICOESCRIT = 131
                    AND OBSERVSERVVAR LIKE '%{data}%'
            """
        return sql

    @staticmethod
    def getSqlValidador131(data):
        sql = f'''
            SELECT
                CODIGOCLIENTE,
                EXTRACT(MONTH FROM DATASERVVAR)||'/'||EXTRACT(YEAR FROM DATASERVVAR) DATA,
                QTDADESERVVAR
            FROM
                SERVICOVARIAVEL
            WHERE
                OBSERVSERVVAR LIKE '%{data}%'
                AND CODIGOSERVICOESCRIT = 131
                AND CODIGOESCRIT >= 9000
                AND CODIGOUSUARIO = 0
        '''
        return sql

    @staticmethod
    def getSqlHonorarios131Find():
        sql = '''
            SELECT DISTINCT
                CODIGOCLIENTE,
                CODIGOESCRIT
            FROM
                SERVICOFIXO
            WHERE 
                CODIGOESCRIT > 9000
        '''
        return sql

    @staticmethod
    def getSqlNomeEmpresa(empresa):
        sql = f'''
            SELECT NOMEEMPRESA FROM EMPRESA WHERE CODIGOEMPRESA = {empresa}
        '''
        return sql

    @staticmethod
    def getSqlSelectHonorarios131(empresas):
        sql = '''
            SELECT H.CODIGOEMPRESA EMPRESA, 
                COUNT(H.CODIGOFUNCCONTR) NUMERO, 
                UPPER(DESCRORGAN) CENTRO_CUSTO, 
                FL.CODIGOESTAB FILIAL, 
                'FOLHA' TIPO,
                EXTRACT(MONTH FROM COMPET)||'/'||EXTRACT(YEAR FROM COMPET) COMPET,
                CASE FC.CODIGOTIPOCONTR
                WHEN 2 THEN 'DIRETOR/PRÓ-LABORE'
                WHEN 5 THEN 'ESTAGIARIO'
                WHEN 7 THEN 'APRENDIZ'
                ELSE 'FOLHA'
                END TIPOCONTRATO
            FROM HISTCALCULOMENSAL H
            JOIN CALCULOEVENTO CE ON H.CODIGOEMPRESA = CE.CODIGOEMPRESA AND
                                    H.CODIGOFUNCCONTR = CE.CODIGOFUNCCONTR AND
                                    H.CODIGOPERCALCULO = CE.CODIGOPERCALCULO
            JOIN FUNCCONTRATO FC ON H.CODIGOEMPRESA = FC.CODIGOEMPRESA AND
                                    H.CODIGOFUNCCONTR = FC.CODIGOFUNCCONTR
            JOIN FUNCLOCAL FL ON H.CODIGOEMPRESA = FL.CODIGOEMPRESA AND
                                H.CODIGOFUNCCONTR = FL.CODIGOFUNCCONTR AND
                                H.DATALOCAL = FL.DATATRANSF
            JOIN ORGANOGRAMA O ON FL.CODIGOEMPRESA = O.CODIGOEMPRESA AND
                                FL.CODIGOESTAB = O.CODIGOESTAB AND
                                FL.CLASSIFORGAN = O.CLASSIFORGAN
            JOIN PERIODOCALCULO P ON P.CODIGOEMPRESA = H.CODIGOEMPRESA AND
                                    H.CODIGOPERCALCULO = P.CODIGOPERCALCULO 
            WHERE H.CODIGOEMPRESA IN {0} AND 
                P.COMPET = '01.'||
                            EXTRACT(MONTH FROM (DATEADD(-1 MONTH TO CAST('NOW' AS DATE)))) ||'.'||
                            EXTRACT(YEAR FROM (DATEADD(-1 MONTH TO CAST('NOW' AS DATE)))) AND 
                ((CODIGOTIPOCONTR <> 5 AND CODIGOEVENTO = 5021) OR 
                (CODIGOTIPOCONTR = 5 AND CODIGOEVENTO = 5022)) AND
                P.CODIGOTIPOCALC = 1
            GROUP BY 1,3,4,6,7
            UNION
            SELECT T.CODIGOEMPRESA, 
                COUNT(CODIGOTERC), 
                UPPER(DESCRORGAN) , 
                T.CODIGOESTAB, 
                CASE GPSORIGEM
                	WHEN 5 THEN 'MEI'
                	ELSE 'AUTONOMO'
                END,
                EXTRACT(MONTH FROM COMPET)||'/'||EXTRACT(YEAR FROM COMPET),
                'TERCEIRO' TIPOCONTRATO
            FROM TERCEIROPGTO T
            JOIN ORGANOGRAMA O ON T.CODIGOEMPRESA = O.CODIGOEMPRESA AND
                                T.CODIGOESTAB = O.CODIGOESTAB AND
                                T.CLASSIFORGAN = O.CLASSIFORGAN
            WHERE COMPET = '01.'||
                            EXTRACT(MONTH FROM (DATEADD(-1 MONTH TO CAST('NOW' AS DATE)))) ||'.'||
                            EXTRACT(YEAR FROM (DATEADD(-1 MONTH TO CAST('NOW' AS DATE)))) AND 
                T.CODIGOEMPRESA IN {0} AND T.GPSORIGEM IN (1,3,9,5)
            GROUP BY 1,3,4,5,6,7
            ORDER BY 1,4,2
        '''.format(empresas)
        return sql