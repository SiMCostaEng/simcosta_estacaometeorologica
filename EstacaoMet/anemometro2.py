from machine import Pin, ADC, UART
from time import sleep
import ustruct

WD_pin = ADC(Pin(4))
WD_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v

WS_pin = ADC(Pin(0))
WS_pin.atten(ADC.ATTN_11DB)       #Full range: 3.3v


uart = UART(2, 19200)
framesync = "WQMX"


while True:
  WS_value = WS_pin.read()
  WD_value = WD_pin.read()
    
  #print(WS_value, WD_value)
  WD_value = str(WD_value)
  WS_value = str(WS_value)
  
  anemometro = [framesync, WS_value, WD_value]
  anemometro_comma_separated = ",".join(anemometro)
  
  #print(anemometro_comma_separated)
  
  uart.write(anemometro_comma_separated)  # write 5 bytes
  print(uart.read())
  sleep(0.1)          
  
          
