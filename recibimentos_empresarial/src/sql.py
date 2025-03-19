def get_recebimentos(escritorio,dataini,datafim,codigos):
    codigos = codigos if len(codigos) > 1 else f"({codigos[0]})"
    sql = """
        select
            c.codigoescrit,
            c.datarctocr,
            c.codigocaixaconta, 
            c.numerodctocr,
            (r.codigocliente||' - '||p.nome) cliente,
            sum(c.valorrctocr) valor
        from
            contarecebida c
        join
            contareceber r on
            c.codigoescrit = r.codigoescrit and
            c.numerodctocr = r.numerodctocr 
        join 
            pessoafinanceiro p on
            r.codigocliente = p.codigopessoafin 
        where
            c.codigoescrit = {0} and
            c.codigocaixaconta in {3} and
            c.datarctocr between '{1}' and '{2}' 
        group by 1,2,3,4,5
        union all
        select 
            s.codigoescrit,
            s.dataemissaons,
            s.codigocaixaconta,
            s.seriens ||s.numerons numerodctocr,
            (s.codigocliente||' - '||p.nome) cliente,
            sum(s.valorliquido) valor
        from
            serviconota s
        join 
            pessoafinanceiro p on
            s.codigocliente = p.codigopessoafin 
        where
            s.codigoescrit = {0} and
            codigocaixaconta in {3} and
            s.dataemissaons between '{1}' and '{2}' 
        group by
            1,2,3,4,5
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
        select
            cast(substring(c.codigoescrit::text from 2 for 3) as numeric) codigoescrit,
            c.datarctocr,
            c.codigocaixaconta, 
            c.numerodctocr,
            (r.codigocliente||' - '||p.nome) cliente,
            sum(c.multarctocr+c.jurorctocr) valor
        from
            contarecebida c
        join
            contareceber r on
            c.codigoescrit = r.codigoescrit and
            c.numerodctocr = r.numerodctocr 
        join 
            pessoafinanceiro p on
            r.codigocliente = p.codigopessoafin 
        where
            c.codigoescrit = 9000+{0} and
            c.codigocaixaconta in {3} and
            c.datarctocr between '{1}' and '{2}' 
        group by
            1,2,3,4,5
        having
            sum(c.multarctocr+c.jurorctocr) <> 0
    """.format(escritorio,dataini,datafim,codigos)
    return sql

def get_max_lancamento():
    sql = """
        select max(CD_LANCAMENTO) from TBL_FINANCEIRO_CONTA_CORRENTE_LANCAMENTOS_DIARIOS
    """
    return sql