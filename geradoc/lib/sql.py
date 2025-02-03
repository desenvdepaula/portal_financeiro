class InadimplenciaSqls:
    db_table = 'CONTARECEBER'

    def get_inadimplentes(self):
        sql = """
            with faturado as (
                select
                    sum(s.valorliquido) total,
                    'FATURADO' situacao,
                    (date(current_date - interval'1 month') - extract(day from date(current_date - interval'1 month'))::int) periodo
                from 
                    serviconota s
                where 
                    s.seriens = 'F'
                    and s.canceladans = '0'
                    and s.dataemissaons between (date(current_date - interval'2 months') - extract(day from current_date)::int+1) and (date(current_date - interval'1 month') - extract(day from date(current_date - interval'1 month'))::int)
            ),
            aberto as (
                select 
                    sum(cr.valorcr) total,
                    'ABERTO' situacao,
                    (date(current_date - interval'2 months') - extract(day from current_date)::int+1) periodo
                from 
                    contareceber cr 
                left join
                    contarecebida cd on
                    cr.codigoescrit = cd.codigoescrit
                    and cr.numerodctocr = cd.numerodctocr
                where 
                    cr.codigoescrit in (9501, 9502, 9505, 9567, 9575)
                    and cr.dataemissaocr between (date(current_date - interval'2 months') - extract(day from current_date)::int+1) and (date(current_date - interval'1 month') - extract(day from date(current_date - interval'1 month'))::int)
                    and statuscr = 1
                    and cr.datavctocr <= (current_date - extract(day from current_date)::int)
                    and (cr.numerodctocr not like 'X%' or cd.numerodctocr not like 'X%')
            ),
            rec_atrasado as (
                select 
                    sum(cr.valorcr) total,
                    'RECEB. APOS PRAZO' situacao,
                    (current_date - extract(day from current_date)::int) periodo
                from 
                    contareceber cr 
                left join
                    contarecebida cd on
                    cr.codigoescrit = cd.codigoescrit
                    and cr.numerodctocr = cd.numerodctocr
                where 
                    cr.codigoescrit in (9501, 9502, 9505, 9567, 9575)
                    and cr.dataemissaocr between (date(current_date - interval'2 months') - extract(day from current_date)::int+1) and (date(current_date - interval'1 month') - extract(day from date(current_date - interval'1 month'))::int)
                    and statuscr = 3
                    and cd.datarctocr > (current_date - extract(day from current_date)::int)
                    and cr.datavctocr <= (current_date - extract(day from current_date)::int)
                    and (cr.numerodctocr not like 'X%' or cd.numerodctocr not like 'X%')
            )
            select 
                total,
                situacao,
                periodo
            from 
                rec_atrasado
            union 
            select 
                total,
                situacao,
                periodo
            from 
                aberto
            union 	
            select 
                total,
                situacao,
                periodo
            from 
                faturado
        """
        return sql
    
    def get_detalhamento(self, data):
        sql = f"""
            select
                cr.valorcr,
                cr.codigoescrit,
                cr.codigocliente,
                cr.numerons,
                'ABERTO' situacao,
                (date(date('{data}') - interval'2 months') - extract(day from date('{data}'))::int+1) periodo
            from 
                contareceber cr 
            left join
                contarecebida cd on
                cr.codigoescrit = cd.codigoescrit
                and cr.numerodctocr = cd.numerodctocr
            where 
                cr.codigoescrit in (9501, 9502, 9505, 9567, 9575)
                and cr.dataemissaocr between (date(date('{data}') - interval'2 months') - extract(day from date('{data}'))::int+1) and (date(date('{data}') - interval'1 month') - extract(day from date(date('{data}') - interval'1 month'))::int)
                and statuscr = 1
                and cr.datavctocr <= (date('{data}') - extract(day from date('{data}'))::int)
                and (cr.numerodctocr not like 'X%' or cd.numerodctocr not like 'X%')
        """
        return sql