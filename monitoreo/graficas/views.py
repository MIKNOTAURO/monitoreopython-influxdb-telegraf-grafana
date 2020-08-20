# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from influxdb import InfluxDBClient

from django.shortcuts import render
from dateutil import parser
from dateutil.tz import tzutc
from plotly.offline import plot
from plotly.graph_objs import Scatter
from graficas.forms_graficas.graficas_forms import GraficasForm
from plotly.graph_objs import Layout

def info_datos_server(request):
    form = GraficasForm()
    tiempo = ""
    if request.method == 'POST':
        form = GraficasForm(request.POST)
        tiempo = form.data.get('tiempo')
        rango = form.data.get('rango')
        if rango is None:
            if tiempo in ['1h', '3h']:
                rango = '10m'
            elif tiempo in ['6h', '12h', '24h']:
                rango = '1h'
            elif tiempo in ['2d', '7d', '30d']:
                rango = '1d'
            else:
                rango = '1m'
            form = GraficasForm(initial={'tiempo': tiempo, 'rango':rango})
        client = InfluxDBClient('3.128.224.155', 8086, 'root', 'root', 'telegraf')
        result = client.query('SELECT mean("used") FROM "mem" WHERE time >= now() - '+ tiempo +' GROUP BY time('+ rango +') fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - '+ tiempo +' GROUP BY time('+ rango +') fill(null)')
    else:
        client = InfluxDBClient('3.128.224.155', 8086, 'root', 'root', 'telegraf')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
    x_data = []
    y_data = []
    for response in result:
        for registro in response:
            if registro['mean']:
                memoria_usada = float(registro['mean'])
            else:
                memoria_usada = None
            hora = parser.parse(registro['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            x_data.append(hora_final)
            y_data.append(memoria_usada)
    x_data_cpu = []
    y_data_cpu = []

    for response_cpu in result_cpu:
        for registro_cpu in response_cpu:
            if registro_cpu['mean']:
                memoria_usada = float(registro_cpu['mean'])
            else:
                memoria_usada = None
            hora = parser.parse(registro_cpu['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            x_data_cpu.append(hora_final)
            y_data_cpu.append(memoria_usada)

    plot_div = plot([Scatter(x=x_data, y=y_data,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='green')],
                    output_type='div')

    plot_div_cpu = plot([Scatter(x=x_data_cpu, y=y_data_cpu,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='red')],
                    output_type='div')

    return render(request, 'dashboard.html', {'plot_div': plot_div, 'form': form, 'plot_div_cpu': plot_div_cpu})