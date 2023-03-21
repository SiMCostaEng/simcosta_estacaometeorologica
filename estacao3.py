from machine import Pin, ADC, UART, SoftI2C
from time import sleep
from ADS1115 import *
import ustruct

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

print('0')

# uart_storex = UART(2, 19200)
# uart_bussola = UART(0, 4800)
# framesync = "WQMX"

ADS1115_ADDRESS = 0x48

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)

P_in_min = 0
P_in_max = 5
P_out_min = 800     #range pressao 800 a 1060 hpa 
P_out_max = 1060

adc.setVoltageRange_mV(ADS1115_RANGE_6144)
adc.setCompareChannels(ADS1115_COMP_0_GND)
adc.setMeasureMode(ADS1115_SINGLE)


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

def readChannel(channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage

while True:
     print("1")
     T_value = T_pin.read()
     H_value = H_pin.read()
     
     T = (T_value - T_in_min) * (T_out_max - T_out_min) / (T_in_max - T_in_min) + T_out_min
     H = (H_value - H_in_min) * (H_out_max - H_out_min) / (H_in_max - H_in_min) + H_out_min
     T = str(T)
     H = str(H)

     WS_value = readChannel(ADS1115_COMP_0_GND)
     WD_value = readChannel(ADS1115_COMP_1_GND)
     P_value = readChannel(ADS1115_COMP_2_GND)
     
     WS = (WS_value - WS_in_min) * (WS_out_max - WS_out_min) / (WS_in_max - WS_in_min) + WS_out_min
     WD = (WD_value - WD_in_min) * (WD_out_max - WD_out_min) / (WD_in_max - WD_in_min) + WD_out_min
     P = (P_value - P_in_min) * (P_out_max - P_out_min) / (P_in_max - P_in_min) + P_out_min
     
     #print("Channel 0: {:<4.2f}".format(P))
     print(WS_value)
     
     bussola = uart_bussola.read()
     if bussola != None:
         bussola=str(bussola)
         bussval = get_first_nbr_from_str(bussola)
         #print(bussval)
     
     estacao = [framesync, WS, WD, T, H, P, bussval]
     #estacao = [framesync, WS_value, WD_value, T, H, GMP343_value]
     estacao_comma_separated = ",".join(estacao)
     print(estacao_comma_separated)
     uart_storex.write(estacao_comma_separated)  # write 5 bytes
     print(uart_storex.read())
     sleep(0.1)          


