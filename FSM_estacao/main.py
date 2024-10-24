import machine
from machine import Pin, UART, SoftI2C
from ADS1115 import *
# import ustruct
from ulab import numpy as np
# import random
import gc
from variables import *
import time
import math 

# start_time = time.ticks_us()
# end_time=0

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

led_debug_1 = Pin(33, mode=Pin.OUT, value=0)
led_debug_2 = Pin(32, mode=Pin.OUT, value=0)

first_run = 0 # criar condição para que os sensores sejam instanciados apenas 1x no inicio do codigo
instancias = {}
dataloggerinst = {}
#uart_ch = 0
uart = UART(2, BAUDRATE) #trocar uart no esquemático para a UART 2. A UART 0 é utilizada como UART DOWNLOAD

responses = {}
resultadoSerial = {}
initialize = 0
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
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)
        uart = UART(2, BAUDRATE)
        #uart.write("\r")
        uart.flush()  # Garante que o comando foi enviado completamente

    elif uart_ch == 1:
        #BAUDRATE=BAUDRATE_PROBECO2
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
        uart = UART(2, BAUDRATE)
        #uart.write("\r")
        uart.flush()  # Garante que o comando foi enviado completamente
                
    elif uart_ch == 2:
        #BAUDRATE=BAUDRATE_COMPASS
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)
        uart = UART(2, BAUDRATE)
        #uart.write("\r")
        uart.flush()  # Garante que o comando foi enviado completamente

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)
        uart = UART(2, BAUDRATE)
        #uart.write("\r")
        uart.flush()  # Garante que o comando foi enviado completamente


# Função para achatar a lista manualmente
def achatar_lista(lista):
    lista_achatada = []
    for sublista in lista:
        for item in sublista:
            lista_achatada.append(item)
    return lista_achatada
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
        self.num_channels = config.get("num_variables")

        for i in range(self.num_channels):
            #print("")
            self.channels.append({
                "channel_index": config.get(f"channel_index{i}"),
                "adc": config.get(f"adc{i}"),
                "port": config.get(f"port{i}"),
                "type":config.get(f"type{i}"),
                "P_in_min": config.get(f"P{i}_in_min"),
                "P_in_max": config.get(f"P{i}_in_max"),
                "P_out_min": config.get(f"P{i}_out_min"),
                "P_out_max": config.get(f"P{i}_out_max"),
            })
            

    def read(self):
        global responses #dicionario que vai salvar as leituras dos sensores. As keys serão os canais

        for channel in self.channels:
            adc_var=eval(channel["adc"])
            port_cte=eval(channel["port"])
            type = channel["type"]

            signal = readChannel(adc_var, port_cte)
            response = (signal - channel["P_in_min"]) * (channel["P_out_max"] - channel["P_out_min"]) / (channel["P_in_max"] - channel["P_in_min"]) + channel["P_out_min"]
            
            key = type + "_" + self.equipmentName + "_" + str(channel["channel_index"])
            #print(key)
            if key not in responses:
                responses[key]=[]
            responses[key].append(response)
            
            gc.collect() # control of garbage collection
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        
        return responses
    
    def process(self, responses):
        data_processed={}

        for key in responses:

            if key.startswith("angular"):
                sin_sum = 0.0
                cos_sum = 0.0
                angles = responses[key]
                print(angles)

                # Somar seno e cosseno dos ângulos
                for angle in angles:
                    r = math.radians(angle)  # Converter para radianos
                    sin_sum += math.sin(r)
                    cos_sum += math.cos(r)

                flen = float(len(angles))
                s = sin_sum / flen
                c = cos_sum / flen
                arc = math.degrees(math.atan2(s, c))  # Usar atan2 para garantir o quadrante correto
                average = arc % 360  # Garantir que o resultado esteja no intervalo [0, 360)

                # Cálculo do desvio padrão
                sin_std_sum = 0.0
                cos_std_sum = 0.0

                for angle in angles:
                    r = math.radians(angle)
                    sin_std_sum += (math.sin(r) - s) ** 2
                    cos_std_sum += (math.cos(r) - c) ** 2

                sin_variance = sin_std_sum / flen
                cos_variance = cos_std_sum / flen

                # A variância angular é a soma das variâncias dos componentes seno e cosseno
                angular_variance = sin_variance + cos_variance
                angular_std_dev = math.sqrt(angular_variance)


                data_mean = average
                data_stdv = math.degrees(angular_std_dev)

            else: #linear
                data_mean=np.mean(responses[key])
                data_stdv=np.std(responses[key])

            if key not in data_processed:
                data_processed[key]=[]

            data_processed[key].append(data_mean)
            data_processed[key].append(data_stdv)

            gc.collect() # control of garbage collection
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        return data_processed
 

class SerialSensor(Sensor):
    def __init__(self, config):
        super().__init__(config)
        self.equipmentName=config.get("equipmentName")
        self.uart_ch=config.get("uart_ch")
        self.baudrate=config.get("BAUDRATE")
        self.time_config=config.get("time_config")
        self.wakeup_msg=config.get("wakeup_msg")
        self.n_var = config.get("num_variables")



    def init(self):
        global interruptCounter
        a=0
        global initialize
        select_uart(self.uart_ch, self.baudrate)
        matrix=[]
        while a < self.time_config and initialize == 0: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
            if interruptCounter > 0 :
                interruptCounter = interruptCounter - 1
                if self.wakeup_msg != " ":
                    print("entrei init, escrevendo R")
                    uart.write(self.wakeup_msg)
                    uart.flush()  # Garante que o comando foi enviado completamente e Limpa o buffer antes de esperar novos dados
                    data=uart.readline()
                    print(data)
                    if data is not None:
                        data_str = data.decode().strip()  # Strip whitespace errors='ignore'
                        if data_str:  # Check if the string is not empty
                            #print("string not empty")
                            x = data_str.split()
                            size = sum(1 for _ in x)
                            if size == 2:  # Check if the split result has the expected length
                                try:
                                    x_floats = [float(valor) for valor in x]
                                    matrix.append(x_floats)
                                    print("Sensor {} has been successfully initialized!".format(self.equipmentName))
                                    initialize = 1
                                    a+=1

                                except ValueError as e:
                                    print("Error converting data to float:", e)
                                    a+=1
                            else:
                                print("Unexpected number of values in data:", x)
                                a+=1
                        else:
                            print("Empty data received")
                            a+=1


    def read(self):
        global interruptCounter
        global resultadoSerial
        uart.flush()  # Limpa o buffer antes de esperar novos dados
        data=uart.readline()
        matrix=[]
        x_floats=[]
                
        if data is not None:
            try: 
                data_str = data.decode().strip()  # Strip whitespace
                #print(data_str)
                if data_str:  # Check if the string is not empty
                    x = data_str.split()
                    size = sum(1 for _ in x)
    
                    if size == self.n_var:  # Check if the split result has the expected length
                        try:
                            x_floats = [float(valor) for valor in x]
                            matrix.append(x_floats)
                        except ValueError as e:
                            print("Error converting data to float:", e)
                    else:
                        print("Unexpected number of values in data:", x)
                else:
                    print("Empty data received")
            except:
                pass

        # Criar um dicionário para armazenar as leituras com o formato equipmentName_index
        
        for i, value in enumerate(x_floats, 1):
            key = f"{self.equipmentName}_{i}"
            if key not in resultadoSerial:
                resultadoSerial[key] = []  # Inicializa a lista se for a primeira leitura
            resultadoSerial[key].append(value)  # Adiciona a nova leitura à lista correspondente


        gc.collect()  # Controle da coleta de lixo
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        return resultadoSerial

    def process (self, responses):
        data_processed={}
        for key in responses:
            data_mean=np.mean(responses[key])
            data_stdv=np.std(responses[key])

            if key not in data_processed:
                data_processed[key]=[]

            data_processed[key].append(data_mean)
            data_processed[key].append(data_stdv)

            gc.collect() # control of garbage collection
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        return data_processed

    def send(self, data):
        global interruptCounter
        select_uart(self.uart_ch, self.baudrate)# select_uart(self.uart_ch, self.baudrate)

        a=0

        while a < self.time_config: # x segundos de envio definidos no json
            if interruptCounter > 0:
                interruptCounter = interruptCounter - 1
                uart.write(data)
                uart.flush()  # Garante que o comando foi enviado completamente
                print(data)
                print("a={}".format(a))
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

        for data, data_info in self.datalogger.items():
            try:
                main_datalogger = initSensors.criar_sensor(data_info)
                self.dataloggerinst[data] = main_datalogger

                print(f"{data} instanciado com sucesso.")
            except ValueError as e:
                print(f"Erro ao criar o equipamento: {e}")

        # print(self.dataloggerinst)
        input_var = 1
        return State0(self.equipments,self.datalogger,self.instancias, self.dataloggerinst).transition(input_var)

class StateWait: #OK
    def __init__(self, equipments, datalogger, instancias, dataloggerinst):
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

        while a < 10: # 10 seguntos de espera
            if interruptCounter > 0:                       
                interruptCounter = interruptCounter - 1
                print("sleep {}".format(a))
                a+=1

        for nome, equipment in self.instancias.items():
            print("teste1")
            if isinstance(equipment, SerialSensor):
                print("é serial {}".format(equipment))
                equipment.init()  # Chama o método config da classe SerialSensor
                print("iniciei {}".format(equipment))

        print('waking up')
        input_var=2
        return StateWait(self.equipments,self.datalogger, self.instancias,self.dataloggerinst).transition(input_var)
        
class StateRead:
    def __init__(self, equipments, instancias, datalogger, dataloggerinst):
        self.state_index='2'
        self.equipments = equipments
        self.instancias = instancias
        self.datalogger = datalogger
        self.dataloggerinst = dataloggerinst

    def transition(self, input_var):
        if input_var == 2:
            return StateRead(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).read()
        elif input_var == 3:
            return StateSend(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).send()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
    def read(self):
        global interruptCounter
        global input_var
        global estacao_comma_separated

            # Inicializando as variáveis fora do loop
        analog_data = {}
        serial_data = {}
        a=0
        led_debug_1.value(config["is_led_1_on"])

        if input_var == 2:
            while a < n_data: # 60 amostras
                if interruptCounter > 0:
                #toggle led and save to the json file
                    led_debug_1.value(not led_debug_1.value())
                    config["is_led_1_on"]=led_debug_1.value()
                    save_config()

                    print("Leitura {} de {}".format(a, n_data))
                    # Diagnóstico: Verificar o conteúdo de self.instancias
                    # print("Instâncias disponíveis:", self.instancias)

                    for nome, equipment in self.instancias.items():
                        if isinstance(equipment, AnalogSensor):
                            analog_data=equipment.read()
                            
                            # for key, respostas in analog_data.items():
                            #     size = len(respostas)
                            # print(f"A chave '{key}' tem {size} respostas.")    
                            
                        #else:
                        #    (f"Erro: {nome} não tem um método 'config' válido.")
                        elif isinstance(equipment, SerialSensor):
                            #print("serial type: {}".format(type(equipment)))
                            serial_data=equipment.read()


                            # print("equipment:{}".format(equipment))
                            # print(dir(equipment))
                            #equipment.init()  # Chama o método config da classe SerialSensor
                            #equipment.read()

                        #else:
                         #   (f"Erro: {nome} não tem um método 'config' válido.") 
                        else:
                            print(f"{nome} não é do tipo AnalogSensor ou SerialSensor. Ignorando...")


                    interruptCounter = interruptCounter - 1
                    led_debug_1.value(0)
                    a+=1

            # for chave, respostas in serial_data.items():
            #     quantidade_respostas = len(respostas)
            # print(f"A chave '{chave}' tem {quantidade_respostas} respostas.")

            # Processamento seguro: se não houver dados, cria um dicionário vazio
            analog_data_processed = equipment.process(analog_data) if analog_data else {}
            serial_data_processed = equipment.process(serial_data) if serial_data else {}

            estacao = analog_data_processed | serial_data_processed #T_result + H_result + LM_result + P_result + WS_result + WD_result
            
            #estacao_round = {key: round(value,3) for key, value in estacao.items()}
            #print(estacao_round)
            print(f"estacao: {estacao}")
            chaves_ordenadas = sorted(estacao.keys())
            print(f"chaves_ordenadas: {CH_A_MUX}")
            valores_ordenados = [estacao[chave] for chave in chaves_ordenadas]
            print(f"valores_ordenados: {valores_ordenados}")
            # Achatar a lista aninhada
            valores_achatados = achatar_lista(valores_ordenados)
            print(f"valores_achatados: {valores_achatados}")
            valores_round=[round(value, decimal) for value in valores_achatados]
            print(f"valores_round: {valores_round}")
 
            # Converter para string e formatar
            estacao = ', '.join(map(str, valores_round))

            estacao=[framesync,' ' + estacao]              #coloca framesync no inicio da msg

            estacao_comma_separated = ','.join(estacao)
            print(estacao_comma_separated)
        
            input_var=3
        
        print("state: {}".format(input_var))
        return StateRead(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).transition(input_var)
         
class StateSend:
    def __init__(self, equipments, instancias, datalogger,dataloggerinst):
        self.state_index = '3'
        self.datalogger = datalogger
        self.dataloggerinst=dataloggerinst
        self.equipments = equipments
        self.instancias=instancias

    def transition(self, input_var):
        if input_var == 3:
            return StateSend(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).send()
        elif input_var == 4:
            return StateErase(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).erase()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
    def send(self):
        global input_var
        global estacao_comma_separated


        for nome, self.main_datalogger in self.dataloggerinst.items():
            #print(f"Processando {nome}: {equipment}")
            if isinstance(self.main_datalogger, SerialSensor):
                self.main_datalogger.send(estacao_comma_separated+"\r\n")
            else:
                print(f" O datalogger {nome} não foi instanciado. Ignorando...")
    
        file = open('teste1.txt', 'a')
        file.write(estacao_comma_separated)
        file.write("\n")
        file.close()

        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        print("send: {}".format(input_var))
        input_var=4
        return StateSend(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).transition(input_var) 
    
class StateErase:
    def __init__(self, equipments, instancias, datalogger,dataloggerinst):
        self.state_index = '4'
        self.datalogger = datalogger
        self.equipments = equipments
        self.instancias=instancias
        self.dataloggerinst=dataloggerinst

    def transition(self, input_var):
        if input_var == 4:
            return StateErase(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).erase()
        elif input_var == 0:
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        else:
            print('erro')
            return State0(self.equipments, self.datalogger, self.instancias, self.dataloggerinst).init_equipments()
        
    def erase(self):
        global input_var
        global responses
        global resultadoSerial

        
        print("erase 1: {}".format(input_var))
        input_var=0
        
        responses.clear()
        resultadoSerial.clear()

        gc.collect() # control of garbage collection
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        print("erase 2: {}".format(input_var))
        # end_time=time.ticks_us()

        # elapsed_time = time.ticks_diff(end_time, start_time)
        # print("tempo de execução: {}".format(elapsed_time))
        
        return StateErase(self.equipments, self.instancias, self.datalogger, self.dataloggerinst).transition(input_var)

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