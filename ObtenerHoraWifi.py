"""
Autor: Leonardo Scelza
Fecha: 2023-09-12
"""


"""
Interruptor Horario con Raspberry Pi Pico W

Este programa implementa un interruptor horario utilizando una Raspberry Pi Pico W.
El dispositivo tiene dos componentes principales: un interruptor físico conectado al Pin 22
y una lámpara controlada por el Pin 20. Además, se utiliza la funcionalidad de conexión WiFi
para obtener la hora de un servidor de tiempo en línea y ajustar el comportamiento del interruptor
según la hora actual.

Hardware:
- Raspberry Pi Pico W
- Interruptor conectado al Pin 22
- Lámpara controlada por el Pin 20
- MOC3021 para el control de la lámpara
- BT137 para la alimentación de la lámpara

Funciones:
- conectar_red_wifi(ssid, clave):
    Establece la conexión a una red WiFi utilizando el nombre de red (SSID) y la contraseña proporcionados.

- obtener_hora():
    Obtiene la hora actual de un servidor de tiempo en línea utilizando el protocolo NTP (Network Time Protocol).

- activar_salida():
    Controla el encendido y apagado de la lámpara en función de la hora actual y el estado del interruptor físico.

Uso:
1. Configurar 'SSID_RED' y 'CLAVE_RED' con los detalles de la red WiFi a la que se desea conectar.
2. Conectar el interruptor al Pin 22 y la lámpara al Pin 20.
3. Al ejecutar el programa, el dispositivo se conectará a la red WiFi y sincronizará su reloj con un servidor de tiempo.
4. La función 'activar_salida()' se encargará de controlar la lámpara según el horario y el estado del interruptor.


Este ejemplo corresponde a un interruptor que controla las luces de un local en función del horario. 
"""




import network
import ntptime
import utime
from machine import Pin

ent_manual = Pin(22, Pin.IN, Pin.PULL_DOWN)
salida = Pin(20, Pin.OUT)


def conectar_red_wifi(ssid, clave) -> None:
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Conectando a red WiFi...')
        sta_if.active(True)
        sta_if.connect(ssid, clave)
        while not sta_if.isconnected():
            pass
    print('Conectado:', sta_if.ifconfig())


def obtener_hora() -> None:
    try:
        ntptime.settime()  
        return utime.localtime()
    except OverflowError:
        return None  

def activar_salida() -> None:
    hora = obtener_hora()
    if (hora[3]-3 >= 0 and hora[3]-3 < 7) or (hora[3]-3 >= 19  and hora[3]-3 <= 23) or ent_manual.value():
        salida.on()
    else:
        salida.off()

        
    

if __name__ == '__main__':
    SSID_RED = '*********' # Reemplazar por el nombre de la red.
    CLAVE_RED = '*********' # Reemplazar por la contraseña de la red.
    
    conectar_red_wifi(SSID_RED, CLAVE_RED)
    #hora = obtener_hora()
    #print('Hora actual (Año, Mes, Día, Hora, Minuto, Segundo, Día de la Semana, Día del Año):', hora)
    
    while True:
        try:
            activar_salida()
            utime.sleep(10)
        except:
            continue


