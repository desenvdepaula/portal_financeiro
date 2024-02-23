class RelatorioFaturamentoServicoSqls:
    
    def __init__(self, inicio, fim, codigos_servicos):
        self.inicio = inicio
        self.fim = fim
        self.codigos_servicos = list(codigos_servicos)

    def get_data(self):
        filter_sql = self.filtering()
        sql = f"""
            SELECT
                SN.CODIGOCLIENTE ,
                P.CODIGOEMPRESA,
                P.CODIGOESTAB,
                P.NOME,
                CAST('01.'||EXTRACT(MONTH FROM SN.DATAEMISSAONS)||'.'||EXTRACT(YEAR FROM SN.DATAEMISSAONS) AS DATE) COMPET,
                CAST(SNI.CODIGOSERVICOESCRIT AS VARCHAR(10))||CAST(' - ' AS VARCHAR(5))||CAST(SE.DESCRSERVICOESCRIT AS VARCHAR(3000)) "CÓDIGO SERVIÇO",
                SUM(SNI.VALORTOTALSERVNOTAITEM) VALOR
            FROM
                SERVICONOTA SN
            LEFT JOIN
                SERVICONOTAITEM SNI ON
                SN.CODIGOESCRIT = SNI.CODIGOESCRIT
                AND SN.SERIENS = SNI.SERIENS
                AND SN.NUMERONS = SNI.NUMERONS
            JOIN
                PESSOAFINANCEIRO P ON
                SN.CODIGOCLIENTE = P.CODIGOPESSOAFIN
            JOIN 
                SERVICOESCRIT SE ON
                SE.CODIGOSERVICOESCRIT = SNI.CODIGOSERVICOESCRIT
            WHERE
                SN.CODIGOESCRIT IN (9501,9502,9505,9567,9575)
                AND SN.SERIENS = 'F'
                AND SN.DATAEMISSAONS BETWEEN '{self.inicio}' AND '{self.fim}'
                {filter_sql}
            GROUP BY 1,2,3,4,5,6
            ORDER BY
                2
        """
        return sql
    
    def filtering(self):
        if not self.codigos_servicos:
            return ''
        elif len(self.codigos_servicos) == 1:
            return f"AND SNI.CODIGOSERVICOESCRIT IN ({self.codigos_servicos[0]})"
        else:
            codigos = tuple(self.codigos_servicos)
            return f"AND SNI.CODIGOSERVICOESCRIT IN {codigos}"