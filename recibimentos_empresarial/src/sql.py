def get_recebimentos(escritorio,dataini,datafim,codigos):
    codigos = codigos if len(codigos) > 1 else f"({codigos[0]})"
    sql = """
        SELECT
            C.CODIGOESCRIT,
            C.DATARCTOCR,
            C.CODIGOCAIXACONTA, 
            C.NUMERODCTOCR,
	        (R.CODIGOCLIENTE||' - '||P.NOME) CLIENTE,
            SUM(C.VALORRCTOCR) VALOR
        FROM
            CONTARECEBIDA C
        JOIN
            CONTARECEBER R ON
            C.CODIGOESCRIT = R.CODIGOESCRIT AND
            C.NUMERODCTOCR = R.NUMERODCTOCR 
        JOIN 
            PESSOAFINANCEIRO P ON
            R.CODIGOCLIENTE = P.CODIGOPESSOAFIN 
        WHERE
            C.CODIGOESCRIT = {0} AND
            C.CODIGOCAIXACONTA IN {3} AND
            C.DATARCTOCR BETWEEN '{1}' AND '{2}' 
        GROUP BY 1,2,3,4,5
        UNION ALL
        SELECT 
            S.CODIGOESCRIT,
            S.DATAEMISSAONS,
            S.CODIGOCAIXACONTA,
	        S.SERIENS ||S.NUMERONS NUMERODCTOCR,
	        (S.CODIGOCLIENTE||' - '||P.NOME) CLIENTE,
            SUM(S.VALORBRUTO) VALOR
        FROM
            SERVICONOTA S
        JOIN 
            PESSOAFINANCEIRO P ON
            S.CODIGOCLIENTE = P.CODIGOPESSOAFIN 
        WHERE
            S.CODIGOESCRIT = {0} AND
            CODIGOCAIXACONTA IN {3} AND
            S.DATAEMISSAONS BETWEEN '{1}' AND '{2}' 
        GROUP BY 1,2,3,4,5
    """.format(escritorio,dataini,datafim,codigos)
    return sql

def get_lancamentos(filial,dataini,datafim):
    sql = """
        SELECT 
            NR_DOCUMENTO,
            DT_LANCAMENTO,
            VL_ENTRADA 
        FROM 
            TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS
        WHERE
            CD_USUARIO = 0 AND
            CD_FILIAL = {0} AND
            DT_LANCAMENTO >= '{1}' AND
            DT_LANCAMENTO <= '{2}'
    """.format(filial,dataini,datafim)
    return sql

def get_juros(escritorio,dataini,datafim,codigos):
    codigos = codigos if len(codigos) > 1 else f"({codigos[0]})"
    sql = """
        SELECT
            CAST(SUBSTRING(C.CODIGOESCRIT FROM 2 FOR 3) AS NUMERIC) CODIGOESCRIT,
            C.DATARCTOCR,
            C.CODIGOCAIXACONTA, 
            C.NUMERODCTOCR,
            (R.CODIGOCLIENTE||' - '||P.NOME) CLIENTE,
            SUM(C.MULTARCTOCR+C.JURORCTOCR) VALOR
        FROM
            CONTARECEBIDA C
        JOIN
            CONTARECEBER R ON
            C.CODIGOESCRIT = R.CODIGOESCRIT AND
            C.NUMERODCTOCR = R.NUMERODCTOCR 
        JOIN 
            PESSOAFINANCEIRO P ON
            R.CODIGOCLIENTE = P.CODIGOPESSOAFIN 
        WHERE
            C.CODIGOESCRIT = 9000+{0} AND
            C.CODIGOCAIXACONTA IN {3} AND
            C.DATARCTOCR BETWEEN '{1}' AND '{2}' 
        GROUP BY 1,2,3,4,5
        HAVING SUM(C.MULTARCTOCR+C.JURORCTOCR) <> 0
    """.format(escritorio,dataini,datafim,codigos)
    return sql

def get_max_lancamento():
    sql = """
        select max(CD_LANCAMENTO) from TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS
    """
    return sql