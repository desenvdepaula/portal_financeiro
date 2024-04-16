from django.db import models
from relatorios.models import ClassificacaoServicos

class DepartamentosControle(models.Model):
    nome_departamento = models.CharField(max_length=255, unique=True)

class Servico(models.Model):
    cd_servico = models.CharField(max_length=7, primary_key=True)
    name_servico = models.CharField(max_length=255)
    tipo_servico = models.ForeignKey(ClassificacaoServicos, on_delete=models.SET(""), blank=True, null=True)
    departamentos = models.ManyToManyField(DepartamentosControle, related_name="departamentos")
    considera_custo = models.BooleanField(default=False)
    classificacao = models.CharField(max_length=255, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

class OrdemServico(models.Model):
    departamento = models.CharField(max_length=255)
    cd_servico = models.CharField(max_length=10)
    servico = models.CharField(max_length=255)
    ds_servico = models.CharField(max_length=47)
    observacoes_servico = models.TextField(blank=True, null=True)
    cd_empresa = models.CharField(max_length=6)
    nome_empresa = models.CharField(max_length=255)
    data_realizado = models.DateField()
    data_cobranca = models.DateField()
    quantidade = models.IntegerField(default=0)
    hora_trabalho = models.CharField(max_length=10)
    valor = models.FloatField()
    autorizado_pelo_cliente = models.BooleanField(default=False)
    type_solicitacao = models.CharField(max_length=30)
    solicitado = models.CharField(max_length=255)
    executado = models.CharField(max_length=255)
    criador_os = models.CharField(max_length=255)
    debitar = models.BooleanField(default=False)
    arquivado = models.BooleanField(default=False)
    ordem_debitada_id = models.IntegerField(blank=True, null=True)
