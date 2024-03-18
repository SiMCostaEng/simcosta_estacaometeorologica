# B=LOW & A=LOW: D0=HIGH
# B=LOW & A=HIGH: D1=HIGH
# B=HIGH & A=LOW: D2=HIGH
# B=HIGH & A=HIGH: D3=HIGH
import machine
from machine import Pin, ADC, UART
import time
from time import sleep

CH_A_MUX = Pin(15, mode=Pin.OUT, value=0)
CH_B_MUX  = Pin(4, mode=Pin.OUT, value=0)

MSG = "0"

BAUDRATE_STORX = 9600
BAUDRATE_COMPASS = 9600
BAUDRATE_PROBECO2 = 9600

uart = UART(2, baudrate=9600)
#uart_station= UART(2, baudrate=9600) #como controlar a velocidade da UART de acordo com o device se uart multiplexada

def select_uart(uart_ch):
    global uart_station, BAUDRATE_STORX, BAUDRATE_COMPASS, BAUDRATE_PROBECO2, MSG 

    if uart_ch == 0:
        #uart_station = UART(2, baudrate=9600) #BAUDRATE_STORX)
        CH_A_MUX.value(0)
        CH_B_MUX.value(0)
        MSG = "CHANNEL 0 CONNECTED"
        print(MSG)
        time.sleep(1)
        uart.write("hello")
        time.sleep(1)
        
        
    elif uart_ch == 1:
        #uart_station = UART(2, baudrate=9600) #BAUDRATE_PROBECO2)
        CH_A_MUX.value(1)
        CH_B_MUX.value(0)
        MSG = "CHANNEL 1 CONNECTED"        
        print(MSG)
        time.sleep(1)
        uart.write("hello")
        time.sleep(1)
                
    elif uart_ch == 2:
        #uart_station = UART(2, baudrate=9600) #BAUDRATE_COMPASS)
        CH_A_MUX.value(0)
        CH_B_MUX.value(1)
        MSG = "CHANNEL 2 CONNECTED"
        print(MSG)
        time.sleep(1)
        uart.write("hello")
        time.sleep(1)

    elif uart_ch == 3:
        CH_A_MUX.value(1)
        CH_B_MUX.value(1)
        MSG = "CHANNEL 3 CONNECTED"        
        print(MSG)
        time.sleep(1)
        uart.write("hello")
        time.sleep(1)

     

while True:
    uart_ch =  int(input("Selecione a serial (0: STOR-X | 1: CO2 | 2: COMPASS ) : "))
    select_uart(uart_ch)


