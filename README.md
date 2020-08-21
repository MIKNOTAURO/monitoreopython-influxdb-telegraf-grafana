# stats Grafana
Estadisticas de Servidor con Grafana, InfluxDB, Telegraft

Se usará Ubuntu 18.04 para el ejemplo

__1 Instalación y configuracion de telegraf__

1.1 Ubicate en el directorio donde deseas trabajar
    
    cd ~/Documentos/stats_test

1.2 Descarga y descomprime los archivos binarios necesarios para Grafana

    wget https://dl.influxdata.com/telegraf/releases/telegraf-1.15.2_linux_amd64.tar.gz
    tar xf telegraf-1.15.2_linux_amd64.tar.gz
    
1.3 Archivo de configuración
  Ingresamos al siguiente repositorio de los datos descomprimidos y creamos un archivo telefraf.conf, con lo siguientes comandos, donde suaremos los plugins input cpu, mem y disk y plugins output influxdb
    
    cd telegraf-1.15.2/usr/bin
    ./telegraf -sample-config -input-filter cpu:mem:disk:net -output-filter influxdb > telegraf.conf
 
 Ya que tenemos el archivo telegraf.conf solo nos queda iniciar telegraf
 
    ./telegraf --config telegraf.conf

__2 Instalación y configuración de Influx DB__
2.1 Ubicate en el directorio donde deseas trabajar
    Abrir otra terminal
    
    cd ~/Documentos/stats_test

2.2 Descarga y descomprime los archivos binarios necesarios para Grafana

    wget https://dl.influxdata.com/influxdb/releases/influxdb-1.8.1_linux_amd64.tar.gz
    tar xvfz influxdb-1.8.1_linux_amd64.tar.gz

2.3 Iniciar InfluxDB
    
    cd influxdb-1.8.1-1/usr/bin
    ./influxd

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
  
    
