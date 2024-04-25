
import machine
import os
#from datetime import datetime
from machine import Pin, UART, SoftI2C
from ADS1115 import *

from ulab import numpy as np

import ure

regex = ure.compile("(\d.+\d.+)")

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

BAUDRATE = 19200
BAUDRATE_STORX = 19200
BAUDRATE_COMPASS = 4800
BAUDRATE_PROBECO2 = 19200

uart_ch = 0
uart = UART(2, BAUDRATE) #trocar uart no esquemático para a UART 2. A UART 0 é utilizada como UART DOWNLOAD
n_data=10
interruptCounter=0
timer=machine.Timer(0)
n_var_co2=2

def handlerInterrupt(timer):
    global interruptCounter    
    interruptCounter+=1
    #print("interruptcounter: {}".format(interruptCounter))
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada

def select_uart(uart_ch):
    global BAUDRATE_STORX, BAUDRATE_COMPASS, BAUDRATE_PROBECO2, BAUDRATE 
    if uart_ch == 0:
        #uart = UART(2, BAUDRATE_STORX)
        BAUDRATE=BAUDRATE_STORX
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)

    elif uart_ch == 1:
        #uart = UART(2, 19200)
        BAUDRATE=BAUDRATE_PROBECO2
        uart.write("i'm in..............")
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
                
    elif uart_ch == 2:
        #uart = UART(2, BAUDRATE_COMPASS)
        BAUDRATE=BAUDRATE_COMPASS
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)


class SerialSensor:
    def __init__(self, uart_ch, BAUDRATE_COMPASS):
        self.uart_ch=uart_ch
        self.baudrate=BAUDRATE_COMPASS
        select_uart(self.uart_ch)

    def write(self, msg):
        global interruptCounter
        a=0
        while a < 15: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
            uart.write(msg) 
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                data=uart.readline()
                print("I read: {}".format(data))
                a+=1

    def read(self, n_data, n_val):
        global interruptCounter
        a=0
        matrix=[]
        while a < n_data: # 60 amostras
        
            if interruptCounter > 0:
                print("Leitura {} de {}".format(a, n_data))                
                interruptCounter = interruptCounter - 1
                
                data=uart.readline()
                print("Serial sensor read: {}".format(data))
                print(type(data))
                
                if data is not None:
                    data_str=data.decode()
                    x=data_str.split()
                    x_floats = [float(valor) for valor in x]
                    matrix.append(x_floats)
                    print(matrix)         
                    a+=1

        # Envia o comando S para o probe de CO2 para finalizar a leitura
        uart.write("S\r\n")

        # Inicializar listas para armazenar os valores
        means=[]
        stds=[]

        # Iterar sobre cada linha e coluna da matriz
        for i in range(n_val):
            column_data = [row[i] for row in matrix]
            means.append(np.mean(column_data))
            stds.append(np.std(column_data))

        #preenche vetor de resultado com média_1, std_1, média_2, std_2,...
        resultado=[]
        for i in range(n_val):
            resultado.append(means[i])
            resultado.append(stds[i])  

        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        return resultado
    
sensor=SerialSensor(1, 19200)
# Função principal do programa
def main():
    global n_data
    
    # Inicializando a máquina de estados com o estado A
    
    while True:
        sensor.write("R\r\n")
        var=sensor.read(n_data, n_var_co2)
        print(var)

# Executando a função principal
if __name__ == "__main__":
    main()

