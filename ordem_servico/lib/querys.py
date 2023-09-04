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