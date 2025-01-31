class BoletosSQL:
    
    @staticmethod
    def sqlCodigoEmpresa(cd_empresa):
        return f""" SELECT CODIGOPESSOAFIN,CODIGOEMPRESA,CODIGOESTAB FROM PESSOAFINANCEIRO WHERE CODIGOPESSOAFIN = {cd_empresa} """
    
class SQLSNFManual:
    
    @staticmethod
    def get_inserts_manual(escritorio,insert,codigo,data, empresas):
        booll = False
        if len(empresas) > 1:
            booll = True
            empresas = tuple(empresas)

        sql = f"""
            SELECT
                {insert} AS CODIGOESCRIT,
                M.codigocliente,
                K.CODIGOSERVICOESCRIT+{codigo} AS CODIGOSERVICOESCRIT,
                L.DATARCTOCR AS DATASERVVAR,
                K.SEQSERVNOTAITEM AS SEQSERVVAR,
                NULL AS SERIENS,
                NULL AS NUMERONS,
                NULL AS SEQSERVNOTAITEM,
                ('1') AS QTDADESERVVAR,
                ('1') AS VALORUNITSERVVAR,
                K.VALORTOTALSERVNOTAITEM AS VALORTOTALSERVVAR,
                NULL AS OBSERVSERVVAR,
                NULL AS SITANTECIPACAO,
                NULL AS SEQLCTO,
                ('3') AS CODIGOUSUARIO,
                L.DATARCTOCR AS DATAHORALCTO,
                ('3') AS ORIGEMDADO,
                NULL AS CHAVEPGTOANTECIP,
                NULL AS VALORANTERIORUNITSERVVAR,
                NULL AS SEQUENCIACAIXA,
                NULL AS CHAVEORIGEM
            FROM
                contarecebida L
            JOIN serviconota M 
            ON
                L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS)
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-1')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-2')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-3')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-4')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-5')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-6')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-7')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-8')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-9')
                OR L.NUMERODCTOCR =(M.SERIENS || '' || M.NUMERONS || '' || '-10')
            JOIN SERVICONOTAITEM K
            ON
                K.CODIGOESCRIT = M.CODIGOESCRIT
                AND K.SERIENS = M.SERIENS
                AND K.NUMERONS = M.NUMERONS
            WHERE
                L.codigoescrit = {escritorio}
                AND M.codigoescrit = {escritorio}
                AND L.DATARCTOCR = '{data}'
                AND L.CODIGOCAIXACONTA IN (14, 77)
                AND M.CODIGOCLIENTE {'IN' if booll else '='} {empresas if booll else empresas[0]}
            ORDER BY
                1,
                2,
                3,
                4
        """
        return sql

class SQLSNotasAntecipadas:
    
    @staticmethod
    def sqlNotasAntecipadas(servico, origem, destino, notas):
        sql = f"""
            insert into servicovariavel
            select
                {destino} codigoescrit,
                n.codigocliente,
                i.codigoservicoescrit+{servico} codigoservicoescrit,
                n.dataemissaons dataemissaons,
                i.seqservnotaitem,
                null::varchar(4) serie,
                null::int numero,
                null::int seq,
                i.qtdadeservnotaitem,
                i.valorunitservnotaitem,
                (i.qtdadeservnotaitem*i.valorunitservnotaitem) valortotal,
                i.obsservnotaitem,
                null::int sitantecipacao,
                null::int seqlcto,
                492 codigousuario,
                now() datahoralcto,
                3 origemdado,
                null::varchar(16) antecipacao,
                null::int valorant,
                null::int seqcaixa,
                null::varchar(20) chaveorigem
            from
                serviconota n
            join
                serviconotaitem i on
                n.codigoescrit = i.codigoescrit 
                and n.seriens = i.seriens 
                and n.numerons = i.numerons 
            where
                n.codigoescrit =  {origem}
                and n.seriens = 'F'    
                and n.numerons in {notas}
        """
        return sql

class SQLSNFRetorno:

    def get_inserts(self, escritorio,insert,codigo,servico,data, empresas):
        sql = """
            select
                {0} as codigoescrit,
                m.codigocliente,
                k.codigoservicoescrit+{1} as codigoservicoescrit,
                l.datarctocr as dataservvar,
                k.seqservnotaitem as seqservvar,
                null as seriens,
                null::int as numerons,
                null::int as seqservnotaitem,
                1 as qtdadeservvar,
                k.valortotalservnotaitem as valorunitservvar,
                k.valortotalservnotaitem as valortotalservvar,
                l.numerodctocr as observservvar,
                null::int as sitantecipacao,
                null::int as seqlcto,
                492 as codigousuario,
                l.datarctocr as datahoralcto,
                3 as origemdado,
                null as chavepgtoantecip,
                null::numeric(16,2) as valoranteriorunitservvar,
                null::int as sequenciacaixa,
                null as chaveorigem
            from
                contarecebida l
            join
                serviconota m on
                l.numerodctocr =(m.seriens || '' || m.numerons)
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-1')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-2')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-3')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-4')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-5')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-6')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-7')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-8')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-9')
                or l.numerodctocr =(m.seriens || '' || m.numerons || '' || '-10')
            join
                serviconotaitem k on
                k.codigoescrit = m.codigoescrit
                and k.seriens = m.seriens
                and k.numerons = m.numerons
            where
                l.codigoescrit = {2}
                and m.codigoescrit = {2}
                and l.datarctocr = '{4}'
                and l.codigocaixaconta = {3}
                and m.codigocliente not in {5}
            order by
                1,2,3,4
        """.format(insert,codigo,escritorio,servico,data, empresas)
        return sql

    def verificar(self, escritorio,cliente,servico,data):
        sql = """
            select
                codigoescrit,
                codigocliente,
                codigoservicoescrit,
                dataservvar,
                observservvar,
                seqservvar
            from
                servicovariavel
            where
                codigoescrit = {0}
                and codigocliente = {1}
                and codigoservicoescrit = {2}
                and dataservvar = '{3}'
        """.format(escritorio,cliente,servico,data)
        return sql

    def codigos(self, codigo):
        sql = """
            select 
                codigoservicoescrit 
            from 
                servicoescrit
            where
                codigoservicoescrit = {0}
        """.format(codigo)
        return sql

