from machine import UART
from machine import Pin
import time

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

CH_A_MUX.value(0)
CH_B_MUX.value(0)

uart = UART(2, baudrate=9600)

while True: 
    time.sleep(1)
    print(uart.read())

