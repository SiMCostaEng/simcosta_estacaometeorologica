import machine
from machine import Pin, UART, SoftI2C
from ADS1115 import *
# import ustruct
from ulab import numpy as np
# import random
import gc
from variables import *

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

led_debug_1 = Pin(33, mode=Pin.OUT, value=0)
first_run = 0 # criar condição para que os sensores sejam instanciados apenas 1x no inicio do codigo
instancias = {}
dataloggerinst = {}
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

equipments = equipment_configs

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
        # Define os atributos básicos do sensor a partir da configuração
        self.equipmentName = config['equipmentName']  # Nome do equipamento
        self.num_variables = config.get('num_variables', 0)  # Número de variáveis, default 0
        self.config = config  # Armazena toda a configuração para uso futuro

    def __repr__(self):
        return f"Sensor(equipmentName={self.equipmentName}, num_variables={self.num_variables})"
class AnalogSensor(Sensor):
    def __init__(self, config):
        super().__init__(config) # Inicializa a superclasse
        # Processa canais e outros detalhes específicos de sensores analógicos
        self.equipmentName=config.get("equipmentName")
        self.channels = [] 
#        self.adc=adc
#        self.port=port
        self.num_channels = config.get("num_variables")

        for i in range(self.num_channels):
            #print("")
            self.channels.append({
                "channel_index": config.get(f"channel_index{i}"),
                "adc": config.get(f"adc{i}"),
                "port": config.get(f"port{i}"),
                "P_in_min": config.get(f"P{i}_in_min"),
                "P_in_max": config.get(f"P{i}_in_max"),
                "P_out_min": config.get(f"P{i}_out_min"),
                "P_out_max": config.get(f"P{i}_out_max"),
            })
        #print(type(self.channels)) # <class 'list'>
        
    # def config(self, channel_index: int):
    #     if 0 <= channel_index < len(self.channels):
    #          # Atualiza o canal com base no índice fornecido e na configuração original
    #         self.channels[channel_index] = {
    #             "ADC": ADC,
    #             "PORT": PORT,
    #             "param_in_min": param_in_min,
    #             "param_in_max": param_in_max,
    #             "param_out_min": param_out_min,
    #             "param_out_max": param_out_max
    #         }
    #     else:
    #         print("Invalid channel index {}. It should be between 0 and {}".format(channel_index, len(self.channels) - 1))

    def config(self):
        print("----------entrei no config---------")

        for index, channel in enumerate(self.channels): # Atualiza o canal com base no índice fornecido e na configuração original
            self.channels[index] = {
                "ADC": ADC,
                "PORT": PORT,
                "param_in_min": param_in_min,
                "param_in_max": param_in_max,
                "param_out_min": param_out_min,
                "param_out_max": param_out_max
                }
            
            print("-------------------chanels--------------")
            print(channel)


    def read(self):
        responses={} #dicionario que vai salvar as leituras dos sensores. As keys serão os canais

        for channel in self.channels:
            adc_var=eval(channel["adc"])
            port_cte=eval(channel["port"])

            signal = readChannel(adc_var, port_cte)
            response = (signal - channel["P_in_min"]) * (channel["P_out_max"] - channel["P_out_min"]) / (channel["P_in_max"] - channel["P_in_min"]) + channel["P_out_min"]
            
            print(response)
            print(type(response))

            responses[self.equipmentName]=response

        print(responses)

        return responses
    
    #def process(self):
        
    

class SerialSensor(Sensor):
    def __init__(self, config):
        super().__init__(config)
        self.uart_ch=config.get("uart_ch")
        self.baudrate=BAUDRATE

    def config(self, n_sec, msg):
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


# class Compass:
#     def __init__(self, uart_ch, BAUDRATE_COMPASS):
#         self.uart_ch=uart_ch
#         self.baudrate=BAUDRATE_COMPASS


#     def get_first_nbr_from_str(self, Compass_info):
#         if not input_str and not isinstance(input_str, str):
#             return 0
#         out_number = ''
#         for ele in input_str:
#             if (ele == '.' and '.' not in out_number) or ele.isdigit():
#                 out_number += ele
#             elif out_number:
#                 break
#         Compass_data=float(out_number)
#         return Compass_data

#     def read(self):
#         global uart, a, uart_ch, Compass_info
#         if Compass_info != None:
#             Compass_info=str(Compass_info)
#             Compass_info = get_first_nbr_from_str(Compass_info)
#             print(Compass_info)
#         return Compass_info

class initSensors:
    @staticmethod
    def criar_sensor(config):
        if not isinstance(config, dict):
            raise TypeError(f"Expected config to be a dictionary, got {type(config).__name__} instead.")
      
        equipment_class = config.get("className")
        
        if equipment_class == "SerialSensor":
            return SerialSensor(config)
        elif equipment_class == "AnalogSensor":
            return AnalogSensor(config)
        else:
            raise ValueError(f"Unknown equipment className '{equipment_class}'. Cannot instantiate.") 
        

############################################################################################################
############################# THE DATA ACQUISITION FINITE STATE MACHINE ####################################
class State0: #OK
    def __init__(self,equipments,datalogger, instancias, dataloggerinst):
        global first_run
        if first_run == 0:
            self.instancias = {}
            self.dataloggerinst = {}
            first_run = 1
        else:
            self.instancias=instancias
            self.dataloggerinst=dataloggerinst

        self.state_index = '0'
        self.equipments = equipments
        self.datalogger = datalogger
        self.initSensors = initSensors()

    def transition(self, input_var): 
        if input_var == 0:
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()  # Passar equipamentos
        elif input_var == 1:
            return StateWait(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).wait()  # Passar equipamentos e instâncias
        else:
            print('erro')
            return State0(self.equipments, self.datalogger).init_equipments()
        
    def init_equipments(self):
        for equip, equip_info in self.equipments.items():
            try:
                equipment = initSensors.criar_sensor(equip_info)
                self.instancias[equip] = equipment
                print(f"{equip} instanciado com sucesso.")
            except ValueError as e:
                print(f"Erro ao criar o equipamento: {e}")

        print(type(self.equipments))
        print(type(self.datalogger))

        for data, data_info in self.datalogger.items():
            try:
                main_datalogger = initSensors.criar_sensor(data_info)

                self.dataloggerinst[data] = main_datalogger

                print("AOOOOOOOOOOO")
                print(self.dataloggerinst)
                print(f"{data} instanciado com sucesso.")
            except ValueError as e:
                print(f"Erro ao criar o equipamento: {e}")

        # print(self.dataloggerinst)
        input_var = 1
        return State0(self.equipments,self.datalogger,self.instancias, self.dataloggerinst).transition(input_var)

class StateWait: #OK
    def __init__(self,equipments,instancias, datalogger,dataloggerinst):
        self.state_index = '1'
        self.equipments = equipments
        self.instancias = instancias
        self.datalogger=datalogger
        self.dataloggerinst=dataloggerinst
        
    def transition(self, input_var):
        if input_var == 1:
            return StateWait(self.equipments, self.instancias,self.datalogger, self.dataloggerinst).wait()
        elif input_var == 2:
            return StateRead(self.equipments, self.instancias,self.datalogger,self.dataloggerinst).read()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
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
        return StateWait(self.equipments,self.datalogger, self.instancias,self.dataloggerinst).transition(input_var)
        
class StateRead:
    def __init__(self,equipments, instancias, datalogger, dataloggerinst):
        self.state_index='2'
        self.equipments = equipments
        self.instancias = instancias
        self.datalogger = datalogger
        self.dataloggerinst=dataloggerinst

    def transition(self, input_var):
        if input_var == 2:
            return StateRead(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).read()
        elif input_var == 3:
            return StateSend(self.datalogger, self.dataloggerinst, self.equipments).send()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
    def read(self):
        global interruptCounter
        global input_var
        global estacao_comma_separated
        a=0
        led_debug_1.value(config["is_led_on"])

        if input_var == 2:
            while a < n_data: # 60 amostras
                if interruptCounter > 0:
                #toggle led and save to the json file
                    led_debug_1.value(not led_debug_1.value())
                    config["is_led_on"]=led_debug_1.value()
                    save_config()

                    print("Leitura {} de {}".format(a, n_data))
                    # Diagnóstico: Verificar o conteúdo de self.instancias
                    # print("Instâncias disponíveis:", self.instancias)

                    for nome, equipment in self.instancias.items():
                        if isinstance(equipment, AnalogSensor):
                            # print("Equipment type: AnalogSensor")
                            # print(" equipment type: {}".format(type(equipment)))
                            #print(f"Métodos disponíveis para {nome}: {dir(equipment)}")
                            #equipment.config()
                            print(equipment)
                            equipment.read()
                        #else:
                        #    (f"Erro: {nome} não tem um método 'config' válido.")
                        elif isinstance(equipment, SerialSensor):
                            print("Equipment type: SerialSensor")
                            #equipment.config()  # Chama o método read da classe SerialSensor
                            #equipment.read()

                        #else:
                         #   (f"Erro: {nome} não tem um método 'config' válido.") 
                        else:
                            print(f"{nome} não é do tipo AnalogSensor ou SerialSensor. Ignorando...")


                    interruptCounter = interruptCounter - 1
                    led_debug_1.value(0)
                    a+=1

            #estacao = wind_data + TH_data + pressure_data + LM_data +co2_data + bussola_data
            #estacao =  WS_data + WD_data  + LM_data + P_data + T_data + H_data #+ co2_data +probe_thr_data 
            estacao = "1"#T_result + H_result + LM_result + P_result + WS_result + WD_result
            estacao=str(estacao).strip('[]')   #transforma list em string retirando conchetes da msg

            estacao=[framesync,' '+estacao]              #coloca framesync no inicio da msg
            #estacao=[counterstr,framesync,estacao]        
            #print(estacao)
            estacao_comma_separated = ','.join(estacao)
            print(estacao_comma_separated)
        
            input_var=3
        
        print("state: {}".format(input_var))
        return StateRead(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).transition(input_var)
         
class StateSend:
    def __init__(self, datalogger, dataloggerinst, equipments):
        self.state_index = '3'
        self.datalogger = datalogger
        self.dataloggerinst=dataloggerinst
        self.equipments = equipments

    def transition(self, input_var):
        if input_var == 3:
            return StateSend(self.datalogger, self.dataloggerinst, self.equipments).send()
        elif input_var == 4:
            return StateErase(self.equipments, self.datalogger).erase()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
    def send(self):
        global input_var
        global estacao_comma_separated

        for nome, self.main_datalogger in self.dataloggerinst.items():
            #print(f"Processando {nome}: {equipment}")
            if isinstance(self.main_datalogger, SerialSensor):
                        #print(f"Lendo dados do sensor {nome}... {equipment}")
                        #if hasattr(equipment, 'config') and callable(getattr(equipment, 'config')):
                print("******************************")
                main_datalogger.init(n_sec," ")
                main_datalogger.send(estacao_comma_separated+"\r\n")
            else:
                print(f" O datalogger {nome} não foi instanciado. Ignorando...")
    
        file = open('testeabril.txt', 'a')
        file.write(estacao_comma_separated)
        file.write("\n")
        file.close()
        print("send: {}".format(input_var))
        input_var=4
        return StateSend(self.datalogger, self.dataloggerinst, self.equipments).transition(input_var) 
    
class StateErase:
    def __init__(self, equipments, datalogger):
        self.state_index = '4'
        self.datalogger = datalogger
        self.equipments = equipments

    def transition(self, input_var):
        if input_var == 4:
            return StateErase(self.equipments, self.datalogger).erase()
        elif input_var == 0:
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
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
        return StateErase(self.equipments, self.datalogger).transition(input_var)

#######################################################################################
# Função principal do programa

def main():
    # Inicializando a máquina de estados com o estado 0
    current_state = State0(equipments, datalogger, instancias, dataloggerinst)

    while True:
        global input_var
        #print(input_var)
        input_var = 0
        #int(input("Digite um número de 0 a 4 (-1 para sair): "))
        if input_var == -1:
            break

        # Fazendo a transição de estado com base no input_var
        current_state = current_state.transition(input_var)
        #print("Estado atual:", current_state.state_index)

# Executando a função principal
if __name__ == "__main__":
    main()