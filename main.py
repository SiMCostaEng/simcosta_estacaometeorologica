import machine
from machine import UART
from machine import Pin, ADC
import time
#a = int.to_bytes(10,2,'big')
uart = UART(0, 115200)
led = machine.Pin(2, machine.Pin.OUT)

while(1):
    led.value(1)
    time.sleep(.5)
    uart.write('oi')  # write 5 bytes
    print(uart.read())
    led.value(0)
    time.sleep(0.5)

    #print(int.from_bytes(uart.read(),'big'))
    
    #time.sleep(0.5)
