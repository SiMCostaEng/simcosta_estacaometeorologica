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
        global a, interruptCounter, uart_ch
        uart_ch=1
        select_uart(uart_ch)
        print("entrei no co2 init")
        a=0
        while a < 2:
            #print("vai escrever R pro probe")
            #uart.write("R\r\n") 
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                a+=1
    
    def read():
        global uart, a, uart_ch, CarbonDioxideProbe_info, interruptCounter, posicao
        
        a=0
        while a<10:
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                
                uart.write(" 1050.7    24.5\r\n")
                       
                
                CarbonDioxideProbe_info.append(uart.readline())
                print("co2 info: {}".format(CarbonDioxideProbe_info[a]))
                a+=1
            #print("CarbonDioxideProbe_info: {}".format(CarbonDioxideProbe_info))

        uart.write("S\r\n")
        print(CarbonDioxideProbe_info)
        print(type(CarbonDioxideProbe_info))
        size=len(CarbonDioxideProbe_info)
        
        #CarbonDioxideProbe_info=str(CarbonDioxideProbe_info)
        #print(CarbonDioxideProbe_info)
        #print(type(CarbonDioxideProbe_info))
        
        numeros_float=[]
        numero1=[]
        numero2=[]
        
        for i in range(size):
            print ("i={}".format(i))
            
            if CarbonDioxideProbe_info[i] != None:
                print("meu dado é {}".format(CarbonDioxideProbe_info[i]))
                
                numeros_str = CarbonDioxideProbe_info[i].split()
                
                # Inicializar uma lista para armazenar os números float


                # Converter os números para float e armazená-los na lista
                for numero in numeros_str:
                    numeros_float.append(float(numero))

            # Extrair os números float
                numero1.append(numeros_float[0])
                numero2.append(numeros_float[1])
                print("Número 1:", numero1)
                print("Número 2:", numero2)
   
while(1):
    
    CarbonDioxideProbe.inicializar()
    co2_data = CarbonDioxideProbe.read()
    #print(int.from_bytes(uart.read(),'big'))
    
    #time.sleep(0.5)


