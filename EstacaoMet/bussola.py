from machine import UART
from machine import Pin, ADC
import time
import struct
import re
#a = int.to_bytes(10,2,'big')
uart = UART(2, 4800)


def get_first_nbr_from_str(input_str):
    if not input_str and not isinstance(input_str, str):
        return 0
    out_number = ''
    for ele in input_str:
        if (ele == '.' and '.' not in out_number) or ele.isdigit():
            out_number += ele
        elif out_number:
            break
    return float(out_number)


while True:
    bussola = uart.read()
    if bussola != None:
        bussola=str(bussola)
        bussval = get_first_nbr_from_str(bussola)
        print(bussval)

