import machine, os, sdcard
from machine import I2C, Pin
from ds1307 import DS1307               #sensor library
import utime

################### RTC ######################

# declare pins for I2C communication
sclPin = Pin(22) # serial clock pin
sdaPin = Pin(21) # serial data pin

# Initiate I2C 
i2c_object = I2C(0,              # positional argument - I2C id
                  scl = sclPin,  # named argument - serial clock pin
                  sda = sdaPin,  # named argument - serial data pin
                  freq = 400000 )# named argument - i2c frequency

result = I2C.scan(i2c_object) # scan i2c bus for available devices

print("I2C scan result : ", result)
if result != []:
    print("I2C connection successfull")
else:
    print("retry")


# clock object at the dedicated i2c port
clockObject = DS1307(i2c_object)

#  enable the RTC module
clockObject.halt(False) # 32 khz crystal enable

################### sd card ######################


myfile = 'robson'

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(5, machine.Pin.OUT)
# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(23),
                  miso=machine.Pin(19))
# Initialize SD card
sd = sdcard.SDCard(spi, cs)

# OR this simpler initialization code should works on Maker Pi Pico too...
#sd = sdcard.SDCard(machine.SPI(1), machine.Pin(15))
vfs = os.VfsFat(sd)
os.mount(sd, '/sd')
# check the content
os.listdir('/sd')

def grava(filename, message):
    with open('/sd/' + str(filename) + '.txt', 'a') as file:
        print('Writing to data.txt...')
        file.write(message)
        file.close()

def config_clock():
    choice = input("Would you like to change the default date time data ( y / n ) : ")
    if choice == "y":
        print("set the default date time data")
        year = int(input("Year : "))
        month = int(input("month (Jan --> 1 , Dec --> 12): "))
        date = int(input("date : "))
        day = int(input("day (1 --> monday , 2 --> Tuesday ... 0 --> Sunday): ")) # 1 --> monday , 2 --> Tuesday ... 0 --> Sunday
        hour = int(input("hour (24 Hour format): "))
        minute = int(input("minute : "))
        second = int(input("second : "))

        now = (year,month,date,day,hour,minute,second,0)
        clockObject.datetime(now)

    else:
        print("Default data is not changed ")
        print("Default date time settings : ")
        default = clockObject.datetime()
        print("Year : ",default[0])
        print("month : ",default[1])
        print("date : ",default[2])
        print("day : ",default[3])
        print("hour : ",default[4])
        print("minute : ",default[5])
        print("second : ",default[6],"\n")
        utime.sleep(5) # time for user to read serial data properly
    

def dia():
    (year,month,date,day,hour,minute,second,p1)=clockObject.datetime()
    return (str(year) + "-" + str(month) + "-" + str(date))

def data():
    (year,month,date,day,hour,minute,second,p1)=clockObject.datetime()
    return ("[" + str(year) + "/" + str(month) + "/" + str(date) + "-" + str(hour) + ":" + str(minute) + ":" + str(second) + "] ")  
    

#config_yclock()

while 1:
    grava(dia(), data())
    grava(dia(), '\n')
    sleep(.1)
# try some standard file operations
# file = open('/sd/test.txt', 'w')
# file.write('Testing SD card on Maker Pi Pico')
# file.close()
    file = open('/sd/'+ dia() +'.txt', 'r')
    data = file.read()
    print(data)
    file.close()
