from machine import UART
import time

uart = UART(2, baudrate=9600)

while True: 
    uart.write("hello")
    time.sleep(0.5)
    print(uart.read(5))