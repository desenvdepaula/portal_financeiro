from django.db import models

class RegrasHonorario(models.Model):
    # Dados Da Empresa
    cnpj_cpf = models.CharField(primary_key=True, max_length=28, unique=True)
    cd_empresa = models.CharField(max_length=6)
    cd_filial = models.CharField(max_length=2)
    razao_social = models.CharField(max_length=255)
    
    #REGRAS
    have_rule = models.BooleanField(default=True)
    calcular = models.BooleanField(default=True, null=True)
    somar_filiais = models.BooleanField(default=False, null=True)
    limite = models.IntegerField(default=0)
    valor = models.FloatField(default=0)
    
    #OBSERVACOES
    observacoes = models.TextField(blank=True, null=True)
    history = models.CharField(max_length=255, null=True, default=None)
