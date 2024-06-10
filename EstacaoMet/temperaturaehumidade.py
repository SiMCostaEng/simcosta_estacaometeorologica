from machine import Pin, ADC, UART
from time import sleep

T_pin = ADC(Pin(4))
T_pin.atten(ADC.ATTN_0DB)  #full range: 1.2v

H_pin = ADC(Pin(2))
H_pin.atten(ADC.ATTN_0DB)

T_in_min = 0
T_in_max = 3413
T_out_min = -40     #range temperatura: -40°C à +60°C
T_out_max = 60

H_in_min = 0
H_in_max = 3413
H_out_min = 0       #range humidade: 0-100%
H_out_max = 100

while True:
     T_value = T_pin.read()
     H_value = H_pin.read()
     
     print(f'T_value: {T_value} H_value: {H_value}')
     
     T = (T_value - T_in_min) * (T_out_max - T_out_min) / (T_in_max - T_in_min) + T_out_min
     H = (H_value - H_in_min) * (H_out_max - H_out_min) / (H_in_max - H_in_min) + H_out_min

     print(f'Temperature: {T} Humidity: {H}')
     
     sleep(.2)
