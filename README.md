# Stats Grafana
Estadisticas de Servidor con Grafana, InfluxDB, Telegraft

Se usará Ubuntu 18.04 para el ejemplo

__1 Instalación y configuración de Influx DB__
1.1 Ubicate en el directorio donde deseas trabajar
    
    cd ~/Documentos/stats_test

1.2 Descarga y descomprime los archivos binarios necesarios para Grafana

    wget https://dl.influxdata.com/influxdb/releases/influxdb-1.8.1_linux_amd64.tar.gz
    tar xvfz influxdb-1.8.1_linux_amd64.tar.gz

1.3 Iniciar InfluxDB
    
    cd influxdb-1.8.1-1/usr/bin
    ./influxd
__2 Instalación y configuracion de telegraf__
    
Abrir nueva terminal *

2.1 Ubicate en el directorio donde deseas trabajar
    
    cd ~/Documentos/stats_test

2.2 Descarga y descomprime los archivos binarios necesarios para Grafana

    wget https://dl.influxdata.com/telegraf/releases/telegraf-1.15.2_linux_amd64.tar.gz
    tar xf telegraf-1.15.2_linux_amd64.tar.gz
    
2.3 Archivo de configuración
  Ingresamos al siguiente repositorio de los datos descomprimidos y creamos un archivo telefraf.conf, con lo siguientes comandos, donde suaremos los plugins input cpu, mem y disk y plugins output influxdb
    
    cd telegraf-1.15.2/usr/bin
    ./telegraf -sample-config -input-filter cpu:mem:disk:net -output-filter influxdb > telegraf.conf
 
 Ya que tenemos el archivo telegraf.conf solo nos queda iniciar telegraf
 
    ./telegraf --config telegraf.conf

__3 Intalación y configuracion de Grafana__

1.1 Ubicate en el directorio donde deseas trabajar
    
    cd ~/Documentos/stats_test

1.2 Descarga y descomprime los archivos binarios necesarios para Grafana

    wget https://dl.grafana.com/oss/release/grafana-7.1.3.linux-amd64.tar.gz
    tar -zxvf grafana-7.1.3.linux-amd64.tar.gz
    
1.3 Inicia el grafana-server
    
    cd grafana-7.1.3/bin
    ./grafana-server

1.4 Habrá iniciado grafana en el puerto 3000, ingresa a tu ip:3000 (127.0.0.1:3000) en tu navegador
  el usuario y contraseña inicial es:
  user: admin
  password: admin
  
# Instalación del proyecto Django
__1 Instalar postgresql, ngixn, pip, curl__


    sudo apt update
    sudo apt install python-pip python-dev libpq-dev postgresql postgresql-contrib nginx curl   

__2 Descargar el proyecto__

    mkdir ~/Documentos/monitoreo_pyhton_grafana
    cd ~/Documentos/monitoreo_pyhton_grafana
    git clone git@github.com:fernandoWH/monitoreopython-influxdb-telegraf-grafana.git
    
__3 Crear entorno virtual__

3.1 Descargar virtualenv

    sudo -H pip install --upgrade pip
    sudo -H pip install virtualenv

3.2 Crear entorno virtual

    virtualenv monitoreo
    source monitoreo/bin/activate
    
ó

    mkvirtualenv monitoreo
    
__4 Instalar requirements.txt__
    
    cd monitoreopython-influxdb-telegraf-grafana/
    pip install -r requirements.txt

__5 Correr el proyecto__

    cd monitoreo
    ./manage.py runserver
    
    
#Configuracion de Proxy Grafana-Ngixn

__1 Crear archivo grafana.conf__

    sudo nano /etc/nginx/sites-available/grafana.conf
    
1.1 Pegar lo siguiente dentro del archivo:

    server {
      listen      80;
      # listen      [::]:80 ipv6only=on;
      server_name localhost;
      root /usr/share/nginx/www;
      index index.html index.htm;
    
    
      location /grafana/ {
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-Host $host;
                proxy_set_header X-Forwarded-Server $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_hide_header 'x-frame-options';
                proxy_set_header x-frame-options allowall;
    
                add_header Access-Control-Allow-Origin *;
                add_header 'Access-Control-Allow-Credentials: true' always;
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
                add_header 'Access-Control-Expose-Headers' 'Content-Type,Content-Length,Content-Range';
                add_header 'Access-Control-Allow-Headers'
                           'Accept,
                            Authorization,
                            Cache-Control,
                            Content-Type,
                            DNT,
                            If-Modified-Since,
                            Keep-Alive,
                            Origin,
                            User-Agent,
                            X-Requested-With' always;
    
                if ($request_method = 'OPTIONS') {
                  return 204;
                }
    
                proxy_pass http://localhost:3000/;
    
            }
    
      location / {
            proxy_pass http://localhost:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Server $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_hide_header 'x-frame-options';
            proxy_set_header x-frame-options allowall;
    
            add_header Access-Control-Allow-Origin *;
            add_header 'Access-Control-Allow-Credentials: true' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Expose-Headers' 'Content-Type,Content-Length,Content-Range';
            add_header 'Access-Control-Allow-Headers'
                       'Accept,
                        Authorization,
                        Cache-Control,
                        Content-Type,
                        DNT,
                        If-Modified-Since,
                        Keep-Alive,
                        Origin,
                        User-Agent,
                        X-Requested-With' always;
    
            if ($request_method = 'OPTIONS') {
              return 204;
            }
        }
    }

1.2 Vincular a sites-enable

    sudo ln -s /etc/nginx/sites-available/grafana.conf /etc/nginx/sites-enabled

1.3 Verificar la sintaxis de grafana.conf
    
    sudo nginx -t
    
1.4 Recargar nginx
    
    sudo service nginx reload
    
1.5 Configurar grafana.ini o defaults.ini

Ingrese a la carpeta donde esta ubicado grafana y abre el archivo

    cd ~/Documentos/stats_test/grafana-7.1.3/conf
    nano defaults.ini
    
Cambiaremos lo siguiente:

    # root_url = %(protocol)s://%(domain)s:%(http_port)s/
    root_url = %(protocol)s://%(domain)s:%(http_port)s/grafana
    
    # enable anonymous access
    # enabled = false
    enabled = true
    
    [dataproxy]

    # This enables data proxy logging, default is false
    # logging = false
    logging =true
    
1.6 Reiniciamos el servicio grafana

    cd ~/Documentos/stats_test/grafana-7.1.3/bin
    ./grafana-server