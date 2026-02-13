class SqlHonorarios131:

    @staticmethod
    def getSqlHonorarios131(empresa, compet):
        sql = f'''
            select 
                h.codigoempresa empresa,
                count(h.codigofunccontr) numero,
                fl.codigoestab filial,
                extract(month from compet)|| '/' || extract(year from compet) compet,
                case
                    fc.codigotipocontr
                    when 2 then 'DIRETOR/PRÓ-LABORE'
                    when 5 then 'ESTAGIARIO'
                    when 7 then 'APRENDIZ'
                    else 'FOLHA'
                end tipocontrato
            from
                histcalculomensal h
            join
                calculoevento ce on
                h.codigoempresa = ce.codigoempresa
                and h.codigofunccontr = ce.codigofunccontr 
                and h.codigopercalculo = ce.codigopercalculo
            join
                funccontrato fc on
                h.codigoempresa = fc.codigoempresa
                and h.codigofunccontr = fc.codigofunccontr
            join
                funclocal fl on
                h.codigoempresa = fl.codigoempresa
                and h.codigofunccontr = fl.codigofunccontr
                and h.datalocal = fl.datatransf
            join
                organograma o on
                fl.codigoempresa = o.codigoempresa
                and fl.codigoestab = o.codigoestab
                and fl.classiforgan = o.classiforgan
            join
                periodocalculo p on
                p.codigoempresa = h.codigoempresa 
                and h.codigopercalculo = p.codigopercalculo
            where
                h.codigoempresa in {empresa}
                and p.compet = '{compet}' 
		        and (fc.datatransfemp is null or fc.datatransfemp <= p.datafinalfolha)
                and ((codigotipocontr <> 5 and codigoevento = 5021) or (codigotipocontr = 5 and codigoevento = 5022)) 
                and p.codigotipocalc = 1
            group by
                1,3,4,5
            union
            select
                t.codigoempresa,
                count(codigoterc),
                t.codigoestab,
                extract(month from compet)|| '/' || extract(year from compet),
                'TERCEIRO' tipocontrato
            from
                terceiropgto t
            join
                organograma o on
                t.codigoempresa = o.codigoempresa
                and t.codigoestab = o.codigoestab
                and t.classiforgan = o.classiforgan
            where
                compet = '{compet}' 
                and t.codigoempresa in {empresa}
                and t.gpsorigem in (1, 3, 9, 5)
            group by
                1,3,4,5
            order by
                1,4,2;
        '''
        return sql

    @staticmethod
    def getSqlNomeEmpresa(empresa):
        sql = f'''
            select nomeempresa from empresa where codigoempresa = {empresa}
        '''
        return sql

    @staticmethod
    def getSqlSelectHonorarios131(empresas):
        sql = f'''
            select
                h.codigoempresa empresa, 
                count(h.codigofunccontr) numero, 
                upper(descrorgan) centro_custo, 
                fl.codigoestab filial, 
                'FOLHA' tipo,
                extract(month from compet)||'/'||extract(year from compet) compet,
                case fc.codigotipocontr
                when 2 then 'DIRETOR/PRÓ-LABORE'
                when 5 then 'ESTAGIARIO'
                when 7 then 'APRENDIZ'
                else 'FOLHA'
                end tipocontrato
            from
                histcalculomensal h
            join
                calculoevento ce on
                h.codigoempresa = ce.codigoempresa 
                and h.codigofunccontr = ce.codigofunccontr 
                and h.codigopercalculo = ce.codigopercalculo
            join
                funccontrato fc on
                h.codigoempresa = fc.codigoempresa 
                and h.codigofunccontr = fc.codigofunccontr
            join
                funclocal fl on
                h.codigoempresa = fl.codigoempresa
                and h.codigofunccontr = fl.codigofunccontr 
                and h.datalocal = fl.datatransf
            join
                organograma o on
                fl.codigoempresa = o.codigoempresa
                and fl.codigoestab = o.codigoestab
                and fl.classiforgan = o.classiforgan
            join
                periodocalculo p on
                p.codigoempresa = h.codigoempresa 
                and h.codigopercalculo = p.codigopercalculo 
            where
                h.codigoempresa in {empresas} and 
                p.compet = date('01.' ||date_part('month', date(current_date - interval'1 month')) || '.' || date_part('year', date(current_date - interval'1 month')))
		        and (fc.datatransfemp is null or fc.datatransfemp <= p.datafinalfolha)
                and ((codigotipocontr <> 5 and codigoevento = 5021) or (codigotipocontr = 5 and codigoevento = 5022)) 
                and p.codigotipocalc = 1
            group by
                1,3,4,6,7
            union
            select
                t.codigoempresa, 
                count(codigoterc), 
                upper(descrorgan) , 
                t.codigoestab, 
                case gpsorigem
                    when 5 then 'MEI'
                    else 'AUTONOMO'
                end,
                extract(month from compet)||'/'||extract(year from compet),
                'TERCEIRO' tipocontrato
            from
                terceiropgto t
            join
                organograma o on
                t.codigoempresa = o.codigoempresa 
                and t.codigoestab = o.codigoestab 
                and t.classiforgan = o.classiforgan
            where
                compet = date('01.' ||date_part('month', date(current_date - interval'1 month')) || '.' || date_part('year', date(current_date - interval'1 month')))
                and t.codigoempresa in {empresas} 
                and t.gpsorigem in (1,3,9,5)
            group by
                1,3,4,5,6,7
            order by
                1,4,2;
        '''
        return sql
    
    @staticmethod
    def getSqlSelectHonorarios131FullFuncionarios():
        sql = '''
            select
                h.codigoempresa empresa, 
                count(h.codigofunccontr) numero, 
                upper(descrorgan) centro_custo, 
                fl.codigoestab filial, 
                'FOLHA' tipo,
                extract(month from compet)||'/'||extract(year from compet) compet,
                case fc.codigotipocontr
                when 2 then 'DIRETOR/PRÓ-LABORE'
                when 5 then 'ESTAGIARIO'
                when 7 then 'APRENDIZ'
                else 'FOLHA'
                end tipocontrato
            from
                histcalculomensal h
            join
                calculoevento ce on
                h.codigoempresa = ce.codigoempresa 
                and h.codigofunccontr = ce.codigofunccontr 
                and h.codigopercalculo = ce.codigopercalculo
            join
                funccontrato fc on
                h.codigoempresa = fc.codigoempresa 
                and h.codigofunccontr = fc.codigofunccontr
            join
                funclocal fl on
                h.codigoempresa = fl.codigoempresa
                and h.codigofunccontr = fl.codigofunccontr 
                and h.datalocal = fl.datatransf
            join
                organograma o on
                fl.codigoempresa = o.codigoempresa
                and fl.codigoestab = o.codigoestab
                and fl.classiforgan = o.classiforgan
            join
                periodocalculo p on
                p.codigoempresa = h.codigoempresa 
                and h.codigopercalculo = p.codigopercalculo 
            where
                p.compet = date('01.' ||date_part('month', date(current_date - interval'1 month')) || '.' || date_part('year', date(current_date - interval'1 month')))
		        and (fc.datatransfemp is null or fc.datatransfemp <= p.datafinalfolha)
                and ((codigotipocontr <> 5 and codigoevento = 5021) or (codigotipocontr = 5 and codigoevento = 5022)) 
                and p.codigotipocalc = 1
            group by
                1,3,4,6,7
            union
            select
                t.codigoempresa, 
                count(codigoterc), 
                upper(descrorgan) , 
                t.codigoestab, 
                case gpsorigem
                    when 5 then 'MEI'
                    else 'AUTONOMO'
                end,
                extract(month from compet)||'/'||extract(year from compet),
                'TERCEIRO' tipocontrato
            from
                terceiropgto t
            join
                organograma o on
                t.codigoempresa = o.codigoempresa 
                and t.codigoestab = o.codigoestab 
                and t.classiforgan = o.classiforgan
            where
                compet = date('01.' ||date_part('month', date(current_date - interval'1 month')) || '.' || date_part('year', date(current_date - interval'1 month')))
                and t.gpsorigem in (1,3,9,5)
            group by
                1,3,4,5,6,7
            order by
                1,4,2;
        '''
        return sql