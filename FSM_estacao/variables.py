#this file contains all variables used in the FSM code
import json
import uos as os

config_file = "config.json" 

# Check if file exists using os.stat
try:
    os.stat(config_file)
except OSError:
    print("Error: config.json file not found.")
    raise

# Load the config file from flash
with open(config_file) as f:
    config_content = f.read()
    print("Config file content:", config_content)  # Print the content to check for issues

try:
    config = json.loads(config_content)
    print("Config loaded successfully:", config)
except ValueError as e:
    print("Error: JSON decode error:", e)
    raise

# Assign variables from config

framesync = config["framesync"]

# PIN ADDR = GND
ADS1115_1_ADDRESS = config.get("ADS1115_1_ADDRESS", 0x48)
# PIR ADDR = VCC
ADS1115_2_ADDRESS = config.get("ADS1115_2_ADDRESS", 0x49)

BAUDRATE = config.get("BAUDRATE",19200)
input_var = config["input_var"]
interruptCounter=config["interruptCounter"]

n_data = config["n_data"]    # quantidade de medidas a ser adquirida
n_var_co2=config["n_var_co2"]    #quantiidade de variáveis medidas no sensor de co2
n_sec = config["n_sec"]     #quantidade de segundos a serem esperados na função init

#Parâmetros dos sensores
# Parâmetros dos sensores (aninhados em "equipments")
equipments = config["equipments"]

# Dicionário para armazenar configurações específicas de cada equipamento
equipment_configs = {}

for equipment in equipments:
    equipment_config = {
        "className": equipment["className"], 
        "equipmentName": equipment["equipmentName"],
        "num_variables": equipment["num_variables"],
        "channel_index0": equipment.get("channel_index0"),
        "adc0": equipment.get("adc0"),
        "port0": equipment.get("port0"),
        "channel_index1": equipment.get("channel_index1"),
        "adc1": equipment.get("adc1"),
        "port1": equipment.get("port1"),
        "BAUDRATE": equipment.get("BAUDRATE", 19200),
        "uart_ch": equipment.get("uart_ch"),
        "P0_in_min": equipment.get("P0_in_min"),
        "P0_in_max": equipment.get("P0_in_max"),
        "P0_out_min": equipment.get("P0_out_min"),
        "P0_out_max": equipment.get("P0_out_max"),
        "P1_in_min": equipment.get("P1_in_min"),
        "P1_in_max": equipment.get("P1_in_max"),
        "P1_out_min": equipment.get("P1_out_min"),
        "P1_out_max": equipment.get("P1_out_max"),
        }

    equipment_configs[equipment["equipmentName"]] = equipment_config


datalogger=config["datalogger"]
# Dicionário para armazenar configurações específicas do datalogger 

print(datalogger)
print(type(datalogger))

datalogger=dict(enumerate(datalogger))
print(datalogger)
# data_dict={}

# for data_info in datalogger:
#     data_dict={
#             "className": equipment["className"],
#             "equipmentName":equipment["equipmentName"],
#             "num_variables":equipment["num_variables"],
#             "uart_ch":equipment["uart_ch"],
#             "BAUDRATE":equipment["BAUDRATE"]
#             }
  
print(datalogger)
print(type(datalogger))
# print(data_dict)
# print(type(data_dict))
#print("====================todas as configs=====================")
#print(equipment_configs)

#print("===================AnemometerYoung======================")
#print(equipment_configs['AnemometerYoung'])

