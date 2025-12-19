from ..models import OrdemServico

def sql_get_services_questor(codigos):
    sql = f"""
        select
            codigoservicoescrit,
            descrservicoescrit
        from
            servicoescrit
        {f"where codigoservicoescrit not in {codigos}" if codigos else ""}
        order by
            2
    """
    return sql

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
                dados = dados.filter(debitar=False, arquivado=False)
            if status == 'ARQUIVADO':
                dados = dados.filter(arquivado=True)
        
    except Exception as err:
        raise Exception(err)
    else:
        return dados

def get_cnpj_empresas():
    return rf"""
        select 
            regexp_replace(e.codigoquestor, '^(\d+)[-/.]s*.*$', '\1')::int codigoquestor,
            case when regexp_replace(e.codigoquestor, '^(\d+)[-/.](\d+)', '\2') = e.codigoquestor then '1' else regexp_replace(e.codigoquestor, '^(\d+)[-/.](\d+)', '\2') end::int filial,
            e.cnpj
        from 
            ottimizza_clientes.depaula_view_empresas e
        where 
            e.codigoquestor not in ('999-000-909', '9999', '999999999')
            and e.situacao not in ('BAIXADA','RESCINDIDA')
    """

def get_codigo_escritorio(empresa, cursor):
    sql = f"""
        select
            distinct
            s.codigoescrit
        from
            servicofixo s
        join
            pessoafinanceiro p on
            s.codigocliente = p.codigopessoafin
        where
            p.codigopessoafin = {empresa} and
            s.codigoservicoescrit in (1,81,115,127,151,155)
    """
    cursor.execute(sql)
    query = cursor.fetchone()
    return query[0] if query else None

def get_sequencia_variavel_empresa(empresa, data_cobranca, cursor):
    sql = f"""
        select
            case
                when max(seqservvar) is null then 1
                else max(seqservvar+1)
            end seqvar
        from
            servicovariavel
        where
            codigocliente = {empresa}
            and dataservvar = '{data_cobranca}'
    """
    cursor.execute(sql)
    query = cursor.fetchone()
    return query[0] if query else None

def get_id_ordem_servico(cursor):
    sql = """
        select
            case
                when max(sequenciacaixa) is null then 1
                else max(sequenciacaixa+1)
            end seqvar
        from
            servicovariavel
    """
    cursor.execute(sql)
    query = cursor.fetchone()
    return query[0] if query else None

def valid_notas_delete(id_ordem_banco, cursor):
    sql = f"""
        select
            seriens,
            numerons,
            case
                when seriens is null and numerons is null then 'SEM NOTA FISCAL'
                else 'POSSUI NOTA'
            end
        from
            servicovariavel
        where
            sequenciacaixa = {id_ordem_banco}
    """
    response = {'valid': True, 'msg': ''}
    cursor.execute(sql)
    query = cursor.fetchall()
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
        insert into servicovariavel (codigoescrit, codigocliente, codigoservicoescrit, dataservvar, seqservvar, seriens, numerons, seqservnotaitem, qtdadeservvar, valorunitservvar, valortotalservvar, observservvar, sitantecipacao, seqlcto, codigousuario, datahoralcto, origemdado, chavepgtoantecip, valoranteriorunitservvar, sequenciacaixa, chaveorigem) values({codigo_escritorio}, {ordem.cd_empresa}, {ordem.cd_servico}, '{ordem.data_cobranca}', {sequencia_variavel_empresa}, null, null, null, {ordem.quantidade}, {ordem.valor}, {valor_total}, '{ordem.ds_servico.replace("'","").replace("–","-")}', null, null, 492, now(), 3, null, null, {id_ordem_banco}, null) returning sequenciacaixa;
    """
    return sql

def build_delete_os(id_ordem_banco):
    sql = f"""
        delete from servicovariavel where sequenciacaixa = {id_ordem_banco}
    """
    return sql