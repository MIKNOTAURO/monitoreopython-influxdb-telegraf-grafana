# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Empresa(models.Model):
    slug = models.SlugField(unique=True)
    nombre = models.CharField(max_length=80, unique=True)


class GrafanaData(models.Model):
    token_admin = models.CharField(max_length=100,  blank=True)
    token_viewer = models.CharField(max_length=100,  blank=True)
    empresa = models.ForeignKey(Empresa, related_name='empresa_grafana')
    id_org= models.IntegerField(null=True)


class GrafanaDashBoards(models.Model):
    uuid_dashboard = models.CharField(max_length=80, unique=True, blank=True)
    id_dashboard = models.IntegerField(null=True),
    link = models.CharField(max_length=150, unique=True, blank=True)
    title = models.CharField(max_length=80, blank=True)
    version = models.IntegerField(blank=True)
    empresa = models.ForeignKey(Empresa, related_name='_dashboard', null=True )