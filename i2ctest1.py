from machine import Pin
from machine import SoftI2C
import time
import ustruct

i2c = SoftI2C(scl = Pin(22), sda = Pin(21), freq=10000)

slv = i2c.scan()
for s in slv:
    buf = i2c.readfrom_mem(s, 0, 1)
    if buf[0] == 0xe5:
      slvAddr = s
      print('adxl345 found at I2C address: ', slv)
      break

def writeByte(addr, data):
  d = bytearray([data])
  i2c.writeto_mem(slvAddr, addr, d)

def readByte(addr):
  return i2c.readfrom_mem(slvAddr, addr, 1)


while True: 
   #fmt = '<h' #little-endian
   buf1 = readByte(0x32)
   buf2 = readByte(0x33)
   buf = bytearray([buf1[0]])
   x, = ustruct.unpack('<h', buf)
   x = x*1
   time.sleep(0.5)

   print('x:',x)
   time.sleep(1)

