# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from graficas.models import Empresa, GrafanaData, GrafanaDashBoards


class EmpresaAdmin(admin.ModelAdmin):
    model = Empresa
    search_fields = ('nombre', 'slug')
    list_display = ('nombre',)
    prepopulated_fields = {"slug": ("nombre",)}


admin.site.register(Empresa, EmpresaAdmin)


class GrafanaDataAdmin(admin.ModelAdmin):
    model = GrafanaData
    search_fields = ('empresa', 'id')
    list_display = ('empresa',)
    raw_id_fields = ['empresa']


admin.site.register(GrafanaData, GrafanaDataAdmin)


class GrafanaDashBoardsAdmin(admin.ModelAdmin):
    model = GrafanaDashBoards
    search_fields = ('title', 'empresa')
    list_display = ('title', 'empresa',)
    raw_id_fields = ['empresa']


admin.site.register(GrafanaDashBoards, GrafanaDashBoardsAdmin)