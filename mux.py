# B=LOW & A=LOW: D0=HIGH
# B=LOW & A=HIGH: D1=HIGH
# B=HIGH & A=LOW: D2=HIGH
# B=HIGH & A=HIGH: D3=HIGH

import machine
from machine import Pin, ADC
from time import sleep

ATXMUX = Pin(32, mode=Pin.OUT, value=0)
BTXMUX = Pin(33, mode=Pin.OUT, value=0)
# ARXMUX = pin(25, mode=Pin.OUT, value=0)
# BRXMUX = pin(26, mode=Pin.OUT, value=0)

Y= ADC(Pin(34))
Y.atten(ADC.ATTN_11DB)   
saida = 0

def select(saida):
    if saida == 0:
        ATXMUX=0
        BTXMUX=0
    elif saida == 1:
        ATXMUX=1
        BTXMUX=0
    elif saida == 2:
        ATXMUX=0
        BTXMUX=1
    elif saida == 3:
        ATXMUX=1
        BTXMUX=1
        
while True:
    saida=0
    saida = int(input("determine a saida: "))
    select(saida)
    sleep(1)
    print("y: {}".format(Y.read()))
    sleep(5)
