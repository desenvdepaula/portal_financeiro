from django.db import models

class RegrasHonorario(models.Model):
    cd_financeiro = models.CharField(max_length=100, primary_key=True, unique=True)
    cd_empresa = models.CharField(max_length=6)
    cd_filial = models.CharField(max_length=2)
    razao_social = models.CharField(max_length=255)
    calcular = models.BooleanField(default=True)
    somar_filiais = models.BooleanField(default=False)
    limite = models.IntegerField(default=0)
    valor = models.FloatField()
