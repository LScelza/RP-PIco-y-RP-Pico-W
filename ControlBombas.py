"""
Autor: Leonardo Scelza
Fecha: 2022-08-15
"""


"""
Este archivo controla dos bombas utilizando una Raspberry Pi Pico. Monitorea la temperatura y corriente a través de sensores DS18B20 y ACS712, respectivamente. 

Hardware requerido:
- 2 bombas.
- 2 sensores de temperatura DS18B20.
- 1 sensor de corriente ACS712.
- Relés electromecánicos o de estado sólido para controlar las bombas.
- 2 selectores de dos posiciones.
- 1 display LCD 16 x 2.
- 1 módulo I2C para el display.

Clase Bomba:

    Attributes:
        - numero (str): Número de la bomba.
        - id_temp (bytearray): Identificación del sensor de temperatura asociado.
        - corriente_falla (float): Corriente máxima para considerar una falla.
        - temp_falla (int): Temperatura máxima para considerar una falla.
        - rele (Pin): Pin para controlar el relé asociado a la bomba.
        - pin_sensor (int): Pin para el sensor de temperatura.
        - estado_bomba (bool): Estado de la bomba (encendida o apagada).
        - estado_falla (bool): Estado de falla (True si hay una falla, False en caso contrario).
        - corriente (float): Corriente medida.
        - temperatura (int): Temperatura medida.

    Methods:
        - marcha(): Enciende la bomba.
        - parada(): Apaga la bomba.
        - medir_corriente(): Mide la corriente utilizando el sensor ACS712.
        - medir_temperatura(): Mide la temperatura utilizando el sensor DS18B20.
        - falla(): Maneja una situación de falla.

Funciones Adicionales:

    - display(linea1, linea2): Muestra información en una pantalla LCD.
    - inicio(): Inicializa el sistema y muestra un mensaje de inicio.
    - verificar_manual(): Verifica si el modo de operación es manual.
    - verificar_bomba1(): Verifica el estado de la bomba 1.
    - marcha_manual(): Inicia una bomba en modo manual.
    - verificar_flotante(): Verifica el estado del sensor flotante.
    - marcha_auto(): Inicia una bomba en modo automático.
    - verificar_falla(): Verifica si hay una falla en alguna de las bombas.
    - main(): Función principal que ejecuta el ciclo de control.

Instrucciones de Uso:

    - Conectar correctamente los componentes hardware.
    - Ejecutar este script en una Raspberry Pi Pico.
    - El sistema controlará las bombas, monitorizará la temperatura y corriente, y manejará situaciones de falla.
"""


from machine import I2C, Pin, ADC                 
import utime							         
from lcd_api import LcdApi                        
from pico_i2c_lcd import I2cLcd                   
import onewire							          
from ds18x20 import DS18X20                       
import binascii                                   

I2C_ADDR = 0x27   
I2C_NUM_ROWS = 2  
I2C_NUM_COLS = 16 
i2c = I2C(0, scl = Pin(9), sda = Pin(8), freq = 400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

manual = Pin(12, Pin.IN, Pin.PULL_DOWN)
flotante = Pin(11, Pin.IN, Pin.PULL_DOWN) 
bomba1 = Pin(14, Pin.IN, Pin.PULL_DOWN)

# Para saber la dirección del sensor:
# ow = onewire.OneWire(Pin(6)) # Crea un objeto onewire y prepara el pin 6 para usar el protocolo.
# sensor = DS18X20(ow) # Define un sensor en ese pin.
# id_temp_bomba1 = binascii.unhexlify("280bb575d0013c92") 
# id_temp_bomba2 = binascii.unhexlify("28de2775d0013c89") 
# En este caso, la dirección se averiguó previamente y acá solo se carga el valor.

class Bomba:
    

    def __init__(self, numero:int, id_temp:any, corriente_falla:float, pin_rele:int, pin_sensor:int, temp_falla:int = 70, tension:int = 380, corriente_nominal:float = 0, potencia:float = 0) -> None:
        self.__numero = numero
        self.__tension = tension
        self.__corriente_nominal = corriente_nominal
        self.__potencia = potencia
        self.__id_temp = id_temp
        self.__corriente_falla = corriente_falla
        self.__temp_falla = temp_falla
        self.__rele = Pin(pin_rele, Pin.OUT)
        self.__pin_sensor = pin_sensor
        self.__estado_bomba = False
        self.__estado_falla = False
        self.__corriente = 0
        self.__temperatura = 0

    def __str__(self) -> str:
        print(f'Bomba N°: {self.__numero}')
        print(f'Tensión: {self.__tension} V')
        print(f'Corriente nominal: {self.__corriente_nominal} A')
        print('Potencia: {self.__potencia} HP')
        

    @property
    def estado_falla(self) -> bool:
        return self.__estado_falla
    
    @property
    def corriente(self) -> float|None:
        return self.__corriente
    
    @property
    def temperatura(self) -> int|None:
        return self.__temperatura
    
    @property
    def estado_bomba(self) -> bool:
        return self.__estado_bomba
    
  
    def marcha(self) -> bool:
        #self.__rele.off()  # Si los relés son de lógica 0
        self.__rele.on()  # Si los relés son de lógica 1
        self.__estado_bomba = True
            
        
    def parada(self) -> bool:
        self.__rele.off()  # Si los relés son de lógica 1
        #self.__rele.on()  # Si los relés son de lógica 0
        self.__estado_bomba = False


    def medir_corriente(self) -> float|None:
        corriente_leida = ADC(26)
        CONVERSION = 3.3 / 65535
        lista = []        
        for i in range(1000):
            reading = corriente_leida.read_u16() * CONVERSION
            corriente = round((reading - 1.65) / .066, 1)
            lista.append(corriente)
            utime.sleep(.001)
        if max(lista) >= self.__corriente_falla:
            self.falla()
            return None
        else:   
            self.__corriente = max(lista)
          

    def medir_temperatura(self)-> int|None:
        try:
            ow = onewire.OneWire(Pin(self.__pin_sensor))
            sensor = DS18X20(ow)
            sensor.convert_temp()
            utime.sleep (1)
            temp = int(sensor.read_temp (self.__id_temp))
            if temp >= self.__temp_falla:
                self.falla()
                return None
            else:
                self.__temperatura = temp
        except:
            ow.reset()


    def falla(self) -> bool:
        self.parada()
        self.__estado_bomba = False
        self.__estado_falla = True


b1 = Bomba(1, binascii.unhexlify("280bb575d0013c92"), 13, 22, 6)
b2 = Bomba(2, binascii.unhexlify("28de2775d0013c89"), 13, 21, 6)


# Para sistemas que soporten f-string (no RP Pico).

# ESTADOS = ('Modo: Manual', 'Modo: Auto', 'Modo: Falla', f'{b1.numero}: ON', f'{b2.numero}: ON', f'I B1: {b1.medir_corriente():3.1f} A',
#            f'I B2: {b2.medir_corriente():3.1f} A', f'Temp. B1: {b1.medir_temperatura():2d} °C', f'Temp. B2: {b2.medir_temperatura:2d} °C',
#             'Esperando...', 'Falla en', 'ambas bombas', 'Llamar al', 'servicio técnico')

ciclo = 0
flotante_previo = False


def display(linea1:str, linea2:str) -> None: # Poner tuplas que correspondan. Ej.: display((ESTADOS(0), ESTADOS(3)))
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(linea1.center(16))
    lcd.move_to(0,1)
    lcd.putstr(linea2.center(16))
    return None


def inicio() -> None:
    utime.sleep(2)
    b1.parada()
    b2.parada()
    lcd.clear()
    lcd.move_to(2, 0)
    lcd.putstr('Iniciando...') 
    utime.sleep(3)
    lcd.clear()
    lcd.move_to(1, 0)
    lcd.putstr('Esperando...')
    utime.sleep(3)
    return None


def verificar_manual() -> bool:
    if manual.value():
        return True
    return False


def verificar_bomba1() -> bool:
    if bomba1.value():
        return True
    return False
    

def marcha_manual() -> bool:
    if verificar_manual():
        if verificar_bomba1():
            b2.parada()
            utime.sleep(1)
            b1.marcha()
            
            # display(ESTADOS[0], ESTADOS[3])
            # RP Pico:
            display('Modo: Manual', 'Bomba 1: ON')
        else:
            b1.parada()
            utime.sleep(1)
            b2.marcha()
            # display(ESTADOS[0], ESTADOS[4])
            # RP Pico:
            display('Modo: Manual', 'Bomba 2: ON')
        return True
    return False


def verificar_flotante() -> bool:
    global flotante_previo
    global ciclo
    if flotante.value():
        if not flotante_previo:
            flotante_previo = True
            ciclo += 1
        return True
    else:
        if flotante_previo:
            flotante_previo = False
        return False


def marcha_auto() -> bool:
    if not verificar_manual():
        if verificar_flotante():
            if ciclo % 2 == 0:
                b2.parada()
                utime.sleep(1)
                b1.marcha()
                #display(ESTADOS[1], ESTADOS[3])
                # RP Pico:
                display('Modo: Auto', 'Bomba 1: ON')
            else:
                b1.parada()
                utime.sleep(1)
                b2.marcha()
                # display(ESTADOS[1], ESTADOS[4])
                # RP Pico:
                display('Modo: Auto', 'Bomba 2: ON')  
        else:
            b1.parada()
            b2.parada()
            # display(ESTADOS[9], '')
            # RP Pico:
            display('Esperando...', '')
        return True
    return False


def verificar_falla() -> None:
    if b1.estado_falla and b2.estado_falla:
        b1.parada()
        b2.parada()
        while True:
            # display(ESTADOS[-4], ESTADOS[-3]) 
            # RP Pico:
            display('Falla en', 'ambas bombas')
            utime.sleep(5)
            # display(ESTADOS[-2], ESTADOS[-1]) 
            # RP Pico:
            display('Llamar al', 'servivcio técnico')
            utime.sleep(5)
    elif b1.estado_falla:
        b1.parada()
        while True:
            if verificar_flotante():
                if not b2.estado_falla:
                    b2.marcha()
                    # display(ESTADOS[1], ESTADOS[4])
                    # RP Pico:
                    display('Modo: Auto', 'Bomba 2: ON')
                    b2.medir_corriente()
                    b2.medir_temperatura()
                    if not b2.estado_falla:
                        utime.sleep(2)
                        # display(ESTADOS[6], ESTADOS[8])
                        # RP Pico:
                        corriente = 'I B2: ' + str(b2.corriente) + ' A'
                        temperatura = 'Temp. B2: ' + str(b2.temperatura) + ' C'
                        display(corriente, temperatura)
                        utime.sleep(2)
                else:
                    while True:
                        # display(ESTADOS[-4], ESTADOS[-3]) 
                        # RP Pico:
                        display('Falla en', 'ambas bombas')
                        utime.sleep(5)
                        # display(ESTADOS[-2], ESTADOS[-1]) 
                        # RP Pico:
                        display('Llamar al', 'servicio técnico')
                        utime.sleep(5)
            else:
                b2.parada()
    elif b2.estado_falla:
        b2.parada()
        while True:
            if verificar_flotante():
                if not b1.estado_falla:
                    b1.marcha()
                    # display(ESTADOS[1], ESTADOS[3])
                    # RP Pico:
                    display('Modo: Auto', 'Bomba 1: ON')
                    b1.medir_corriente()
                    b1.medir_temperatura()
                    if not b1.estado_falla:
                        utime.sleep(2)
                        # display(ESTADOS[5], ESTADOS[7])
                        # RP Pico:
                        corriente = 'I B1: ' + str(b1.corriente) + ' A'
                        temperatura = 'Temp. B1: ' + str(b1.temperatura) + ' C'
                        display(corriente, temperatura)
                        utime.sleep(2)
                else:
                    while True:
                        # display(ESTADOS[-4], ESTADOS[-3]) 
                        # RP Pico:
                        display('Falla en', 'ambas bombas')
                        utime.sleep(5)
                        # display(ESTADOS[-2], ESTADOS[-1])
                        # RP Pico:
                        display('Llamar al', 'servicio técnico')
                        utime.sleep(5)
            else:
                b1.parada()
    else:
        return None
    


def main() -> None:
     inicio()
     while True:
        #print(ciclo)
        marcha_manual()
        marcha_auto()
        b1_en_marcha = b1.estado_bomba
        b2_en_marcha = b2.estado_bomba
        if b1_en_marcha:
            b1.medir_corriente()
            b1.medir_temperatura()
            if not b1.estado_falla:
                utime.sleep(2)
                # display(ESTADOS[5], ESTADOS[7])
                # RP Pico:
                corriente = 'I B1: ' + str(b1.corriente) + ' A'
                temperatura = 'Temp. B1: ' + str(b1.temperatura) + ' C'
                display(corriente, temperatura)
               
                utime.sleep(2)
            else:
                verificar_falla()
        if b2_en_marcha:
            b2.medir_corriente()
            b2.medir_temperatura()
            if not b2.estado_falla:
                utime.sleep(2)
                # display(ESTADOS[6], ESTADOS[8])
                # RP Pico:
                corriente = 'I B2: ' + str(b2.corriente) + ' A'
                temperatura = 'Temp. B2: ' + str(b2.temperatura) + ' C'
                display(corriente, temperatura)
        
                utime.sleep(2)
            else:
                verificar_falla()
        
        
 


if __name__ == '__main__':
    main()