from machine import Pin, ADC, UART
from time import sleep
import ustruct

WD_pin = ADC(Pin(4))
WD_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v

WS_pin = ADC(Pin(0))
WS_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v

T_pin = ADC(Pin(36))
T_pin.atten(ADC.ATTN_0DB)  #full range: 1.2v

H_pin = ADC(Pin(39))
H_pin.atten(ADC.ATTN_0DB)

T_in_min = 0
T_in_max = 3413
T_out_min = -40     #range temperatura: -40°C à +60°C
T_out_max = 60

H_in_min = 0
H_in_max = 3413
H_out_min = 0       #range humidade: 0-100%
H_out_max = 100

uart_storex = UART(2, 19200)
framesync = "WQMX"

#uart_gmp343 = UART(0, 19200)

while True:
     T_value = T_pin.read()
     H_value = H_pin.read()
     
     T = (T_value - T_in_min) * (T_out_max - T_out_min) / (T_in_max - T_in_min) + T_out_min
     H = (H_value - H_in_min) * (H_out_max - H_out_min) / (H_in_max - H_in_min) + H_out_min
     T = str(T)
     H = str(H)

     WS_value = WS_pin.read()
     WD_value = WD_pin.read()
    
     WD_value = str(WD_value)
     WS_value = str(WS_value)
     
     #GMP343_value = uart_gmp343.read()
     
     estacao = [framesync, WS_value, WD_value, T, H]
     #estacao = [framesync, WS_value, WD_value, T, H, GMP343_value]
     estacao_comma_separated = ",".join(estacao)
  
     uart_storex.write(estacao_comma_separated)  # write 5 bytes
     print(uart_storex.read())
     sleep(0.1)          
  
          
