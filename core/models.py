from django.db import models

class LogPID(models.Model):
    execucao = models.CharField(max_length=100)
    cd_empresa = models.CharField(max_length=10)
    descricao = models.TextField(blank=True, null=True, default='NULL')
    aplication = models.CharField(max_length=255)
    usuario = models.CharField(max_length=100)

    class Meta:
        db_table = 'log'
