class InadimplenciaSqls:
    db_table = 'CONTARECEBER'

    def get_inadimplentes(self):
        sql = """
            SELECT SUM(VALORCR), 
	            'RECEB. APOS PRAZO' TIPO,
	            CAST('NOW' AS DATE)- extract(day from cast('now' as date)) AS DATA
                FROM CONTARECEBER CR
                LEFT JOIN CONTARECEBIDA CD ON CR.CODIGOESCRIT = CD.CODIGOESCRIT AND
                CR.NUMERODCTOCR = CD.NUMERODCTOCR
                WHERE CR.CODIGOESCRIT IN (9501,9502,9505,9567,9575) AND
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
                WHERE CR.CODIGOESCRIT IN (9501,9502,9505,9567,9575) AND
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
    
    def get_detalhamento(self, data):
        sql = f"""
            SELECT
                VALORCR,
                CR.CODIGOESCRIT,
                CR.CODIGOCLIENTE,
                CR.NUMERONS,
                'ABERTO',
                DATEADD(-2 MONTH TO CAST('{data}' AS DATE)) - EXTRACT(DAY FROM CAST('{data}' AS DATE))+ 1 AS DATA
            FROM
                CONTARECEBER CR
            LEFT JOIN
                CONTARECEBIDA CD ON
                CR.CODIGOESCRIT = CD.CODIGOESCRIT
                AND CR.NUMERODCTOCR = CD.NUMERODCTOCR
            WHERE
                CR.CODIGOESCRIT IN (9501,9502,9505,9567,9575)
                AND DATAEMISSAOCR BETWEEN DATEADD(-2 MONTH TO CAST('{data}' AS DATE)) - EXTRACT(DAY FROM CAST('{data}' AS DATE))+ 1 AND
                DATEADD(-1 MONTH TO CAST('{data}' AS DATE)) - EXTRACT(DAY FROM DATEADD(-1 MONTH TO CAST('{data}' AS DATE)))
                AND STATUSCR = 1
                AND DATAVCTOCR <= CAST('{data}' AS DATE)- EXTRACT(DAY FROM CAST('{data}' AS DATE))
                AND (CR.NUMERODCTOCR NOT LIKE 'X%' OR CD.NUMERODCTOCR NOT LIKE 'X%')
        """
        return sql