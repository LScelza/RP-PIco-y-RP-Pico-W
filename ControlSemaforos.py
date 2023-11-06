"""
Autor: Leonardo Scelza
Fecha: 2023-03-10
"""


"""
Controlador de Semáforo con Barrera Infrarroja

Este programa controla dos semáforos utilizando una placa Raspberry Pi Pico y una barrera infrarroja.
El hardware requerido incluye una barrera infrarroja, dos buzzer, y dos semáforos.
Las salidas de los buzzer están conectadas a transistores 2N2222 y las salidas de las luces están
conectadas a un optoacoplador MOC3021 y triacs BT137.

Clases:
- Semaforo: Controla el semáforo y sus componentes.
- Barrera: Representa la barrera infrarroja y su estado.

Funciones:
- main: Función principal que inicializa una instancia de Barrera y una instancia de Semaforo, y
  controla el semáforo en un bucle infinito.

Hardware Conexiones:
- Barrera: Conectada al Pin 21 (entrada).
- Ajuste de tiempo: Conectado al ADC Pin 26.
- Buzzer Derecho: Conectado al Pin 20 (salida).
- Buzzer Izquierdo: Conectado al Pin 19 (salida).
- Luz Verde: Conectada al Pin 18 (salida).
- Luz Roja: Conectada al Pin 17 (salida).

Clases:

- Semaforo:
    - Atributos:
        - __tension_lamparas (str): Tensión de las lámparas (default: '220 VCA').
        - __tension_buzzer (str): Tensión del buzzer (default: '12 VCC').
        - __barrera (Pin): Objeto Pin representando la barrera.
    
    - Métodos:
        - __str__(): Retorna información sobre la tensión de las lámparas y del buzzer.
        - regular_tiempo() -> float: Regula el tiempo de acuerdo a la lectura del ajuste de tiempo.
        - leer_barrera() -> bool: Lee el estado de la barrera y espera si está sensando.
        - encender_luz_verde(): Enciende la luz verde.
        - apagar_luz_verde(): Apaga la luz verde.
        - encender_luz_roja(): Enciende la luz roja.
        - apagar_luz_roja(): Apaga la luz roja.
        - encender_buzzer(): Enciende ambos buzzers.
        - apagar_buzzer(): Apaga ambos buzzers.
        - control_luces(): Controla el semáforo según el estado de la barrera.

- Barrera:
    - Atributos:
        - __tension_barrera (str): Tensión de la barrera (default: '12 VCC').
        - __salida (str): Especificaciones de salida (default: 'Relé NO-NC, máx.: 24 V 0.5 A').
        - __modelo (str): Modelo de la barrera (default: 'CYGNUS BIR2-60M').
        - __estado (bool): Estado de la barrera (default: False).

    - Métodos:
        - get_estado() -> str: Retorna el estado actual de la barrera.
        - __str__(): Retorna información sobre el modelo, tensión de la barrera, tipo de salida y estado.
        - sensar() -> None: Actualiza el estado de la barrera basado en la lectura del pin.

Función Principal:

- main():
    - Crea una instancia de Barrera y una instancia de Semaforo.
    - Controla el semáforo en un bucle infinito.
"""


from machine import Pin, ADC
import utime

barrera = Pin(21, Pin.IN, Pin.PULL_DOWN)
ajuste_tiempo = ADC(26)
buzzer_d = Pin(20, Pin.OUT)
buzzer_i = Pin(19, Pin.OUT)
verde = Pin(18, Pin.OUT)  
roja = Pin(17, Pin.OUT)  

class Semaforo:
    
    def __init__(self, barrera:object,tension_lamparas:str='220 VCA', tension_buzzer:str='12 VCC') -> None:
        self.__tension_lamparas = tension_lamparas
        self.__tension_buzzer = tension_buzzer
        self.__barrera = barrera

    def __str__(self) -> str:
        return f'Tensión de lámparas: {self.__tension_lamparas}\nTensión de buzzer: {self.__tension_buzzer}'
    
    def regular_tiempo(self) -> float:
        lectura = ajuste_tiempo.read_u16()
        if lectura <= 1000:
            return round((lectura / 10) / 1000,2) 
        else:
            return round((lectura * .0224 + 100) / 1000,2)
    
    
    def leer_barrera(self) -> bool:
        if self.__barrera.get_estado() == 'Sensando':
            utime.sleep(self.regular_tiempo())
            if self.__barrera.get_estado() == 'Sensando':
                return True
            else:
                return False

    
    def encender_luz_verde(self) -> None:
        verde.on()

    def apagar_luz_verde(self) -> None:
        verde.off()

    def encender_luz_roja(self) -> None:
        roja.on()

    def apagar_luz_roja(self) -> None:
        roja.off()

    def encender_buzzer(self) -> None:
        buzzer_d.on()
        buzzer_i.on()

    def apagar_buzzer(self) -> None:
        buzzer_i.off()
        buzzer_d.off()

    def control_luces(self) -> None:
        while self.leer_barrera():
            self.apagar_luz_verde()
            self.encender_luz_roja()
            self.encender_buzzer()
            utime.sleep(5)
        self.apagar_luz_roja()
        self.apagar_buzzer()
        self.encender_luz_verde()

    

class Barrera:
    
    def __init__(self, modelo:str='CYGNUS BIR2-60M', tension_barrera:str='12 VCC', salida:str='Relé NO-NC, máx.: 24 V 0.5 A', estado:bool=False) -> None:
        self.__tension_barrera = tension_barrera
        self.__salida = salida
        self.__modelo = modelo
        self.__estado = estado

    def get_estado(self):
        self.sensar()
        if self.__estado:
            return 'Sensando'
        return 'En espera'
        

    def __str__(self) -> str:
        return f'Modelo: {self.__modelo}\Tensión de alimentación barrera: {self.__tension_barrera}\Tipo de salida: {self.__salida}\nEstado: {self.get_estado()}'
    
    def sensar(self) -> bool:
        if barrera.value():
            self.__estado = True
        else:
            self.__estado = False

def main() -> None:
    b1 = Barrera()
    s1 = Semaforo(b1)
    while True:
        s1.control_luces()


if __name__ == '__main__':
    main()
            
