import machine
from machine import Pin, UART, SoftI2C
from ADS1115 import *
import ustruct
from ulab import numpy as np
import random
import gc
import json
from variables import *

config_file = "config.json" 

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

led_debug_1 = Pin(33, mode=Pin.OUT, value=0)

#uart_ch = 0
uart = UART(2, BAUDRATE) #trocar uart no esquemático para a UART 2. A UART 0 é utilizada como UART DOWNLOAD

WS_data = []
WD_data = []
T_data = []
H_data = []
P_data = []
LM_data = []
co2_data=[]


i2c = SoftI2C(scl = Pin(22), sda = Pin(21))


adc_1 = ADS1115(ADS1115_1_ADDRESS, i2c=i2c)
adc_2 = ADS1115(ADS1115_2_ADDRESS, i2c=i2c)

adc_1.setVoltageRange_mV(ADS1115_RANGE_6144)
adc_1.setCompareChannels(ADS1115_COMP_0_GND)
adc_1.setMeasureMode(ADS1115_SINGLE)
adc_2.setVoltageRange_mV(ADS1115_RANGE_6144)
adc_2.setCompareChannels(ADS1115_COMP_0_GND)
adc_2.setMeasureMode(ADS1115_SINGLE) 


timer=machine.Timer(0)

def handlerInterrupt(timer):
    global interruptCounter    
    interruptCounter+=1
    #print("interruptcounter: {}".format(interruptCounter))
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada

#function to save the config dict do the json file
def save_config():
    with open(config_file,"w") as f:
        json.dump(config, f)

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
        #print(BAUDRATE)
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)

    elif uart_ch == 1:
        #BAUDRATE=BAUDRATE_PROBECO2
        uart = UART(2, BAUDRATE)
        #print(BAUDRATE)
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

class Sensor:
    def __init__(self, config):
        self.config = config
     
    def from_config(cls, config_file):
        with open(config_file) as f:
            config = json.load(f)
        
        equipment_class = config.get("className")
        
        if equipment_class == "SerialSensor":
            return SerialSensor(config)
        elif equipment_class == "AnalogSensor":
            return AnalogSensor(config)
        else:
            raise ValueError(f"Unknown equipment className '{equipment_class}'. Cannot instantiate.") 
        
class AnalogSensor(Sensor):
    def __init__(self, config):
        super().__init__(config)
        self.adc=adc
        self.port=port
        self.num_channels = num_variables
        self.channels = [] #duvida
        
        for i in range(num_channels):
            # Initialize channel parameters as desired.
            channel = {
                "ADC":0,
                "PORT":0,
                "param_in_min": 0,
                "param_in_max": 0,
                "param_out_min": 0,
                "param_out_max": 0
            }
            self.channels.append(channel)

    def config_channel(self, channel_index: int, ADC: int, PORT: int, param_in_min: float, param_in_max: float, param_out_min: float, param_out_max: float):
        if 0 <= channel_index < len(self.channels):
            self.channels[channel_index] = {
                "ADC": ADC,
                "PORT": PORT,
                "param_in_min": param_in_min,
                "param_in_max": param_in_max,
                "param_out_min": param_out_min,
                "param_out_max": param_out_max
            }
        # else:
        #     print("Invalid channel index {}. It should be between 0 and {}".format(channel_index, len(self.channels) - 1))

    def read_channel(self, channel_index):
        if 0 <= channel_index < len(self.channels):
            signal = readChannel(self.channels[channel_index]["ADC"], self.channels[channel_index]["PORT"])
            response = (signal - self.channels[channel_index]["param_in_min"]) * (self.channels[channel_index]["param_out_max"] - self.channels[channel_index]["param_out_min"]) / (self.channels[channel_index]["param_in_max"] - self.channels[channel_index]["param_in_min"]) + self.channels[channel_index]["param_out_min"]

            return response
        # else:
        #     print("Invalid channel index {}. It should be between 0 and {}".format(
        #         channel_index, len(self.channels) - 1))
        #     return None

    # def read_all_channels(self):
    #     return self.channels


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

class SerialSensor(Sensor):
    def __init__(self, config):
        super().__init__(config)
        self.uart_ch=uart_ch
        self.baudrate=BAUDRATE

    def init(self, n_sec, msg):
        global interruptCounter
        a=0
        initialize = 0
        select_uart(self.uart_ch, self.baudrate)
        matrix=[]
        while a <= n_sec and initialize == 0: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
             
            if interruptCounter > 0 :
                interruptCounter = interruptCounter - 1
                if msg != " ":
                    print("entrei init, escrevendo R")
                    uart.write(msg)
                    data=uart.readline()
                    
                    if data is not None:
                        print("not None")
                        data_str = data.decode().strip()  # Strip whitespace
                        print(data_str)
                        if data_str:  # Check if the string is not empty
                            print("string not empty")
                            x = data_str.split()
                            size = sum(1 for _ in x)
                            if size == 2:  # Check if the split result has the expected length
                                try:
                                    x_floats = [float(valor) for valor in x]
                                    matrix.append(x_floats)
                                    a+=1
                                    initialize = 1
                                    print(initialize)
                                    
                                except ValueError as e:
                                    print("Error converting data to float:", e)
                                    a+=1
                            else:
                                print("Unexpected number of values in data:", x)
                                a+=1
                        else:
                            print("Empty data received")
                            a+=1
                a+=1

    def read(self, n_data, n_val ):
        global interruptCounter
        print(type(n_val))
        a=0
        matrix=[]
        while a < n_data: # 60 amostras
            if interruptCounter > 0:
                print("Leitura {} de {}".format(a, n_data))                
                interruptCounter = interruptCounter - 1
                
                
                data=uart.readline()
                
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
        while a < 5: # 5 seguntos de envio 

            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                uart.write(data) 
                print(data)
                a+=1

######################################################################################

#criando os sensores seriais + storx

ProbeCO2 = SerialSensor(1, 19200) 
STORX = SerialSensor(0, 9600)  



anemometro = AnalogSensor(2)
anemometro.config_channel(0, adc_2, ADS1115_COMP_2_GND, WS_in_min, WS_in_max, WS_out_min, WS_out_max)
anemometro.config_channel(1, adc_2, ADS1115_COMP_1_GND, WD_in_min, WD_in_max, WD_out_min, WD_out_max)

LM35 = AnalogSensor(1)
LM35.config_channel(0, adc_2, ADS1115_COMP_0_GND, LM_in_min, LM_in_max, LM_out_min, LM_out_max)

probe_thr = AnalogSensor(2)
probe_thr.config_channel(0, adc_1, ADS1115_COMP_0_GND, T_in_min, T_in_max, T_out_min, T_out_max)
probe_thr.config_channel(1, adc_1, ADS1115_COMP_1_GND, H_in_min, H_in_max, H_out_min, H_out_max)

barometro = AnalogSensor(1)
barometro.config_channel(0, adc_2, ADS1115_COMP_3_GND, P_in_min, P_in_max, P_out_min, P_out_max)


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
        a=0
        led_debug_1.value(config["is_led_on"])
        
        if input_var == 2:
            while a < n_data: # 60 amostras
#                 print("oi1")

                if interruptCounter > 0:
                    
                    #toggle led and save to the json file
                    led_debug_1.value(not led_debug_1.value())
                    config["is_led_on"]=led_debug_1.value()
                    save_config()


                    print("Leitura {} de {}".format(a, n_data))
                    
                    interruptCounter = interruptCounter - 1
                    led_debug_1.value(0)
                
                    T = probe_thr.read_channel(0)
                    T_data.append(T)
                    print("T_data: {}".format(T_data))

                    H = probe_thr.read_channel(1)
                    H_data.append(H)
                    print("H_data: {}".format(H_data))
                    
                    LM = LM35.read_channel(0)
                    LM_data.append(LM)
                    print("LM_data: {}".format(LM_data))

                    P = barometro.read_channel(0)
                    P_data.append(P)
                    print("P_data: {}".format(P_data))

                    WS = anemometro.read_channel(0)
                    WS_data.append(WS)
                    print("WS_data: {}".format(WS_data))
                    
                    WD = anemometro.read_channel(1)
                    WD_data.append(WD)                    
                    print("WD_data: {}".format(WD_data))
                    
                    gc.collect() # control of garbage collection
                    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

                    a+=1                    

            #ProbeCO2.init(n_sec,"R\r\n")
            #co2_data = ProbeCO2.read(n_data, n_var_co2)
            
            #print(co2_data)

            T_mean = np.mean(T_data)
            T_stdev = np.std(T_data)            
            T_result=[T_mean,T_stdev]

            H_mean = np.mean(H_data)
            H_stdev = np.std(H_data)
            H_result=[H_mean,H_stdev]

            LM_mean = np.mean(LM_data)
            LM_stdev = np.std(LM_data)
            LM_result=[LM_mean, LM_stdev]

            P_mean = np.mean(P_data)
            P_stdev = np.std(P_data)
            P_result=[P_mean, P_stdev]

            WS_mean = np.mean(WS_data)
            WS_stdev = np.std(WS_data)
            WS_result=[WS_mean, WS_stdev]            
            
            WD_mean = np.mean(WD_data)
            WD_stdev = np.std(WD_data)
            WD_result=[WD_mean,WS_stdev]
    

            #estacao = wind_data + TH_data + pressure_data + LM_data +co2_data + bussola_data
            #estacao =  WS_data + WD_data  + LM_data + P_data + T_data + H_data #+ co2_data +probe_thr_data 
            estacao = T_result + H_result + LM_result + P_result + WS_result + WD_result
            estacao=str(estacao).strip('[]')   #transforma list em string retirando conchetes da msg

            estacao=[config["framesync"],' '+estacao]              #coloca framesync no inicio da msg
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
        
        STORX.init(n_sec," ")
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
        global input_var
        #print(input_var)
        input_var = 1#int(input("Digite um número de 0 a 4 (-1 para sair): "))
        if input_var == -1:
            break

        # Fazendo a transição de estado com base no input_var
        current_state = current_state.transition(input_var)
        #print("Estado atual:", current_state.state_index)

# Executando a função principal
if __name__ == "__main__":
    main()




