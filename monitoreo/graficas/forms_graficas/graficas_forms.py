#!
# -*- coding: utf-8 -*-
#

from django import forms


class GraficasForm(forms.Form):
    TIEMPO = (
        ('5m', 'Últimos 5 minutos'),
        ('15m', 'Ùltimos 15 minutos'),
        ('30m', 'Ùltimos 30 minutos'),
        ('1h', 'Ùltima 1 hora'),
        ('3h', 'Ùltimas 3 horas'),
        ('6h', 'Ùltimas 6 horas'),
        ('12h', 'Ùltimas 12 horas'),
        ('24h', 'Ùltimas 24 horas'),
        ('2d', 'Ùltimos 2 dias'),
        ('7d', 'Ùltimos 7 dias'),
        ('30d', 'Ùltimos 30 dias'),
    )
    RANGO = (
        ('10s', '10s'),
        ('1m', '1m'),
        ('5m', '5m'),
        ('10m', '10m'),
        ('15m', '15m'),
        ('1h', '1h'),
        ('1d', '1d'),
    )
    rango = forms.ChoiceField(choices=RANGO, label="Rango:", required=False, initial='1m')
    tiempo = forms.ChoiceField(choices=TIEMPO, label="Tiempo:", required=True, initial='15m')