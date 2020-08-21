# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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

        result_net = client.query(
            'SELECT mean("bytes_recv") FROM "net" WHERE time >= now() - '+ tiempo +' GROUP BY time('+ rango +') fill(null)')

    else:
        client = InfluxDBClient('3.128.224.155', 8086, 'root', 'root', 'telegraf')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_net = client.query(
            'SELECT mean("bytes_recv") FROM "net" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
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

    x_data_net = []
    y_data_net = []

    for response_net in result_net:
        for registro_net in response_net:
            if registro_net['mean']:
                bytes_recv = float(registro_net['mean'])
            else:
                bytes_recv = None
            hora = parser.parse(registro_net['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            x_data_net.append(hora_final)
            y_data_net.append(bytes_recv)

    plot_div = plot([Scatter(x=x_data, y=y_data,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='green')],
                    output_type='div')

    plot_div_cpu = plot([Scatter(x=x_data_cpu, y=y_data_cpu,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='red')],
                    output_type='div')
    plot_div_net = plot([Scatter(x=x_data_net, y=y_data_net,
                                 mode='lines', name='test',
                                 opacity=0.8, marker_color='blue')],
                        output_type='div')

    return render(request, 'dashboard.html', {'plot_div': plot_div, 'form': form, 'plot_div_cpu': plot_div_cpu,
                                              'plot_div_net': plot_div_net})

def info_datos_server_google(request):
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
            form = GraficasForm(initial={'tiempo': tiempo, 'rango': rango})
        client = InfluxDBClient('3.128.224.155', 8086, 'root', 'root', 'telegraf')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - ' + tiempo + ' GROUP BY time(' + rango + ') fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - ' + tiempo + ' GROUP BY time(' + rango + ') fill(null)')

        result_net = client.query(
            'SELECT mean("bytes_recv") FROM "net" WHERE time >= now() - ' + tiempo + ' GROUP BY time(' + rango + ') fill(null)')

    else:
        client = InfluxDBClient('3.128.224.155', 8086, 'root', 'root', 'telegraf')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_net = client.query(
            'SELECT mean("bytes_recv") FROM "net" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')

    data_mem = [['Tiempo', 'Mb']]
    mem_min = 0
    for response in result:
        for registro in response:
            if registro['mean']:
                memoria_usada = float(registro['mean']) / (1000000)
                if mem_min == 0:
                    mem_min = memoria_usada
                if mem_min > memoria_usada:
                    mem_min = memoria_usada
            else:
                memoria_usada = None
            hora = parser.parse(registro['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            data_mem.append([hora_final, memoria_usada])

    data_cpu = [['Tiempo', 'CPU']]
    cpu_min = 0
    for response_cpu in result_cpu:
        for registro_cpu in response_cpu:
            if registro_cpu['mean']:
                cpu = float(registro_cpu['mean']) / (1024)
                if cpu_min == 0:
                    cpu_min = cpu
                if cpu_min > cpu:
                    cpu_min = cpu
            else:
                cpu = None
            hora = parser.parse(registro_cpu['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            data_cpu.append([hora_final, cpu])

    data_net = [['Tiempo', 'Bytes']]
    net_min = 0
    for response_net in result_net:
        for registro_net in response_net:
            if registro_net['mean']:
                bytes_recv = float(registro_net['mean'])/(1000000)
                if net_min == 0:
                    net_min = bytes_recv
                if net_min > bytes_recv:
                    net_min = bytes_recv
            else:
                bytes_recv = None
            hora = parser.parse(registro_net['time'])
            hora_final = hora.strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.strftime("%d/%m -%H:%M:%S")
            data_net.append([hora_final, bytes_recv])

    data_mem = json.dumps(data_mem)
    data_net = json.dumps(data_net)
    data_cpu = json.dumps(data_cpu)
    # mem_min = mem_min - 0.05
    # net_min = net_min - 0.05
    # cpu_min = cpu_min -1
    return render(request, 'dashboard_google.html', {'form': form, 'data_mem': data_mem, 'mem_min': mem_min,
                                                     'data_net': data_net, 'net_min': net_min, 'data_cpu': data_cpu,
                                                     'cpu_min': cpu_min})