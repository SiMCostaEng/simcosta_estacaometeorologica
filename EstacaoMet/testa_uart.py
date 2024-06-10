from machine import UART
from machine import Pin, ADC
import time
#a = int.to_bytes(10,2,'big')
uart = UART(2, 19200)

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

CH_A_MUX.value(0)
CH_B_MUX.value(0) 


while(1):
    uart.write("oiiii")
    time.sleep(1)
    print(uart.readline())
    time.sleep(1)
    #print(int.from_bytes(uart.read(),'big'))
    
    #time.sleep(0.5)
