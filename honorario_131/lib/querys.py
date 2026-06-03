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
                end tipocontrato,
                es.inscrfederal
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
                estab es on
                fl.codigoempresa = es.codigoempresa
                and fl.codigoestab = es.codigoestab
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
                1,3,4,5,6
            union
            select
                t.codigoempresa,
                count(codigoterc),
                t.codigoestab,
                extract(month from compet)|| '/' || extract(year from compet),
                'TERCEIRO' tipocontrato,
                es.inscrfederal
            from
                terceiropgto t
            join
                organograma o on
                t.codigoempresa = o.codigoempresa
                and t.codigoestab = o.codigoestab
                and t.classiforgan = o.classiforgan
            join 
                estab es on
                t.codigoempresa = es.codigoempresa
                and t.codigoestab = es.codigoestab
            where
                compet = '{compet}' 
                and t.codigoempresa in {empresa}
                and t.gpsorigem in (1, 3, 9, 5)
            group by
                1,3,4,5,6
            order by
                1,4,2;
        '''
        return sql