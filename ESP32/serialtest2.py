from machine import UART
from machine import Pin, ADC
import time
#a = int.to_bytes(10,2,'big')
uart = UART(2, 19200)

a=1.234
b=str(a)

SN = 1
date = 190123
time = 125955
Pumped = 0
Cond = 0.1000 #// (S/m)
Temp = 20.0 #//(C),
Pres = 0.03 #//(dbar),
Sal = 0.012 #//(PSU),
RawDO = 10000.1#; //(Hz),
OxSat = 5.892#; //(ml/l),
DO = 6.220#; //(ml/l),
PercentOxSat = 1.0555 #; //(%),
TURBIDITYC = 83.00#; //(COUNTS),
TURBIDITYntu = 0.201#;//(NTU),
CHLAcounts = 47.000#; //(COUNTS),
CHLA = -0.024#; //(UG/L),
CDOMcounts = 56.000#; //(COUNTS),
CDOMppb = 0.541#; //(PPB-QSDE)

# c_SN = str(SN)
# c_date = str(date)
# c_time = str(time)
# c_Pumped = str(Pumped)
# c_Cond = str(Cond) 
# c_Temp = str(Temp)
# c_Pres = str(Pres)
# c_Sal = str(Sal)
# c_RawDO = str(RawDO)
# c_OxSat = str(OxSat)
# c_DO = str(DO)
# c_PercentOxSat = str(PercentOxSat)
# c_TURBIDITYC = str(TURBIDITYC)
# c_TURBIDITYntu = str(TURBIDITYntu)
# c_CHLAcounts = str(CHLAcounts)
# c_CHLA = str(CHLA)
# c_CDOMcounts = str(CDOMcounts)
# c_CDOMppb = str(CDOMppb)

c = bytearray(19)
c[0] ='WQMX'
c[1] = str(SN)
c[2] = str(date)
c[3] = str(time)
c[4] = str(Pumped)
c[5] = str(Cond) 
c[6] = str(Temp)
c[7] = str(Pres)
c[8] = str(Sal)
c[9] = str(RawDO)
c[10] = str(OxSat)
c[11] = str(DO)
c[12] = str(PercentOxSat)
c[13] = str(TURBIDITYC)
c[14] = str(TURBIDITYntu)
c[15] = str(CHLAcounts)
c[16] = str(CHLA)
c[17] = str(CDOMcounts)
c[18] = str(CDOMppb)
#uart.write('ANEMOM,')  # write 5 bytes

#uart1.write('\r\n')  # write 5 bytes
#uart1.read(5)         # read up to 5 bytes

print(c)
# 
# while(1):
#     uart.write(b)  # write 5 bytes
#     #time.sleep(0.5)
#     print(uart.read(5))
#     #print(int.from_bytes(uart.read(),'big'))
#     
#     #time.sleep(0.5)