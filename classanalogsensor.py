import machine
import os
#from datetime import datetime
from machine import Pin, UART, SoftI2C
from ADS1115 import *
import ustruct
from ulab import numpy as np
import random
import gc

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

BAUDRATE = 19200
BAUDRATE_STORX = 19200
BAUDRATE_COMPASS = 4800
BAUDRATE_PROBECO2 = 19200

uart_ch = 0
uart = UART(2, BAUDRATE) #trocar uart no esquemático para a UART 2. A UART 0 é utilizada como UART DOWNLOAD

framesync = "STATION"

WS_in_min = 0.0
WS_in_max = 5.0
WS_out_min = 0.0    #WIND SPEED RANGE: 0 to 100 M/S
WS_out_max = 100.0
 
WD_in_min = 0.01
WD_in_max = 4.94
WD_out_min = 0.0     #WIND DIRECTION RANGE: 0 to 360
WD_out_max = 360.0

T_in_min = 0
T_in_max = 1.0
T_out_min = -40     #range temperatura: -40°C à +60°C
T_out_max = 60
 
H_in_min = 0
H_in_max = 1.0
H_out_min = 0       #range humidade: 0-100%
H_out_max = 100

P_in_min = 0
P_in_max = 5
P_out_min = 800     #range pressao 800 a 1060 hpa 
P_out_max = 1060

#PCB LM35
LM_in_min = 0.0
LM_in_max = 1.50     #out 0mV + 10mV/°C
LM_out_min = 2.0     #range pressao 800 a 1060 hpa 
LM_out_max = 150.0


WS_data = []
WD_data = []
T_data = []
H_data = []
P_data = []
LM_data = []
co2_data=[]
 
ADS1115_1_ADDRESS = 0x48   # PIN ADDR = GND
ADS1115_2_ADDRESS = 0X49   # PIR ADDR = VCC

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

adc_1 = ADS1115(ADS1115_1_ADDRESS, i2c=i2c)
adc_2 = ADS1115(ADS1115_2_ADDRESS, i2c=i2c)

adc_1.setVoltageRange_mV(ADS1115_RANGE_6144)
adc_1.setCompareChannels(ADS1115_COMP_0_GND)
adc_1.setMeasureMode(ADS1115_SINGLE)
adc_2.setVoltageRange_mV(ADS1115_RANGE_6144)
adc_2.setCompareChannels(ADS1115_COMP_0_GND)
adc_2.setMeasureMode(ADS1115_SINGLE) 

input_var = 0

interruptCounter=0
timer=machine.Timer(0)

totalInterruptsCounter=0

a=0
state_name='0'
n_data = 60    # quantidade de medidas a ser adquirida
n_var_co2=2


def handlerInterrupt(timer):
    global interruptCounter    
    interruptCounter+=1
    #print("interruptcounter: {}".format(interruptCounter))
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada

"""  
def readChannel_1(channel):
    adc_1.setCompareChannels(channel)
    adc_1.startSingleMeasurement()
    while adc_1.isBusy():
        pass
    voltage = adc_1.getResult_V()
    return voltage

def readChannel_2(channel):
    adc_2.setCompareChannels(channel)
    adc_2.startSingleMeasurement()
    while adc_2.isBusy():
        pass
    voltage = adc_2.getResult_V()
    return voltage

"""

def readChannel(adc, channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage


class AnalogSensor:
    def __init__(self, X_in_min, X_in_max, X_out_min, X_out_max):
        self.X_in_min = X_in_min
        self.X_in_max = X_in_max
        self.X_out_min = X_out_min
        self.X_out_max = X_out_max
        
    def read(self, n_data, ADC, PORT):
        global interruptCounter
        a=0
        while a < n_data: # 60 amostras
            if interruptCounter > 0:
                print("Leitura {} de {}".format(a, n_data))
                interruptCounter = interruptCounter - 1
                X_value =  readChannel(ADC, PORT)
                X = (X_value - self.X_in_min) * (self.X_out_max - self.X_out_min) / (self.X_in_max - self.X_in_min) + self.X_out_min
                #print("leitura temperatura int {}".format(X))
                X_data.append(X)
                a+=1

        X_mean = np.mean(X_data)
        X_stdev = np.std(X_data)
    
        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
        X_Data = [X_mean, X_stdev]
        #print(X_Data)
        return X_Data
    



# criando os sensores 
anemometro = anemometer(WS_in_min, WS_in_max, WS_out_min, WS_out_max, WD_in_min, WD_in_max, WD_out_min, WD_out_max) 
LM35 = InternalTemperature(LM_in_min, LM_in_max, LM_out_min, LM_out_max)
probe_thr = TemperatureHumidityProbe(T_in_min, T_in_max, T_out_min, T_out_max, H_in_min, H_in_max, H_out_min, H_out_max)
barometro = Barometer(P_in_min, P_in_max, P_out_min, P_out_max)



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

