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
import re

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
        print(f"uart {uart_ch}  opened")
        uart = UART(2, BAUDRATE)
        while uart.any():
            uart.read()  # Lê todos os dados e descartaclear_uart_buffer(uart)
        #uart.write("\r")
        #uart.flush()  # Garante que o comando foi enviado completamente

    elif uart_ch == 1:
        #BAUDRATE=BAUDRATE_PROBECO2
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
        print(f"uart {uart_ch}  opened")
        uart = UART(2, BAUDRATE)
        #uart.write("\r")
        while uart.any():
            uart.read()  # Lê todos os dados e descartaclear_uart_buffer(uart)
        #uart.flush()  # Garante que o comando foi enviado completamente
                
    elif uart_ch == 2:
        #BAUDRATE=BAUDRATE_COMPASS
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)
        print(f"uart {uart_ch}  opened")
        uart = UART(2, BAUDRATE)
        while uart.any():
            uart.read()  # Lê todos os dados e descartaclear_uart_buffer(uart)
        #uart.write("\r")
        #uart.flush()  # Garante que o comando foi enviado completamente

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)
        print(f"uart {uart_ch}  opened")
        uart = UART(2, BAUDRATE)
        while uart.any():
            uart.read()  # Lê todos os dados e descartaclear_uart_buffer(uart)
        #uart.write("\r")
        #uart.flush()  # Garante que o comando foi enviado completamente
    config["CURRENT_UART"]=uart_ch
    save_config()
    # print(config["CURRENT_UART"])

# def clear_uart_buffer(uart):
#     global interruptCounter
#     a=0
#     """Ler e descartar todos os dados no buffer da UART."""
#     while uart.any():
#         uart.read()  # Lê todos os dados e descarta
#         print("limpa, limpa, limpa tudo!")
    
#     while a < 1:
#         if interruptCounter > 0:
#             interruptCounter = interruptCounter - 1  # Pequeno atraso para garantir que o buffer esteja limpo
#             a+=1

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
        self.initialized=config.get("initialized")
        self.format=config.get("format")
        self.checksum_type=config.get("checksum_type")
        self.checksum_format=config.get("checksum_format")
        self.vars=[]
        self.resultadoSerial={}

        for i in range(self.n_var):
            self.vars.append({
                "var": config.get(f"var_{i}"),
            })
            
    def checksum_evaluate(self, s:str) -> int:
        # Converte a string em bytes e calcula a soma de cada byte
        # Calcula o checksum de acordo com o tipo e formato determinado no JSON
        if self.checksum_type == "MOD256":
            mysum = sum(s.encode('utf-8'))  # Soma os valores dos bytesmysum = sum(s)  # soma dos valores dos bytes
            return mysum % 256  # retorna o checksum (mod 256 para limitar ao intervalo de um byte)
            
        elif self.checksum_type == "XOR":
            checksum = 0
            for byte in s:
                checksum ^= ord(byte)

            if self.checksum_format == "dec":
                return checksum
            elif self.checksum_format == "hex":
                return f"{checksum:02X}"  # Retorna o checksum em hexadecimal (2 caracteres)


    def checksum_verify(self, s: str) -> bool:
        """Verifica se o checksum da string é válido. A string deve ter o formato 'conteudo*checksum'."""

        try:
            # Verifica se a string contém o caractere '*'
            if '*' not in s:
                print("Erro: '*' não encontrado na string.")
                return False

            if s.startswith(b'$'):
                s=s[1:] #remover $
                # print(f"s:{s}")
            
            # Separar a parte principal e o checksum fornecido
            if isinstance(s,bytes):
                conteudo, checksum = s.decode().rsplit('*', 1)
            elif isinstance(s,str):
                conteudo, checksum = s.rsplit('*', 1)
            else:
                print("String de formato desconhecido")
            
            if self.checksum_type=="MOD256":          
            # Verificar se o checksum fornecido é numérico
                if not checksum.isdigit():
                    print("Erro: O checksum fornecido não é numérico.")
                    return False
                # Calcular o checksum da parte principal
                checksum_calculado = self.checksum_evaluate(conteudo.strip())
                return checksum_calculado == int(checksum.strip())
            
            elif self.checksum_type=="XOR":
                checksum_calculado = self.checksum_evaluate(conteudo)
                return checksum_calculado.upper() == checksum.strip().upper()

        except Exception as e:
            # Caso algum erro inesperado aconteça
            print(f"Erro ao verificar checksum: {e}")
            return False
        

    def init(self):
        global interruptCounter
        a=0

        select_uart(self.uart_ch, self.baudrate)
        matrix=[]
        while a <= self.time_config and self.initialized == 0: # 10 seguntos de envio para ler o sensor
            # Envia o comando R para o probe de CO2 para iniciar a leitura
            if interruptCounter > 0 :
                interruptCounter = interruptCounter - 1
                if self.wakeup_msg != " ":
                    #print("entrei init, escrevendo R")
                    uart.write(self.wakeup_msg)
 #                   uart.flush()  # Garante que o comando foi enviado completamente e Limpa o buffer antes de esperar novos dados
                    data=uart.readline()
                    print(f"data is: {data}")
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
                                    
                                    #aqui adicionar a inicialização do dicionario
                                    for i in range(1, self.n_var + 1):  # Defina `numero_de_leituras` conforme necessário
                                        key = f"{self.equipmentName}_{i}"
                                        self.resultadoSerial[key] = []  # Define o valor inicial como 
                                    print(self.resultadoSerial)

                                    
                                    print("Sensor {} has been successfully initialized!".format(self.equipmentName))
                                    self.initialized = 1
                                    print(f"init: {self.initialized}")
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
        if a== self.time_config and initialize == 0:
            print("Station was unable to initialize {}".format(self.equipmentName))
        
        if self.initialized == 2:
            print("No initialization message needed...")
            for i in range(1, self.n_var + 1):  # Defina `numero_de_leituras` conforme necessário
                key = f"{self.equipmentName}_{i}"
                self.resultadoSerial[key] = []  # Define o valor inicial como 
            print(self.resultadoSerial)

    def read(self):
        global interruptCounter
        #global resultadoSerial

        #print(f"current uart: {config["CURRENT_UART"]}")
        #print(f"uart do sensor: {self.uart_ch}")
        if config["CURRENT_UART"] != self.uart_ch:
        #    print("mudei")
            select_uart(self.uart_ch, self.baudrate)
            config["CURRENT_UART"]=self.uart_ch
        #    print(config["CURRENT_UART"])
        # else:
        #     print("nothing changed...")
        #     print(config["CURRENT_UART"])

        
        #uart.flush()  # Limpa o buffer antes de esperar novos dados
        data=uart.readline()
        #print("###")
        #print(data)
        #matrix=[]
        x_floats=[]



        if self.format == "ASCII":
            #print("é ASCII")
            #print(data) #b'  605.6    26.6\r\n'
            #print(type(data))
            if data is not None:
                try: 
                    data_str = data.decode().strip()  # Strip whitespace
                    #print(data_str) #605.6    26.5
                    if data_str:  # Check if the string is not empty
                        x = data_str.split()
                        #print(x) #['605.6', '26.5']
                        size = sum(1 for _ in x)
        
                        if size == self.n_var:  # Check if the split result has the expected length
                            try:
                                x_floats = [float(valor) for valor in x]
                                #print(f"x_floats={x_floats}")
                                #matrix.append(x_floats)
                            except ValueError as e:
                                print("Error converting data to float:", e)
                        else:
                            print("Unexpected number of values in data:", x)
                    else:
                        print("Empty data received")
                except:
                    pass

            #if self.initialized:# Verifica se o sensor falhou ao inicializar
            # Criar um dicionário para armazenar as leituras com o formato equipmentName_index
            for i, value in enumerate(x_floats, 1):
                key = f"{self.equipmentName}_{i}"
                #print(key)
                self.resultadoSerial[key].append(value)  # Adiciona a nova leitura à lista correspondente
                #print(self.resultadoSerial)


        elif self.format == "NMEA":
            #print(data)
            #print(type(data)) #bytes
            if data is not None:
                if self.checksum_verify(data):
                    #print(f"checksum is ok? {self.checksum_verify(data)}")

                    cleaned_data = bytes([b for b in data if 32 <= b <= 126 or b in (10, 13)])
                    
                    try:
                        # Tentar decodificar os bytes limpos
                        decoded_data = cleaned_data.decode('utf-8') 
                        #decoded_data = decoded_data.decode().strip("$*")  # Strip whitespace
                        #print(f"decoded data:{decoded_data}")
                        #print(type(decoded_data)) #str
                    except UnicodeDecodeError:
                        # Se falhar, retorne uma string vazia
                        return ''

                        #x_floats = re.findall(r'\d+\.\d+',data)
                        #x_floats = [float(x_float) for x_float in x_floats] 
                    #data_str=str(data)
                    
                    caracteres_para_substituir=["P","T","R","*"]
                    c=["$","b","'","C"]

                    for char in caracteres_para_substituir:
                        decoded_data=decoded_data.replace(char,",")
                        #print(decoded_data)
                    #data_str = data.decode().strip()  # Strip whitespace
                    # data_str = data_str.strip("$*")
                    for char in c:
                        decoded_data=decoded_data.replace(char,"")
                    
                    #print(decoded_data)
                    if decoded_data:  # Check if the string is not empty
                        x = decoded_data.split(',')

                        try:
                            x_floats = [float(valor) for valor in x[:self.n_var]]
                            size=len(x_floats)
                            
                            if size != self.n_var:
                                print("Unexpected number of values in data")
                            
                            #matrix.append(x_floats)
                        
                        except ValueError as e:
                            print("Error converting data to float:", e)
                    else:
                        print("Empty data received")
                else:
                    print("Checksum doesn't match")
                            # Criar um dicionário para armazenar as leituras com o formato equipmentName_index
            
            for i, value in enumerate(x_floats, 1):
                key = f"{self.equipmentName}_{i}"
                #print(key)
                #print(self.resultadoSerial)
                self.resultadoSerial[key].append(value)  # Adiciona a nova leitura à lista correspondente
            
            
        else:
            print("Couldn't recognize the format.")


        gc.collect()  # Controle da coleta de lixo
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

        return self.resultadoSerial

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

  
        data=data.strip()
        # print(f"data strip:{data}")
        #adicionando checksum à string para envio
        checksum = self.checksum_evaluate(data)
        # print(f"meu checksum:{checksum}")

        
        string_final = data + "*" + str(checksum)

        # print(f"string_final:{string_final}")
        # Dividir no caractere '*', remover espaços e reconstruir
        # conteudo, checksum = string_final.rsplit('*', 1)
        # s_corrigida = f"{conteudo.strip()}*{checksum.strip()}"
        # print(f"s_corrigida: {s_corrigida}")
        # if self.checksum_verify(s_corrigida):
        if self.checksum_verify(string_final):
            #print(f"verify: {self.checksum_verify(string_final)}")

            while a < self.time_config: # x segundos de envio definidos no json
                if interruptCounter > 0:
                    interruptCounter = interruptCounter - 1
                    uart.write(string_final)
                    #ndata=uart.write(data)
                    #print(f"ndata={ndata}")
                    uart.flush()  # Garante que o comando foi enviado completamente
                    print(f"string enviada: {string_final}")
                    #print("a={}".format(a))
                    a+=1


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

        while a < 20: # 10 seguntos de espera
            if interruptCounter > 0:                       
                interruptCounter = interruptCounter - 1
                print("sleeping for... {}".format(a))
                a+=1

        for nome, equipment in self.instancias.items():
            #print("teste1")
            if isinstance(equipment, SerialSensor):
                #print("é serial {}".format(equipment))
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
            #leitura sensores analógicos
            while a < n_data:
                if interruptCounter > 0:
                    #toggle led and save to the json file
                    led_debug_1.value(not led_debug_1.value())
                    config["is_led_1_on"]=led_debug_1.value()
                    save_config()
                    for nome, equipment in self.instancias.items():
                        if isinstance(equipment, AnalogSensor):
                            analog_data=equipment.read()
                    #print("Leitura {} de {} de sensor do tipo {}".format(a, n_data, type(equipment)))
                    interruptCounter = interruptCounter - 1
                    led_debug_1.value(0)
                    if a==(n_data-1):
                        print("Done!")
                    a+=1
                    
            a=0
            #leitura sensores seriais

            for name, equipment in self.instancias.items():
                if isinstance(equipment,SerialSensor):

                    while a<n_data:
                        #print("oi")
                        if interruptCounter >0:
                            led_debug_1.value(not led_debug_1.value())
                            config["is_led_1_on"]=led_debug_1.value()
                            save_config()

                            #print("Leitura {} de {} de sensor do tipo {}".format(a, n_data, type(equipment)))
                            serial_data=equipment.read()|serial_data
                            
                            #
                            print(f"serial {equipment}:{serial_data}")
                            #print(f"tipo serial dada: {type(serial_data)}") #dict
                            interruptCounter = interruptCounter - 1
                            led_debug_1.value(0)
                            #print(f"a={a}")
                            a=a+1
                            
            
                            if a==n_data:
                                if any(len(value) < n_data for value in serial_data.values()):
                                    print("nao tenho a quantidade certa")
                                    #print(f"a={a}")
                                    a=a-1
                                    #print(f"new a={a}")
                                else:
                                    print("All done!")
                    a=0
         

            analog_data_processed = equipment.process(analog_data) if analog_data else {}
            serial_data_processed = equipment.process(serial_data) if serial_data else {}

            estacao = analog_data_processed | serial_data_processed #T_result + H_result + LM_result + P_result + WS_result + WD_result
            
            #estacao_round = {key: round(value,3) for key, value in estacao.items()}
            #print(estacao_round)
            #print(f"estacao: {estacao}")
            chaves_ordenadas = sorted(estacao.keys())
            #print(f"chaves_ordenadas: {chaves_ordenadas}")
            valores_ordenados = [estacao[chave] for chave in chaves_ordenadas]
            #print(f"valores_ordenados: {valores_ordenados}")
            # Achatar a lista aninhada
            valores_achatados = achatar_lista(valores_ordenados)
            #print(f"valores_achatados: {valores_achatados}")
            valores_round=[round(value, decimal) for value in valores_achatados]
            #print(f"valores_round: {valores_round}")
 
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