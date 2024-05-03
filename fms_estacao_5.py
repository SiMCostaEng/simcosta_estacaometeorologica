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
#BAUDRATE_STORX = 19200
#BAUDRATE_COMPASS = 4800
#BAUDRATE_PROBECO2 = 19200


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


a=0
state_name='0'
n_data = 60    # quantidade de medidas a ser adquirida
n_var_co2=2    #quantiidade de variáveis medidas no sensor de co2
n_sec = 60     #quantidade de segundos a serem esperados na função init

def handlerInterrupt(timer):
    global interruptCounter    
    interruptCounter+=1
    #print("interruptcounter: {}".format(interruptCounter))
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada


def readChannel(adc, channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage

def select_uart(uart_ch, BAUDRATE):
    global uart
    if uart_ch == 0:
        #BAUDRATE=BAUDRATE_STORX
        uart = UART(2, BAUDRATE)
        print(BAUDRATE)
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)

    elif uart_ch == 1:
        #BAUDRATE=BAUDRATE_PROBECO2
        uart = UART(2, BAUDRATE)
        print(BAUDRATE)
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
                
    elif uart_ch == 2:
        #BAUDRATE=BAUDRATE_COMPASS
        uart = UART(2, BAUDRATE)
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)

class TemperatureHumidityProbe:
    def __init__(self, T_in_min, T_in_max, T_out_min, T_out_max, H_in_min, H_in_max, H_out_min,H_out_max):
        self.T_in_min = T_in_min
        self.T_in_max = T_in_max
        self.T_out_min = T_out_min
        self.T_out_max = T_out_max
        self.H_in_min = H_in_min
        self.H_in_max = H_in_max
        self.H_out_min = H_out_min
        self.H_out_max = H_out_max

    def read(self, n_data, ADC_T, PORT_T, ADC_H, PORT_H):
        global interruptCounter
        a=0
        while a < n_data:
            if interruptCounter > 0:
                print('Leitura {} de {}'.format(a, n_data))
                interruptCounter = interruptCounter - 1 
                T_value =  readChannel(ADC_T, PORT_T)
                T = (T_value - self.T_in_min) * (self.T_out_max - self.T_out_min) / (self.T_in_max - self.T_in_min) + self.T_out_min
                
                #print("T: {}".format(T))
                T_data.append(T)
                
                H_value =  readChannel(ADC_H, PORT_H)
                H = (H_value - self.H_in_min) * (self.H_out_max - self.H_out_min) / (self.H_in_max - self.H_in_min) + self.H_out_min
                #print("H: {}".format(H))
                H_data.append(H)
                a+=1
        
        T_mean = np.mean(T_data)
        T_stdev = np.std(T_data)
        H_mean = np.mean(H_data)
        H_stdev = np.std(H_data)
    
        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
        probeTHRData = [T_mean, T_stdev, H_mean, H_stdev]
        #probeData = str(probeData)
        return probeTHRData

class Barometer:
    def __init__(self, P_in_min, P_in_max, P_out_min, P_out_max):
        self.P_in_min = P_in_min
        self.P_in_max = P_in_max
        self.P_out_min = P_out_min
        self.P_out_max = P_out_max

    def read(self, n_data, ADC_P, PORT_P):
        global interruptCounter
        a=0
        while a < n_data:
            if interruptCounter > 0:
                print('Leitura {} de {}'.format(a, n_data))
                interruptCounter = interruptCounter - 1 
                P_value =  readChannel(ADC_P, PORT_P)
                P = (P_value - P_in_min) * (P_out_max - P_out_min) / (P_in_max - P_in_min) + P_out_min
                P_data.append(P)
                
                a+=1
            
            P_mean = np.mean(P_data)
            P_stdev = np.std(P_data)
        
        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
        barometerData = [P_mean, P_stdev]   #List
        return barometerData

class anemometer: 
    def __init__(self, WS_in_min, WS_in_max, WS_out_min, WS_out_max, WD_in_min, WD_in_max, WD_out_min, WD_out_max):
        self.WS_in_min = WS_in_min
        self.WS_in_max = WS_in_max
        self.WS_out_min = WS_out_min
        self.WS_out_max = WS_out_max 
        self.WD_in_min = WD_in_min
        self.WD_in_max = WD_in_max
        self.WD_out_min = WD_out_min
        self.WD_out_max = WD_out_max

    def read(self, n_data, ADC_WS, PORT_WS, ADC_WD, PORT_WD):
        global interruptCounter
        a=0

        while a < n_data:
            if interruptCounter > 0:
                WS_value=readChannel(ADC_WS, PORT_WS)
                WD_value=readChannel(ADC_WD, PORT_WD)
                print("Leitura {} de {}".format(a, n_data))
                interruptCounter = interruptCounter - 1 
                WS = (WS_value - self.WS_in_min) * (self.WS_out_max - self.WS_out_min) / (WS_in_max - self.WS_in_min) + self.WS_out_min
                WS_data.append(WS)
                #print("ws data: {}".format(WS_data))
                WD = (WD_value - self.WD_in_min) * (self.WD_out_max - self.WD_out_min) / (WD_in_max - self.WD_in_min) + self.WD_out_min
                WD_data.append(WD)
                #print("wd data: {}".format(WD_data))
                a+=1
        WS_mean = np.mean(WS_data)
        WS_stdev = np.std(WS_data)
        WD_mean = np.mean(WD_data)
        WD_stdev = np.std(WD_data)
    
        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
        anemometerData = [WS_mean, WS_stdev, WD_mean, WD_stdev]   #List
        print(anemometerData)
        return anemometerData

class InternalTemperature:
    def __init__(self, LM_in_min, LM_in_max, LM_out_min, LM_out_max):
        self.LM_in_min=LM_in_min
        self.LM_in_max=LM_in_max
        self.LM_out_min=LM_out_min
        self.LM_out_max=LM_out_max
        
    def read(self, n_data, ADC, PORT):
        global interruptCounter
        a=0
        while a < n_data: # 60 amostras
            if interruptCounter > 0:
                print("Leitura {} de {}".format(a, n_data))
                interruptCounter = interruptCounter - 1
                LM_value =  readChannel(ADC, PORT)
                LM = (LM_value - self.LM_in_min) * (self.LM_out_max - self.LM_out_min) / (self.LM_in_max - self.LM_in_min) + self.LM_out_min
                print("leitura temperatura int {}".format(LM))
                LM_data.append(LM)
                a+=1

        LM_mean = np.mean(LM_data)
        LM_stdev = np.std(LM_data)
    
        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    
        InternalTempData = [LM_mean, LM_stdev]
        print(InternalTempData)
        return InternalTempData
    
class Compass:
    def __init__(self, uart_ch, BAUDRATE_COMPASS):
        self.uart_ch=uart_ch
        self.baudrate=BAUDRATE_COMPASS


    def get_first_nbr_from_str(self, Compass_info):
        if not input_str and not isinstance(input_str, str):
            return 0
        out_number = ''
        for ele in input_str:
            if (ele == '.' and '.' not in out_number) or ele.isdigit():
                out_number += ele
            elif out_number:
                break
        Compass_data=float(out_number)
        return Compass_data

    def read(self):
        global uart, a, uart_ch, Compass_info
        if Compass_info != None:
            Compass_info=str(Compass_info)
            Compass_info = get_first_nbr_from_str(Compass_info)
            print(Compass_info)
        return Compass_info

class SerialSensor:
    def __init__(self, uart_ch, BAUDRATE):
        self.uart_ch=uart_ch
        self.baudrate=BAUDRATE

    def init(self, n_sec, msg):
        global interruptCounter
        a=0
        select_uart(self.uart_ch, self.baudrate)
        while a < n_sec: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
            uart.write(msg) 
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                data=uart.readline()
                a+=1

    def read(self, n_data, n_val):
        global interruptCounter
        print(type(n_val))
        a=0
        matrix=[]
        while a < n_data: # 60 amostras
            if interruptCounter > 0:
                print("Leitura {} de {}".format(a, n_data))                
                interruptCounter = interruptCounter - 1
                
                data=uart.readline()
                #print("Serial sensor read: {}".format(data))
                #print(type(data))
                
                if data is not None:
                    data_str = data.decode().strip()  # Strip whitespace
                    print(data_str)
                    if data_str:  # Check if the string is not empty
                        x = data_str.split()
                        size = sum(1 for _ in x)
 
                        if size == n_val:  # Check if the split result has the expected length
                            try:
                                x_floats = [float(valor) for valor in x]
                                matrix.append(x_floats)
                                a += 1
                            except ValueError as e:
                                print("Error converting data to float:", e)
                        else:
                            print("Unexpected number of values in data:", x)
                    else:
                        print("Empty data received")
        a=0
        # Envia o comando S para o probe de CO2 para finalizar a leitura
        uart.write("s\r\n")

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

    def send(self, data):
        global interruptCounter
        a=0
        while a < 10: # 5 seguntos de envio 
            uart.write(data) 
            print(data)
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                a+=1

######################################################################################

#criando os sensores seriais + storx

ProbeCO2 = SerialSensor(1, 19200) 
STORX = SerialSensor(0, 9600)  

# criando os sensores analogicos
anemometro = anemometer(WS_in_min, WS_in_max, WS_out_min, WS_out_max, WD_in_min, WD_in_max, WD_out_min, WD_out_max) 
LM35 = InternalTemperature(LM_in_min, LM_in_max, LM_out_min, LM_out_max)
probe_thr = TemperatureHumidityProbe(T_in_min, T_in_max, T_out_min, T_out_max, H_in_min, H_in_max, H_out_min, H_out_max)
barometro = Barometer(P_in_min, P_in_max, P_out_min, P_out_max)

#######################################################################################
############################# FINITE STATE MACHINE ####################################
class State0: #OK
    def __init__(self):
        self.state_index = '0'

    def transition(self, input_var): 
        if input_var == 0:
            return State0()
        elif input_var == 1:
            return StateWait().wait()
        else:
            print('erro')
            return State0()
class StateWait: #OK
    def __init__(self):
        self.state_index = '1'
        
    def transition(self, input_var):
        if input_var == 1:
            return StateWait().wait()
        elif input_var == 2:
            #print("wait => read ok")
            return StateRead().read()
        else:
            print('erro')
            return State0()
        
    def wait(self):
        global input_var
        global interruptCounter

        a=0
        print("state: {}".format(input_var))
        print('going to sleep')

        while a < 10: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
 
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                a+=1

        print('waking up')
        input_var=2
        return StateWait().transition(input_var)     
class StateRead:
    def __init__(self):
        self.state_index='2'

    def transition(self, input_var):
        if input_var == 2:
            return StateRead().read()
        elif input_var == 3:
            return StateSend().send()
        else:
            print('erro')
            return State0()
        
    def read(self):
        global interruptCounter
        global input_var
        global estacao_comma_separated

        
        if input_var == 2:
            #T_value = readChannel_1(ADS1115_COMP_0_GND)
            #H_value = readChannel_1(ADS1115_COMP_1_GND)
            #P_value = readChannel_2(ADS1115_COMP_3_GND)
            #TH_data = TemperatureHumidityRead(T_value, H_value)
            #pressure_data = barometerRead(P_value)
            #WS_value = readChannel_1(ADS1115_COMP_2_GND)
            #WD_value = readChannel_1(ADS1115_COMP_3_GND)

           # PROBE_CO2.inicializar()
            #co2_data = PROBE_CO2.read(n_data)
            #print(co2_data)

            ProbeCO2.init(n_sec,"R\r\n")
            co2_data = ProbeCO2.read(n_data, n_var_co2)
            print(co2_data)
            
            pressure_data = barometro.read(n_data, adc_2, ADS1115_COMP_3_GND)
            print(pressure_data)

            wind_data = anemometro.read(n_data, adc_2, ADS1115_COMP_2_GND, adc_2, ADS1115_COMP_1_GND)

            LM_data = LM35.read(n_data, adc_2, ADS1115_COMP_0_GND)

            probe_thr_data = probe_thr.read(n_data, adc_1, ADS1115_COMP_0_GND, adc_1, ADS1115_COMP_1_GND)
            print(probe_thr_data)

            #uart_ch=2 #bussola
            #select_uart(uart_ch)
        
            #bussola_data = Compass.read(uart.read())
        

            #estacao = wind_data + TH_data + pressure_data + LM_data +co2_data + bussola_data
            estacao =  wind_data  + LM_data + co2_data +  pressure_data + probe_thr_data 

            estacao=str(estacao).strip('[]')   #transforma list em string retirando conchetes da msg

            estacao=[framesync,' '+estacao]              #coloca framesync no inicio da msg
            #estacao=[counterstr,framesync,estacao]        
            #print(estacao)
            estacao_comma_separated = ','.join(estacao)
            print(estacao_comma_separated)
        
            input_var=3
        
        print("state: {}".format(input_var))
        return StateRead().transition(input_var)   
    
class StateSend:
    def __init__(self):
        self.state_index = '3'

    def transition(self, input_var):
        if input_var == 3:
            return StateSend().send()
        elif input_var == 4:
            return StateErase().erase()
        else:
            print('erro')
            return State0()
        
    def send(self):
        global input_var
        global estacao_comma_separated
        
        STORX.init(n_sec,"oi storx\r\n")
        STORX.send(estacao_comma_separated+"\r\n")


        file = open('testeabril.txt', 'a')
        file.write(estacao_comma_separated)
        file.write("\n")
        file.close()
        print("send: {}".format(input_var))
        input_var=4
        return StateSend().transition(input_var) 
class StateErase:
    def __init__(self):
        self.state_index = '4'

    def transition(self, input_var):
        if input_var == 4:
            return StateErase()
        elif input_var == 0:
            return State0()
        else:
            print('erro')
            return State0()
        
    def erase(self):
        global input_var
        WS_data.clear()
        WD_data.clear()
        T_data.clear()
        H_data.clear()
        P_data.clear()
        LM_data.clear()
        co2_data.clear()
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
    #    global input_var
        #print(input_var)
    #    input_var = int(input("Digite um número de 0 a 4 (-1 para sair): "))
    #    if input_var == -1:
    #        break

        # Fazendo a transição de estado com base no input_var
        current_state = current_state.transition(input_var)
        #print("Estado atual:", current_state.state_index)

# Executando a função principal
if __name__ == "__main__":
    main()
