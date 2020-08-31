# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from influxdb import InfluxDBClient
import requests

from django.shortcuts import render
from dateutil import parser
from dateutil.tz import tzutc
from plotly.offline import plot
from plotly.graph_objs import Scatter
from graficas.forms_graficas.graficas_forms import GraficasForm
from pytz import timezone
from plotly.graph_objs import Layout

from graficas.models import Empresa, GrafanaData, GrafanaDashBoards


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
        client = InfluxDBClient('3.131.109.207', 8086, 'root', 'root', 'telegraf_digitalocean')
        result = client.query('SELECT mean("used") FROM "mem" WHERE time >= now() - '+ tiempo +' GROUP BY time('+ rango +') fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - '+ tiempo +' GROUP BY time('+ rango +') fill(null)')

        result_net_speed = client.query(
            'SELECT moving_average(derivative(mean(bytes_recv), 1s), 30) *16  as "download bytes/sec",  moving_average(derivative(mean(bytes_sent), 1s), 30) *16 as '
            '"upload bytes/sec" FROM net WHERE time > now() - '+ tiempo +' GROUP BY time(15s)')
        result_net_used = client.query('SELECT non_negative_difference(mean("bytes_recv")) *2 FROM "net" '
                                       'WHERE time >= now() -' + tiempo + ' GROUP BY time(15s) fill(null)')
    else:
        client = InfluxDBClient('3.131.109.207', 8086, 'root', 'root', 'telegraf_digitalocean')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_net_speed = client.query(
            'SELECT moving_average(derivative(mean(bytes_recv), 1s), 30) *16 as "download bytes/sec", moving_average(derivative(mean(bytes_sent), 1s), 30) *16 as '
            '"upload bytes/sec" FROM net WHERE time > now() - 15m GROUP BY time(15s)')
        result_net_used = client.query('SELECT non_negative_difference(mean("bytes_recv")) *2 FROM "net" '
                                       'WHERE time >= now() - 15m GROUP BY time(15s) fill(null)')

    x_data = []
    y_data = []
    for response in result:
        for registro in response:
            if registro['mean']:
                memoria_usada = float(registro['mean'])
            else:
                memoria_usada = None
            hora = parser.parse(registro['time'])
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
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
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            x_data_cpu.append(hora_final)
            y_data_cpu.append(memoria_usada)

    x_data_net = []
    download_y_data_net = []
    upload_y_data_net = []

    for response_net in result_net_speed:
        for registro_net in response_net:
            if registro_net['download bytes/sec']:
                download_bytes = float(registro_net['download bytes/sec'])
                if download_bytes < 0:
                    download_bytes = 0.0
            else:
                download_bytes = None
            if registro_net['upload bytes/sec']:
                upload_bytes = float(registro_net['upload bytes/sec'])
                if upload_bytes < 0:
                    upload_bytes = 0.0
            else:
                upload_bytes = None
            hora = parser.parse(registro_net['time'])
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            x_data_net.append(hora_final)
            download_y_data_net.append(download_bytes)
            upload_y_data_net.append(upload_bytes)

    x_data_net_used = []
    y_data_net_used = []
    for response_net_used in result_net_used:
        for registro_net_used in response_net_used:
            if registro_net_used['non_negative_difference']:
                memoria_usada = float(registro_net_used['non_negative_difference'])
            else:
                memoria_usada = None
            hora = parser.parse(registro_net_used['time'])
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            x_data_net_used.append(hora_final)
            y_data_net_used.append(memoria_usada)

    plot_div = plot([Scatter(x=x_data, y=y_data,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='green')],
                    output_type='div')

    plot_div_cpu = plot([Scatter(x=x_data_cpu, y=y_data_cpu,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='red')],
                    output_type='div')

    plot_div_net = plot([Scatter(x=x_data_net, y=download_y_data_net,
                                 mode='lines', name='Download bytes/sec',
                                 opacity=0.9, marker_color='blue'), Scatter(x=x_data_net, y=upload_y_data_net,
                                 mode='lines', name='Upload bytes/sec',
                                 opacity=0.9, marker_color='red')],
                        output_type='div')

    plot_div_net_used = plot([Scatter(x=x_data_net_used, y=y_data_net_used,
                                 mode='lines', name='Bytes',
                                 opacity=0.8, marker_color='blue')],
                        output_type='div')

    return render(request, 'dashboard.html', {'plot_div': plot_div, 'form': form, 'plot_div_cpu': plot_div_cpu,
                                              'plot_div_net': plot_div_net, 'plot_div_net_used': plot_div_net_used})

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
        client = InfluxDBClient('3.131.109.207', 8086, 'root', 'root', 'telegraf_digitalocean')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - ' + tiempo + ' GROUP BY time(' + rango + ') fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - ' + tiempo + ' GROUP BY time(' + rango + ') fill(null)')

        result_net_speed = client.query(
            'SELECT moving_average(derivative(mean(bytes_recv), 1s), 30) *16  as "download bytes/sec",  moving_average(derivative(mean(bytes_sent), 1s), 30) *16 as '
            '"upload bytes/sec" FROM net WHERE time > now() - '+ tiempo +' GROUP BY time(15s)')

        result_net_used = client.query('SELECT non_negative_difference(mean("bytes_recv")) *2 FROM "net" '
                                       'WHERE time >= now() -'+ tiempo +' GROUP BY time(15s) fill(null)')

    else:
        client = InfluxDBClient('3.131.109.207', 8086, 'root', 'root', 'telegraf_digitalocean')
        result = client.query(
            'SELECT mean("used") FROM "mem" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_cpu = client.query(
            'SELECT mean("usage_system") FROM "cpu" WHERE time >= now() - 15m GROUP BY time(1m) fill(null)')
        result_net_speed = client.query(
            'SELECT moving_average(derivative(mean(bytes_recv), 1s), 30) *16 as "download bytes/sec", '
            'moving_average(derivative(mean(bytes_sent), 1s), 30) *16 as "upload bytes/sec" FROM net '
            'WHERE time > now() - 15m GROUP BY time(15s)')
        result_net_used = client.query('SELECT non_negative_difference(mean("bytes_recv")) *2 FROM "net" '
                                       'WHERE time >= now() - 15m GROUP BY time(15s) fill(null)')

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
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
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
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            data_cpu.append([hora_final, cpu])

    data_net = [['Tiempo', 'Download bps', 'Upload bps']]
    net_min = 0
    for response_net in result_net_speed:
        for registro_net in response_net:
            if registro_net['download bytes/sec']:
                download_bytes = float(registro_net['download bytes/sec'])/1000
                if download_bytes < 0 :
                    download_bytes = 0.0
                if net_min == 0:
                    net_min = download_bytes
                if net_min > download_bytes:
                    net_min = download_bytes
            else:
                download_bytes = None
            if registro_net['upload bytes/sec']:
                upload_bytes = float(registro_net['upload bytes/sec'])/1000
                if upload_bytes < 0:
                    upload_bytes = 0.0
                if net_min == 0:
                    net_min = upload_bytes
                if net_min > upload_bytes:
                    net_min = upload_bytes
            else:
                upload_bytes = None

            hora = parser.parse(registro_net['time'])
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            data_net.append([hora_final, download_bytes, upload_bytes])

    data_net_used = [['Tiempo', 'Download Kb']]
    net_min_used = 0
    for response_net_used in result_net_used:
        for registro_net_used in response_net_used:
            if registro_net_used['non_negative_difference']:
                memoria_usada = float(registro_net_used['non_negative_difference'])
                if net_min_used == 0:
                    net_min_used = memoria_usada
                if net_min_used > memoria_usada:
                    net_min_used = memoria_usada
            else:
                memoria_usada = None
            hora = parser.parse(registro_net_used['time'])
            hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%H:%M:%S")
            if tiempo in ['24h', '2d', '7d', '30d']:
                hora_final = hora.astimezone(timezone('America/Cancun')).strftime("%d/%m -%H:%M:%S")
            data_net_used.append([hora_final, memoria_usada])


    data_mem = json.dumps(data_mem)
    data_net = json.dumps(data_net)
    data_cpu = json.dumps(data_cpu)
    data_net_used = json.dumps(data_net_used)
    # mem_min = mem_min - 0.05
    # net_min = net_min - 0.05
    # cpu_min = cpu_min -1
    return render(request, 'dashboard_google.html', {'form': form, 'data_mem': data_mem, 'mem_min': mem_min,
                                                     'data_net': data_net, 'net_min': net_min, 'data_cpu': data_cpu,
                                                     'cpu_min': cpu_min, 'data_net_used': data_net_used,
                                                     'net_min_used': net_min_used})


def api_grafana(request):
    empresa = Empresa.objects.get(slug='fcetina')
    grafana_data = GrafanaData.objects.filter(empresa=empresa)
    if not grafana_data:
        grafana_data = crear_organizacion_grafana(empresa)
    else:
        grafana_data = grafana_data[0]
    grafana_dashboard = GrafanaDashBoards.objects.filter(empresa=empresa)
    if not grafana_dashboard:
        grafana_dashboard = crear_dashboard_grafana(empresa, grafana_data)
    else:
        grafana_dashboard = grafana_dashboard[0]
    token = grafana_data.token_viewer
    url = grafana_dashboard.link

    url = 'http://3.131.109.207'+url+'?kiosk=tv&var-servidor=InfluxDB&theme=light'
    print url
    return render(request, 'api_grafana.html', {'url': url, 'token': token})


def crear_organizacion_grafana(empresa):
    data_create_organization = {"name": empresa.slug}
    data_create_organization = json.dumps(data_create_organization)
    headers_post_create_origanization = {
        "Content-Type": "application/json",
    }
    errores = []
    response_create_organization = requests.post(url="http://admin:fcetina235@3.131.109.207/grafana/api/orgs",
                                                 data=data_create_organization,
                                                 headers=headers_post_create_origanization)
    if response_create_organization.status_code == 200:
        response = json.loads(response_create_organization.text)
        if response['orgId']:
            id_organizacion = int(response['orgId'])
            data_add_admin = {"loginOrEmail": "admin", "role": "Admin"}
            data_add_admin = json.dumps(data_add_admin)
            response_add_admin = requests.post(url='http://admin:fcetina235@3.131.109.207/grafana/api/orgs/'+ str(id_organizacion)+'/users',
                                               data=data_add_admin, headers=headers_post_create_origanization)
            if response_add_admin.status_code == 200 or response_add_admin.status_code == 409:
                response = json.loads(response_add_admin.text)
                response_switch = requests.post(url='http://admin:fcetina235@3.131.109.207/grafana/api/user/using/'+str(id_organizacion))
                data_key_admin = {"name": "keyadmin"+empresa.slug, "role": "Admin"}
                data_key_viewer = {"name": "keyviewer"+empresa.slug, "role": "Viewer"}
                data_key_admin = json.dumps(data_key_admin)
                data_key_viewer = json.dumps(data_key_viewer)
                response_key_admin = requests.post(url='http://admin:fcetina235@3.131.109.207/grafana/api/auth/keys',
                                                   data=data_key_admin, headers=headers_post_create_origanization)
                response_key_viewer = requests.post(url='http://admin:fcetina235@3.131.109.207/grafana/api/auth/keys',
                                                    data=data_key_viewer, headers=headers_post_create_origanization)
                response_key_admin = json.loads(response_key_admin.text)
                response_key_viewer = json.loads(response_key_viewer.text)
                key_admin = response_key_admin['key']
                key_viewer = response_key_viewer['key']

                grafana_data = GrafanaData()
                grafana_data.id_org = id_organizacion
                grafana_data.token_admin = key_admin
                grafana_data.token_viewer = key_viewer
                grafana_data.empresa = empresa
                grafana_data.save()

                return grafana_data

        else:
            errores.appen(response['message'])
            return None

JSON_PANEL_BANDWIDTH = {
  "aliasColors": {
    "net.moving_average_1": "dark-red"
  },
  "bars": False,
  "dashLength": 10,
  "dashes": False,
  "fieldConfig": {
    "defaults": {
      "custom": {}
    },
    "overrides": []
  },
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 8,
    "w": 12,
    "x": 12,
    "y": 0
  },
  "hiddenSeries": False,
  "id": 6,
  "legend": {
    "avg": False,
    "current": False,
    "max": False,
    "min": False,
    "show": True,
    "total": False,
    "values": False
  },
  "lines": True,
  "linewidth": 1,
  "NonePointMode": "null",
  "percentage": False,
  "pluginVersion": "",
  "pointradius": 2,
  "points": False,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": False,
  "steppedLine": False,
  "targets": [
    {
      "groupBy": [
        {
          "params": [
            "15s"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "measurement": "net",
      "orderByTime": "ASC",
      "policy": "default",
      "query": "SELECT moving_average(non_negative_derivative(mean(\"bytes_recv\"), 1s), 30) *16 as \"download bytes/sec\", moving_average(non_negative_derivative(mean(\"bytes_sent\"), 1s), 30) *16 as \"upload bytes/sec\" FROM \"net\" WHERE $timeFilter GROUP BY time(15s) fill(null)",
      "rawQuery": True,
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "bytes_recv"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          },
          {
            "params": [
              "1s"
            ],
            "type": "non_negative_derivative"
          },
          {
            "params": [
              "30"
            ],
            "type": "moving_average"
          },
          {
            "params": [
              "*16"
            ],
            "type": "math"
          }
        ],
        [
          {
            "params": [
              "bytes_sent"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          },
          {
            "params": [
              "1s"
            ],
            "type": "non_negative_derivative"
          },
          {
            "params": [
              "30"
            ],
            "type": "moving_average"
          },
          {
            "params": [
              "*16"
            ],
            "type": "math"
          }
        ]
      ],
      "tags": []
    }
  ],
  "thresholds": [],
  "timeFrom": None,
  "timeRegions": [],
  "timeShift": None,
  "title": "Public Bandwidth",
  "tooltip": {
    "shared": True,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": None,
    "mode": "time",
    "name": None,
    "show": True,
    "values": []
  },
  "yaxes": [
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    },
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    }
  ],
  "yaxis": {
    "align": False,
    "alignLevel": None
  },
  "datasource": None
}

JSON_PANEL_RAM = {
  "aliasColors": {},
  "bars": False,
  "dashLength": 10,
  "dashes": False,
  "fieldConfig": {
    "InfluxDB": {
      "custom": {}
    },
    "overrides": []
  },
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 8,
    "w": 12,
    "x": 0,
    "y": 0
  },
  "hiddenSeries": False,
  "id": 4,
  "legend": {
    "avg": False,
    "current": False,
    "max": False,
    "min": False,
    "show": True,
    "total": False,
    "values": False
  },
  "lines": True,
  "linewidth": 1,
  "NonePointMode": "null",
  "percentage": False,
  "pluginVersion": "7.1.3",
  "pointradius": 2,
  "points": False,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": False,
  "steppedLine": False,
  "targets": [
    {
      "groupBy": [
        {
          "params": [
            "1m"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "measurement": "mem",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "used"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": []
    }
  ],
  "thresholds": [],
  "timeFrom": None,
  "timeRegions": [],
  "timeShift": None,
  "title": "Mem RAM",
  "tooltip": {
    "shared": True,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": None,
    "mode": "time",
    "name": None,
    "show": True,
    "values": []
  },
  "yaxes": [
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    },
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    }
  ],
  "yaxis": {
    "align": False,
    "alignLevel": None
  },
  "datasource": None
}

JSON_PANEL_CPU = {
  "aliasColors": {},
  "bars": False,
  "dashLength": 10,
  "dashes": False,
  "fieldConfig": {
    "defaults": {
      "custom": {}
    },
    "overrides": []
  },
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 9,
    "w": 12,
    "x": 0,
    "y": 8
  },
  "hiddenSeries": False,
  "id": 2,
  "legend": {
    "avg": False,
    "current": False,
    "max": False,
    "min": False,
    "show": True,
    "total": False,
    "values": False
  },
  "lines": True,
  "linewidth": 1,
  "NonePointMode": "null",
  "percentage": False,
  "pluginVersion": "7.1.3",
  "pointradius": 2,
  "points": False,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": False,
  "steppedLine": False,
  "targets": [
    {
      "groupBy": [
        {
          "params": [
            "1m"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "measurement": "cpu",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "usage_system"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          }
        ]
      ],
      "tags": []
    }
  ],
  "thresholds": [],
  "timeFrom": None,
  "timeRegions": [],
  "timeShift": None,
  "title": "CPU",
  "tooltip": {
    "shared": True,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": None,
    "mode": "time",
    "name": None,
    "show": True,
    "values": []
  },
  "yaxes": [
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    },
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    }
  ],
  "yaxis": {
    "align": False,
    "alignLevel": None
  },
  "datasource": None
}

JSON_PANEL_CONSUMO_NET = {
  "aliasColors": {},
  "bars": False,
  "dashLength": 10,
  "dashes": False,
  "fieldConfig": {
    "defaults": {
      "custom": {}
    },
    "overrides": []
  },
  "fill": 1,
  "fillGradient": 0,
  "gridPos": {
    "h": 8,
    "w": 12,
    "x": 12,
    "y": 8
  },
  "hiddenSeries": False,
  "id": 8,
  "legend": {
    "avg": False,
    "current": False,
    "max": False,
    "min": False,
    "show": True,
    "total": False,
    "values": False
  },
  "lines": True,
  "linewidth": 1,
  "NonePointMode": "null",
  "percentage": False,
  "pluginVersion": "7.1.3",
  "pointradius": 2,
  "points": False,
  "renderer": "flot",
  "seriesOverrides": [],
  "spaceLength": 10,
  "stack": False,
  "steppedLine": False,
  "targets": [
    {
      "groupBy": [
        {
          "params": [
            "1m"
          ],
          "type": "time"
        },
        {
          "params": [
            "null"
          ],
          "type": "fill"
        }
      ],
      "measurement": "net",
      "orderByTime": "ASC",
      "policy": "default",
      "refId": "A",
      "resultFormat": "time_series",
      "select": [
        [
          {
            "params": [
              "bytes_recv"
            ],
            "type": "field"
          },
          {
            "params": [],
            "type": "mean"
          },
          {
            "params": [],
            "type": "non_negative_difference"
          },
          {
            "params": [
              "*2"
            ],
            "type": "math"
          }
        ]
      ],
      "tags": []
    }
  ],
  "thresholds": [],
  "timeFrom": None,
  "timeRegions": [],
  "timeShift": None,
  "title": "Bytes Download",
  "tooltip": {
    "shared": True,
    "sort": 0,
    "value_type": "individual"
  },
  "type": "graph",
  "xaxis": {
    "buckets": None,
    "mode": "time",
    "name": None,
    "show": True,
    "values": []
  },
  "yaxes": [
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    },
    {
      "format": "short",
      "label": None,
      "logBase": 1,
      "max": None,
      "min": None,
      "show": True
    }
  ],
  "yaxis": {
    "align": False,
    "alignLevel": None
  },
  "datasource": None
}
def crear_dashboard_grafana(empresa, grafana_data):
    token_admin = grafana_data.token_admin
    authorization = 'Bearer ' + token_admin
    data_create_new_dashboard = {
          "dashboard": {
                "id": None,
                "uid": None,
                "title": "Server Status - "+ empresa.nombre,
                "tags": ["templated"],
                "timezone": "browser",
                "schemaVersion": 16,
                "version": 0,
                "refresh": "25s"
          },
          "folderId": 0,
          "overwrite": False
    }
    headers_grafana = {
        "Authorization": authorization,
        "Content-Type": "application/json",
    }
    data_create_new_dashboard = json.dumps(data_create_new_dashboard)

    response_create_dashboard = requests.post(url='http://3.131.109.207/grafana/api/dashboards/db',
                                              data=data_create_new_dashboard, headers=headers_grafana)
    if response_create_dashboard.status_code == 200:
        response = json.loads(response_create_dashboard.text)

        id_dashboard = response['id']
        uuid_dashboard = response['uid']
        version_dashboard = int(response['version'])
        url = response['url']
        data_create_panels = {
              "dashboard": {
                    "id": id_dashboard,
                    "panels": [JSON_PANEL_BANDWIDTH, JSON_PANEL_CPU, JSON_PANEL_CONSUMO_NET, JSON_PANEL_RAM],
                    "uid": uuid_dashboard,
                    "title": "Server Status - " + empresa.nombre,
                    "version": version_dashboard,
              }
        }
        data_create_panels = json.dumps(data_create_panels)
        data_db = {
            "name": "InfluxDB",
            "type": "influxdb",
            "typeLogoUrl": "public/app/plugins/datasource/influxdb/img/influxdb_logo.svg",
            "access": "proxy",
            "url": "http://localhost:8086",
            "password": "",
            "user": "",
            "database": "telegraf_digitalocean",
            "basicAuth": False,
            "isDefault": True,
            "jsonData": {},
            "readOnly": False
        }
        data_db = json.dumps(data_db)
        response_db = requests.post(url='http://3.131.109.207/grafana/grafana/api/datasources', data=data_db, headers=headers_grafana)
        response_create_panels = requests.post(url='http://3.131.109.207/grafana/api/dashboards/db',
                                               data=data_create_panels, headers=headers_grafana)
        if response_create_panels.status_code == 200:
            dashboard_grafana = GrafanaDashBoards()
            dashboard_grafana.uuid_dashboard = uuid_dashboard
            dashboard_grafana.id_dashboard = id_dashboard
            dashboard_grafana.link = url
            dashboard_grafana.title = "Server Status - "+ empresa.nombre
            dashboard_grafana.version = version_dashboard + 1
            dashboard_grafana.empresa = empresa
            dashboard_grafana.save()

            return dashboard_grafana
    else:
        return None