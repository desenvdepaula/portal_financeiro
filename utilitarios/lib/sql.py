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
                AND L.CODIGOCAIXACONTA = 14
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
    def sqlNotasAntecipadas(servico, origem, destino, notas, codigo_usuario):
        sql = f"""
            INSERT INTO SERVICOVARIAVEL
            SELECT
                {destino} CODIGOESCRIT,
                N.CODIGOCLIENTE,
                I.CODIGOSERVICOESCRIT+{servico} CODIGOSERVICOESCRIT,
                N.DATAEMISSAONS DATAEMISSAONS,
                I.SEQSERVNOTAITEM,
                NULL SERIE,
                NULL NUMERO,
                NULL SEQ,
                I.QTDADESERVNOTAITEM,
                I.VALORUNITSERVNOTAITEM,
                I.QTDADESERVNOTAITEM*I.VALORUNITSERVNOTAITEM VALORTOTAL,
                I.OBSSERVNOTAITEM,
                NULL SITANTECIPACAO,
                NULL SEQLCTO,
                {codigo_usuario} CODIGOUSUARIO,
                CAST('NOW' AS TIMESTAMP) DATAHORALCTO,
                3 ORIGEMDADO,
                NULL ANTECIPACAO,
                NULL VALORANT,
                NULL SEQCAIXA,
                NULL CHAVEORIGEM
            FROM
                SERVICONOTA N
            JOIN
                SERVICONOTAITEM I ON
                N.CODIGOESCRIT = I.CODIGOESCRIT AND
                N.SERIENS = I.SERIENS AND
                N.NUMERONS = I.NUMERONS 
            WHERE
                N.CODIGOESCRIT = {origem}
                AND N.SERIENS = 'F'
                AND N.NUMERONS IN {notas}
        """
        return sql

class SQLSNFRetorno:

    def get_inserts(self, escritorio,insert,codigo,servico,data, empresas):
        sql = """
            SELECT
                {0} AS CODIGOESCRIT,
                M.codigocliente,
                K.CODIGOSERVICOESCRIT+{1} AS CODIGOSERVICOESCRIT,
                L.DATARCTOCR AS DATASERVVAR,
                K.SEQSERVNOTAITEM AS SEQSERVVAR,
                'NULL' AS SERIENS,
                'NULL' AS NUMERONS,
                'NULL' AS SEQSERVNOTAITEM,
                ('1') AS QTDADESERVVAR,
                K.VALORTOTALSERVNOTAITEM AS VALORUNITSERVVAR,
                K.VALORTOTALSERVNOTAITEM AS VALORTOTALSERVVAR,
                L.NUMERODCTOCR AS OBSERVSERVVAR,
                'NULL' AS SITANTECIPACAO,
                'NULL' AS SEQLCTO,
                0 AS CODIGOUSUARIO,
                L.DATARCTOCR AS DATAHORALCTO,
                ('3') AS ORIGEMDADO,
                'NULL' AS CHAVEPGTOANTECIP,
                'NULL' AS VALORANTERIORUNITSERVVAR,
                'NULL' AS SEQUENCIACAIXA,
                'NULL' AS CHAVEORIGEM
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
                L.codigoescrit = {2}
                AND M.codigoescrit = {2}
                AND L.DATARCTOCR = '{4}'
                AND L.CODIGOCAIXACONTA = {3}
                AND M.codigocliente NOT IN {5}
            ORDER BY
                1,
                2,
                3,
                4
        """.format(insert,codigo,escritorio,servico,data, empresas)
        return sql

    def verificar(self, escritorio,cliente,servico,data):
        sql = """
            SELECT
                CODIGOESCRIT,
                CODIGOCLIENTE,
                CODIGOSERVICOESCRIT,
                DATASERVVAR,
                OBSERVSERVVAR,
                SEQSERVVAR
            FROM
                SERVICOVARIAVEL
            WHERE
                CODIGOESCRIT = {0}
                AND CODIGOCLIENTE = {1}
                AND CODIGOSERVICOESCRIT = {2}
                AND DATASERVVAR = '{3}'
        """.format(escritorio,cliente,servico,data)
        return sql

    def codigos(self, codigo):
        sql = """
            SELECT 
                CODIGOSERVICOESCRIT 
            FROM 
                SERVICOESCRIT
            WHERE
                CODIGOSERVICOESCRIT = {0}
        """.format(codigo)
        return sql

