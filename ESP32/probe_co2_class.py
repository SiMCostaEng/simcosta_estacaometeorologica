import machine
import os
import ure
#from datetime import datetime
from machine import Pin, UART, SoftI2C
from machine import Timer
from ADS1115 import *
import ustruct
from ulab import numpy as np
import random
import gc

#a = int.to_bytes(10,2,'big')
uart = UART(2, 19200)

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX = Pin(4, mode=Pin.OUT, value=0)

CH_A_MUX.value(1)
CH_B_MUX.value(0)

BAUDRATE = 19200
BAUDRATE_STORX = 19200
BAUDRATE_COMPASS = 4800
BAUDRATE_PROBECO2 = 19200

CarbonDioxideProbe_info=[]

interruptCounter=0
timer=machine.Timer(0)

totalInterruptsCounter=0

a=0
#https://regex101.com/r/5O5syZ/4

posicao = 0


def handlerInterrupt(timer):
    global interruptCounter    
    interruptCounter+=1
    print("interruptcounter: {}".format(interruptCounter))
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada
    
    


def select_uart(uart_ch):
    global uart_station, BAUDRATE_STORX, BAUDRATE_COMPASS, BAUDRATE_PROBECO2, BAUDRATE 

    if uart_ch == 0:
        #uart = UART(2, BAUDRATE_STORX)
        BAUDRATE=BAUDRATE_STORX
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)

    elif uart_ch == 1:
        #uart = UART(2, 19200)
        BAUDRATE=BAUDRATE_PROBECO2
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




class CarbonDioxideProbe:
    def __init__(self, uart_ch):
        self.uart_ch = 1
        self.baudrate = 19200
    
    def inicializar():
        global interruptCounter, uart_ch
        uart_ch=1
        select_uart(uart_ch)
        print("entrei no co2 init")
        
        a=0

        while a < 10: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
            uart.write("R\r\n") 
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                a+=1
    
    def read():
        global uart, uart_ch, CarbonDioxideProbe_info, interruptCounter
        
        a=0
        dados_float=[]
        concentracao_co2=[]
        temperatura_co2=[]
        
        while a<60: # 60 amostras
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                
                # uart.write(" 1050.7    24.5\r\n")
                               
                CarbonDioxideProbe_info=uart.readline()
                print("co2 info: {}".format(CarbonDioxideProbe_info))
                if CarbonDioxideProbe_info != None:
                    print("co2 info: {}".format(CarbonDioxideProbe_info))
                    numeros_str = CarbonDioxideProbe_info.split()
                    # Converter os números para float e armazená-los na lista
                    for numero in numeros_str:
                        numero = numero.strip()  # Remover espaços em branco da string antes de converter
                        if numero:  # Verificar se a string não está vazia após remover os espaços em branco
                            dados_float.append(float(numero))

                    # Extrair os números float
                    concentracao_co2.append(dados_float[0])
                    temperatura_co2.append(dados_float[1])
                    #print("Número 1:", concentracao_co2)
                    #print("Número 2:", temperatura_co2)
                a+=1

                # Envia o comando S para o probe de CO2 para finalizar a leitura
                uart.write("S\r\n")

                concentracao_co2_mean = np.mean(concentracao_co2)
                concentracao_co2_stdev = np.std(concentracao_co2)
                temperatura_co2_mean = np.mean(temperatura_co2)
                temperatura_co2_stdev = np.std(temperatura_co2)
                
                gc.collect() # control of garbage collection
                gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
                probeCO2Data = [concentracao_co2_mean, concentracao_co2_stdev, temperatura_co2_mean, temperatura_co2_stdev]   #List
    
        return probeCO2Data
 
while(1):
    CarbonDioxideProbe.inicializar()
    co2_data = CarbonDioxideProbe.read()
    print(co2_data)



