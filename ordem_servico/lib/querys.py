from ..models import OrdemServico

def filter_planilha(filtros):
    try:
        dados = OrdemServico.objects.all()
        
        if 'empresa' in filtros:
            empresa = filtros.get('empresa')
            dados = dados.filter(cd_empresa=empresa)
            
        if 'data_da_cobranca' in filtros:
            data = '-'.join(filtros.get('data_da_cobranca').split("/")[::-1])
            dados = dados.filter(data_cobranca=data)
            
        if 'valor' in filtros:
            valor = filtros.get('valor').replace(".",'').replace(",",".")
            dados = dados.filter(valor=valor)
        
        if 'servico' in filtros:
            servico = filtros.get('servico').upper()
            dados = dados.filter(servico__icontains=servico)
            
        if ('min_date' in filtros or 'max_date' in filtros) and not 'data_da_cobranca' in filtros:
            if 'min_date' in filtros and 'max_date' in filtros:
                min_date = filtros.get('min_date')
                max_date = filtros.get('max_date')
                dados= dados.filter(data_cobranca__range=[min_date, max_date])
            elif 'min_date' in filtros:
                min_date = filtros.get('min_date')
                dados= dados.filter(data_cobranca__gte=min_date)
            elif 'max_date' in filtros:
                max_date = filtros.get('max_date')
                dados= dados.filter(data_cobranca__lte=max_date)

        if 'status' in filtros:
            status = filtros.get('status').upper()
            if status == 'DEBITADO':
                dados = dados.filter(debitar=True)
            if status == 'DEBITAR':
                dados = dados.filter(debitar=False)
            if status == 'ARQUIVADO':
                dados = dados.filter(arquivado=True)
        
    except Exception as err:
        raise Exception(err)
    else:
        return dados

def get_codigo_escritorio(empresa, cursor):
    sql = f"""
        SELECT
            DISTINCT
            S.CODIGOESCRIT
        FROM
            SERVICOFIXO S
        JOIN
            PESSOAFINANCEIRO P ON
            S.CODIGOCLIENTE = P.CODIGOPESSOAFIN
        WHERE
            P.CODIGOEMPRESA = {empresa} AND
            S.CODIGOSERVICOESCRIT IN (1,81,115,127,151,155)
    """
    query = cursor.execute(sql).fetchone()
    return query[0] if query else None

def get_sequencia_variavel_empresa(empresa, data_cobranca, cursor):
    sql = f"""
        SELECT
            CASE
                WHEN MAX(SEQSERVVAR) IS NULL THEN 1
                ELSE MAX(SEQSERVVAR+1)
            END SEQVAR
        FROM
            SERVICOVARIAVEL
        WHERE
            CODIGOCLIENTE = {empresa}
            AND DATASERVVAR = '{data_cobranca}'
    """
    query = cursor.execute(sql).fetchone()
    return query[0] if query else None

def get_id_ordem_servico(cursor):
    sql = """
        SELECT
            CASE
                WHEN MAX(SEQUENCIACAIXA) IS NULL THEN 1
                ELSE MAX(SEQUENCIACAIXA+1)
            END SEQVAR
        FROM
            SERVICOVARIAVEL
    """
    query = cursor.execute(sql).fetchone()
    return query[0] if query else None

def valid_notas_delete(id_ordem_banco, cursor):
    sql = f"""
        SELECT
            SERIENS,
            NUMERONS,
            CASE
                WHEN SERIENS IS NULL AND NUMERONS IS NULL THEN 'SEM NOTA FISCAL'
                ELSE 'POSSUI NOTA'
            END
        FROM
            SERVICOVARIAVEL
        WHERE
            SEQUENCIACAIXA = {id_ordem_banco}
    """
    response = {'valid': True, 'msg': ''}
    query = cursor.execute(sql).fetchall()
    if query:
        query = query[0]
        if query[2] == 'SEM NOTA FISCAL':
            response['valid'] = True
        else:
            response['valid'] = False
            response['msg'] = f"Primeiramente Apague as Notas desta OS: {'SERIENS: '+str(query[0]) if query[0] else '' }, {'NUMERONS: '+str(query[1]) if query[1] else ''}"
    else:
        response['valid'] = False
        response['msg'] = "Erro na Busca das Notas, tente Novamente."
        
    return response

def build_insert_os(id_ordem_banco, ordem, codigo_escritorio, sequencia_variavel_empresa):
    valor_total = ordem.quantidade * ordem.valor
    sql = f"""
        INSERT INTO SERVICOVARIAVEL (CODIGOESCRIT, CODIGOCLIENTE, CODIGOSERVICOESCRIT, DATASERVVAR, SEQSERVVAR, SERIENS, NUMERONS, SEQSERVNOTAITEM, QTDADESERVVAR, VALORUNITSERVVAR, VALORTOTALSERVVAR, OBSERVSERVVAR, SITANTECIPACAO, SEQLCTO, CODIGOUSUARIO, DATAHORALCTO, ORIGEMDADO, CHAVEPGTOANTECIP, VALORANTERIORUNITSERVVAR, SEQUENCIACAIXA, CHAVEORIGEM) VALUES({codigo_escritorio}, {ordem.cd_empresa}, {ordem.cd_servico}, '{ordem.data_cobranca}', {sequencia_variavel_empresa}, NULL, NULL, NULL, {ordem.quantidade}, {ordem.valor}, {valor_total}, '{ordem.ds_servico}', NULL, NULL, 0, CAST('NOW' AS TIMESTAMP), 3, NULL, NULL, {id_ordem_banco}, NULL) returning SEQUENCIACAIXA;
    """
    return sql

def build_delete_os(id_ordem_banco):
    sql = f"""
        DELETE FROM SERVICOVARIAVEL WHERE SEQUENCIACAIXA = {id_ordem_banco}
    """
    return sql