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
                dados = dados.filter(cod_os_omie__isnull=False)
            if status == 'DEBITAR':
                dados = dados.filter(cod_os_omie__isnull=True, arquivado=False)
            if status == 'ARQUIVADO':
                dados = dados.filter(arquivado=True)
        
    except Exception as err:
        raise Exception(err)
    else:
        return dados

def get_cnpj_empresas(empresas_request=None):
    if empresas_request:
        empresas = tuple(empresas_request) if len(empresas_request) > 1 else f"('{empresas_request[0]}')"
    filter_emp = f"and e.codigoquestor in {empresas}" if empresas_request else ''
    return rf"""
        select 
            regexp_replace(e.codigoquestor, '^(\d+)[-/.]s*.*$', '\1')::int codigoquestor,
            upper(e.razaosocial) razaosocial,
            case when regexp_replace(e.codigoquestor, '^(\d+)[-/.](\d+)', '\2') = e.codigoquestor then '1' else regexp_replace(e.codigoquestor, '^(\d+)[-/.](\d+)', '\2') end::int filial,
            e.cnpj
        from 
            ottimizza_clientes.depaula_view_empresas e
        where 
            e.codigoquestor not in ('999-000-909', '9999', '999999999')
            and e.situacao not in ('BAIXADA','RESCINDIDA')
            {filter_emp}
    """