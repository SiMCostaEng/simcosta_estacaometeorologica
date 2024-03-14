import machine
import os
#from datetime import datetime
from machine import Pin, UART, SoftI2C
from time import sleep
from ADS1115 import *
import ustruct
from ulab import numpy as np
import random


CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

BAUDRATE_STORX = 19200
BAUDRATE_COMPASS = 4800
BAUDRATE_PROBECO2 = 19200

uart_ch = 0
uart = UART(2, BAUDRATE_STORX) #trocar uart no esquemático para a UART 2. A UART 0 é utilizada como UART DOWNLOAD

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
T_in_max = 3413
T_out_min = -40     #range temperatura: -40°C à +60°C
T_out_max = 60
 
H_in_min = 0
H_in_max = 3413
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
# print(type(WS_data)) 
WD_data = []
T_data = []
H_data = []
P_data = []
 

 
ADS1115_1_ADDRESS = 0x48
ADS1115_2_ADDRESS = 0X49

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
totalInterruptsCounter=0

contador = 0
marcador = 0

timer=machine.Timer(0)
        



def handlerInterrupt(timer):
    global interruptCounter
    global contador
    global input_var
    
    interruptCounter = interruptCounter + 1
    contador = contador + 1
    
    global estacao_comma_separated
    
    if input_var == 2:
        T_value = readChannel_1(ADS1115_COMP_0_GND)
        H_value = readChannel_1(ADS1115_COMP_1_GND)
        WS_value = readChannel_1(ADS1115_COMP_2_GND)  #random.uniform(0.0, 10.0)
        WD_value = readChannel_1(ADS1115_COMP_3_GND)
        P_value = readChannel_2(ADS1115_COMP_3_GND)
        LM_value =  readChannel_2(ADS1115_COMP_0_GND)
        
        TH_data = TemperatureHumidityRead(T_value, H_value)
        wind_data = anemometerRead(WS_value, WD_value)
        pressure_data = barometerRead(P_value)
        LM_data=InternalTemperatureRead(LM_value)
        
        uart_ch=2 #bussola
        select_uart(uart_ch)
        
        bussola_data = getBussolaInfo(uart.read())
        
        
        uart_ch=1 #probe co2
        select_uart(uart_ch)
        
        co2_data = CarbonDioxideProbe.read(uart.read())
        
        estacao = wind_data + TH_data + pressure_data + LM_data #+ bussola_data

        estacao=str(estacao).strip('[]')   #transforma list em string retirando conchetes da msg
        counterstr=str(totalInterruptsCounter)
        
        estacao=[framesync,' '+estacao]              #coloca framesync no inicio da msg
        #estacao=[counterstr,framesync,estacao]        
        #print(estacao)
        estacao_comma_separated = ','.join(estacao)
        print(estacao_comma_separated)
    
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada


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

def select(uart_ch):
    global uart_station, BAUDRATE_STORX, BAUDRATE_COMPASS, BAUDRATE_PROBECO2, MSG 

    if uart_ch == 0:
        uart = UART(2, BAUDRATE_STORX)
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)

    elif uart_ch == 1:
        uart = UART(2, BAUDRATE_PROBECO2)
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
                
    elif uart_ch == 2:
        uart = UART(2, BAUDRATE_COMPASS)
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)

def anemometerRead(WS_value, WD_value):

    WS = (WS_value - WS_in_min) * (WS_out_max - WS_out_min) / (WS_in_max - WS_in_min) + WS_out_min
    WS_data.append(WS)
#     print(len(WS_data))
    WS_mean = np.mean(WS_data)
    WS_stdev = np.std(WS_data)
    
    WD = (WD_value - WD_in_min) * (WD_out_max - WD_out_min) / (WD_in_max - WD_in_min) + WD_out_min
    
    WD_data.append(WD)
    WD_mean = np.mean(WD_data)
    WD_stdev = np.std(WD_data)
    
    gc.collect() # control of garbage collection
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
    anemometerData = [WS_mean, WS_stdev, WD_mean, WD_stdev]   #List
    #print(type(anemometerData))
    #anemometerData = str(anemometerData)                     #make list into string
     
    #print(type(anemometerData))

    return anemometerData

def barometerRead(P_value):
    P = (P_value - P_in_min) * (P_out_max - P_out_min) / (P_in_max - P_in_min) + P_out_min
    #print(P)
    P_data.append(P)
    #print(P_data)
#     print(len(WS_data))
    P_mean = np.mean(P_data)
    P_stdev = np.std(P_data)
  
    gc.collect() # control of garbage collection
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
    barometerData = [P_mean, P_stdev]   #List
    
    return barometerData


def TemperatureHumidityRead(T_value, H_value):
    T = (T_value - T_in_min) * (T_out_max - T_out_min) / (T_in_max - T_in_min) + T_out_min
    T_data.append(T)
    # print(len(WS_data))
    T_mean = np.mean(T_data)
    T_stdev = np.std(T_data)
    
    H = (H_value - H_in_min) * (H_out_max - H_out_min) / (H_in_max - H_in_min) + H_out_min
    H_data.append(H)
    H_mean = np.mean(H_data)
    H_stdev = np.std(H_data)
    
    gc.collect() # control of garbage collection
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
    probeTHRData = [T_mean, T_stdev, H_mean, H_stdev]
    #probeData = str(probeData)
    return probeTHRData


def InternalTemperatureRead(LM_value):
    LM = (LM_value - LM_in_min) * (LM_out_max - LM_out_min) / (LM_in_max - LM_in_min) + LM_out_min
    LM_data.append(LM)
    # print(len(WS_data))
    LM_mean = np.mean(LM_data)
    LM_stdev = np.std(LM_data)
    
    gc.collect() # control of garbage collection
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
    InternalTempData = [LM_mean, LM_stdev]
    print(InternalTempData)
    #probeData = str(probeData)
    return probeTHRData

def getBussolaInfo (bussola):
    if bussola != None:
         bussola=str(bussola)
         bussval = get_first_nbr_from_str(bussola)
         print(bussval)
    return bussval

def get_first_nbr_from_str(input_str):
    if not input_str and not isinstance(input_str, str):
        return 0
    out_number = ''
    for ele in input_str:
        if (ele == '.' and '.' not in out_number) or ele.isdigit():
            out_number += ele
        elif out_number:
            break
    return float(out_number)


class CarbonDioxideProbe:
    def __init__(self, uart_ch):
        self.uart_ch = 1
        self.baudrate = 19200
    
    def inicializar():
        uart_ch=1
        uart.write("R\r\n")
    
    def read():
        global uart, a, uart_ch, CarbonDioxideProbe_info
        
        uart_ch=1
        uart.write("R\r\n")
        if a < 20:
            time.sleep(1)
            CarbonDioxideProbe_info=uart.read()
            #print("CarbonDioxideProbe_info: {}".format(CarbonDioxideProbe_info))
            a+=1
        uart.write("S\r\n")
        return CarbonDioxideProbe_info
    
    def separate(CarbonDioxideProbe_info):
        a=[]
        
        if CarbonDioxideProbe_info != None:
            for word in CarbonDioxideProbe_info.split():
                try:
                    a.append(float(word))
                except ValueError:
                    pass
           
        CarbonDioxideProbe_data = a
        return CarbonDioxideProbe_data

#######################################################################################
############################# FINITE STATE MACHINE ####################################

class State0:
    def __init__(self):
        self.name = '0'

    def transition(self, input_var):
        global contador
        global marcador
        
        if input_var == 0:
            return State0()
        elif input_var == 1:
            marcador = contador
            
            return StateWait.wait()
        else:
            print('erro')
            return State0()
        
class StateWait:
    def __init__(self):
        self.name = '1'
        
        
    def transition(self, input_var):

        if input_var == 1:
            return StateWait.wait()
        elif input_var == 2:
            return StateRead.read()
        else:
            print('erro')
            return State0()
        
    def wait():
        global input_var
        global interruptCounter
        global totalInterruptsCounter

        totalInterruptsCounter = 0
        interruptCounter = 0
        
        print("wait: {}".format(input_var))
        print('going to sleep')
        
        while totalInterruptsCounter < 10:    #espera 10s para iniciar leituras
            
            if interruptCounter > 0:
                input_var=1
                state = machine.disable_irq()
                interruptCounter = interruptCounter - 1
                machine.enable_irq(state)

                totalInterruptsCounter = totalInterruptsCounter + 1
                print("slept for: "+ str(totalInterruptsCounter))     
        
        print("interrupt has occurred: "+ str(totalInterruptsCounter))     
            #machine.enable_irq(state)
            #print("interrupt has occurred: "+ str(totalInterruptsCounter))            
        
        interruptCounter = 0
        totalInterruptsCounter = 0
        
        print('waking up')
        input_var=2
        print("wait: {}".format(input_var))
        return StateWait().transition(input_var)     

class StateRead:
    def __init__(self):
        self.name = '2'

    def transition(self, input_var):
        if input_var == 2:
            return StateRead.read()
        elif input_var == 3:
            return StateSend.send()
        else:
            print('erro')
            return State0()
        
    def read():
        global interruptCounter
        global totalInterruptsCounter
        global input_var
        global estacao_comma_separated
        
        print("read: {}".format(input_var))
        
        
        while totalInterruptsCounter < 60:    #lê 600 amostras
            
            if interruptCounter > 0:
                input_var=2
                state = machine.disable_irq()
                interruptCounter = interruptCounter - 1
                machine.enable_irq(state)

                totalInterruptsCounter = totalInterruptsCounter + 1
                print("read {} amostras ".format(totalInterruptsCounter))     
        
        print("interrupt has occurred: "+ str(totalInterruptsCounter))     
            #machine.enable_irq(state)
            #print("interrupt has occurred: "+ str(totalInterruptsCounter))            
        
        print('li tudo')
        interruptCounter = 0
        totalInterruptsCounter = 0
        input_var=3
        print("leu: {}".format(input_var))
        return StateRead().transition(input_var)     

        

        
    
class StateSend:
    def __init__(self):
        self.name = '3'

    def transition(self, input_var):
        if input_var == 3:
            return StateSend.send()
        elif input_var == 4:
            return StateErase.erase()
        else:
            print('erro')
            return State0()
        
    def send():
        global input_var
        global estacao_comma_separated
        
        file = open('teste.txt', 'a')
        file.write(estacao_comma_separated)
        file.write("\n")
        file.close()
        print("send: {}".format(input_var))
        input_var=4
        return StateSend().transition(input_var)
    
class StateErase:
    def __init__(self):
        self.name = '4'

    def transition(self, input_var):
        if input_var == 4:
            return StateErase()
        elif input_var == 0:
            return State0()
        else:
            print('erro')
            return State0()
        
    def erase():
        global input_var
        P_data.clear()
        print("erase 1: {}".format(input_var))
        input_var=0
        
        print("erase 2: {}".format(input_var))
        return StateErase().transition(input_var)


#######################################################################################


# Função principal do programa
def main():
    # Inicializando a máquina de estados com o estado A
    current_state = State0()

    while True:
        global input_var
        #print(input_var)
        input_var = int(input("Digite um número de 0 a 4 (-1 para sair): "))
        if input_var == -1:
            break

        # Fazendo a transição de estado com base no input_var
        current_state = current_state.transition(input_var)
        print("Estado atual:", current_state.name)
        print("main: {}".format(input_var))

# Executando a função principal
if __name__ == "__main__":
    main()



