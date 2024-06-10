from machine import UART
from machine import Pin, ADC
import time
#a = int.to_bytes(10,2,'big')
uart = UART(2, 19200)

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)   
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

CH_A_MUX.value(1)
CH_B_MUX.value(0) 


while(1):
    time.sleep(2)
    uart.write("R\r\n")
    time.sleep(2)
    for i in range(10):
        uart.write("R\r\n")
        time.sleep(1)
        print(uart.read())
        print(i)
        i+=1
    #print(int.from_bytes(uart.read(),'big'))
    uart.write("S\r\n")
    for i in range(100):
        uart.write("S\r\n")
        time.sleep(1)
        print(uart.read())
        print(i)
        i+=1
    
    #time.sleep(0.5)
