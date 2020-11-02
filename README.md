# Resumen
- sucam es una herramienta que permite monitorear en tiempo real su casa, oficina, o cualquier sitio que tenga camaras y haga uso de ésta. sucam solo graba fracciones de vídeos, y esto se debe a que solo guarda cuando detecta movimientos. A su vez este sistema puede enviar notificaciones SMS para alertar sobre intrusos o movimientos detectados en casa.
- Con sucam puede ver en tiempo real los eventos sucedidos en el lugar, através de un sitioweb.
- sucam tiene 4 modos: normal, detectar movimiento, diferencia de movimientos y gris.

# Estado actual
EN CONSTRUCCIÓN

# DISPOSITIVOS DE PRUEBAS
- MacOS
- Raspberry PI 4B

# PASOS
- Ejecutar los siguientes pasos:
1. pip3 install -r requirements.txt
2. python3 main.py
3. Abrir "http://localhost:5000/" en el navegador
4. Para detener "Live Streaming" abrir en el navegador "http://localhost:5000/ms-sudo-cam/api/v1/video-stop"

# CAMBIOS
- Para cambiar los modos de pantallas:
1. Abrir el archivo index.html
2. Modificar el modo en la linea 19. Ejemplo, cambiar type_cam (valores permitidos: 1,2,3,4): <img src="{{ url_for('video_feed', type_cam=3) }}" width="100%">

# MAC
1. brew install opencv

# LINUX
$ sudo ufw allow 5000