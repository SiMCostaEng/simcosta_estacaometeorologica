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



print("=========================================")
print(equipment_configs)



print("===================AnemometerYoung======================")
print(equipment_configs['AnemometerYoung']['port0'])

# #WIND SPEED RANGE: 0 to 100 M/S
# WS_in_min = config["WS_in_min"]
# WS_in_max = config["WS_in_max"]
# WS_out_min = config["WS_out_min"]
# WS_out_max = config["WS_out_max"]

# #WIND DIRECTION RANGE: 0 to 360
# WD_in_min = config["WD_in_min"]
# WD_in_max = config["WD_in_max"]
# WD_out_min = config["WD_out_min"]
# WD_out_max = config["WD_out_max"]

# #range temperatura: -40°C à +60°C
# T_in_min = config["T_in_min"]
# T_in_max = config["T_in_max"]
# T_out_min = config["T_out_min"]
# T_out_max = config["T_out_max"]

# #range humidade: 0-100%
# H_in_min = config["H_in_min"]
# H_in_max = config["H_in_max"]
# H_out_min = config["H_out_min"]
# H_out_max = config["H_out_max"]

# #range pressao 800 a 1060 hpa
# P_in_min = config["P_in_min"]
# P_in_max = config["P_in_max"]
# P_out_min = config["P_out_min"] 
# P_out_max = config["P_out_max"]

# #PCB LM35 out 0mV + 10mV/°C
# LM_in_min = config["LM_in_min"]
# LM_in_max = config["LM_in_max"]
# LM_out_min = config["LM_out_min"]
# LM_out_max = config["LM_out_max"]

