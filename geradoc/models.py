from django.db import models

class Inadimplencia(models.Model):
    vl_pagas_mes_seguinte = models.FloatField()
    vl_notas_aberto = models.FloatField()
    vl_faturado_mes_anterior = models.FloatField()
    vl_inadimplente = models.FloatField()
    percent_inadimplente = models.FloatField()
    competencia = models.DateField()
    data_elaboracao = models.DateField(auto_now_add=True)
    dt_nota_fiscal1 = models.DateField(null=True)
    dt_nota_fiscal2 = models.DateField(null=True)
    observacoes = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)