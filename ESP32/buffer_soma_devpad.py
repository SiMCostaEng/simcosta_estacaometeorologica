from machine import Pin, ADC, UART, SoftI2C
from time import sleep
from ADS1115 import *
import ustruct
from ulab import numpy as np
import random

WD_pin = ADC(Pin(4))
WD_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v
 
WS_pin = ADC(Pin(0))
WS_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v

T_pin = ADC(Pin(36))
T_pin.atten(ADC.ATTN_0DB)  #full range: 1.2v
 
H_pin = ADC(Pin(39))
H_pin.atten(ADC.ATTN_0DB)
 
WS_in_min = 0
WS_in_max = 5
WS_out_min = 0     #WIND SPEED RANGE: 0 to 100 M/S
WS_out_max = 100
 
WD_in_min = 0.01
WD_in_max = 4.94
WD_out_min = 0     #WIND DIRECTION RANGE: 0 to 360
WD_out_max = 360

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

WS_data = []
WD_data = []
T_data = []
H_data = []
P_data = []
 
# uart_storex = UART(2, 19200)
# uart_bussola = UART(0, 4800)
# framesync = "WQMX"
 
ADS1115_1_ADDRESS = 0x48
#ADS1115_2_ADDRESS = 0X49

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))

adc_1 = ADS1115(ADS1115_1_ADDRESS, i2c=i2c)
#adc_2 = ADS1115(ADS1115_2_ADDRESS, i2c=i2c)

adc_1.setVoltageRange_mV(ADS1115_RANGE_6144)
adc_1.setCompareChannels(ADS1115_COMP_0_GND)
adc_1.setMeasureMode(ADS1115_SINGLE)
#adc_2.setVoltageRange_mV(ADS1115_RANGE_6144)
#adc_2.setCompareChannels(ADS1115_COMP_0_GND)
#adc_2.setMeasureMode(ADS1115_SINGLE) 

def readChannel_1(channel):
    adc_1.setCompareChannels(channel)
    adc_1.startSingleMeasurement()
    while adc_1.isBusy():
        pass
    voltage = adc_1.getResult_V()
    return voltage

# def readChannel_2(channel):
#     adc_2.setCompareChannels(channel)
#     adc_2.startSingleMeasurement()
#     while adc_2.isBusy():
#         pass
#     voltage = adc_2.getResult_V()
#     return voltage

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

def anemometerRead(WS_value, WD_value):
    WS = (WS_value - WS_in_min) * (WS_out_max - WS_out_min) / (WS_in_max - WS_in_min) + WS_out_min
    WS_data.append(WS)
    #WS_size=len(WS_data)
    WS_mean = np.mean(WS_data)
    WS_stdev = np.std(WS_data)
    
    WD = (WD_value - WD_in_min) * (WD_out_max - WD_out_min) / (WD_in_max - WD_in_min) + WD_out_min
    WD_data.append(WD)
    WD_mean = np.mean(WD_data)
    WD_stdev = np.std(WD_data)
    
    anemometerData = [WS_mean, WS_stdev, WD_mean, WD_stdev]
#     print(WS_value)
#     print(WS_data)
#     #print(WS_size)
#     print(WS_mean)
#     print(WS_stdev)
#     
    return anemometerData


# def getBussolaInfo (bussola)
#     if bussola != None:
#          bussola=str(bussola)
#          bussval = get_first_nbr_from_str(bussola)
# #          print(bussval)
#     return bussval
    
while True:
#     T_value = readChannel_1(ADS1115_COMP_0_GND)
#     H_value = readChannel_1(ADS1115_COMP_1_GND)
    WS_value = readChannel_1(ADS1115_COMP_2_GND)  #random.uniform(0.0, 10.0)
    WD_value = readChannel_1(ADS1115_COMP_3_GND)
    
    print(anemometerRead(WS_value, WD_value))
#     LM_value =  readChannel_2(ADS1115_COMP_0_GND)
#     P_value = readChannel_2(ADS1115_COMP_3_GND)
    
#     bussola_data = getBussolaInfo(uart_bussola.read()) 
#     a = anemometerRead(WS_value, WD_value)
#     estacao = [framesync, a]
#      #estacao = [framesync, WS_value, WD_value, T, H, GMP343_value]
#     estacao_comma_separated = ",".join(estacao)
#     print(estacao_comma_separated)
#     uart_storex.write(estacao_comma_separated)  # write 5 bytes
#     print(uart_storex.read())
#     sleep(1)          



