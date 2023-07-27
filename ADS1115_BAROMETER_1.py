#####################################################################################
# Example program for the ADS1115_mPy module
#
# This program shows how to use the ADS1115 in single shot mode. 
#  
# Further information can be found on (currently only for the Arduino version):
# https://wolles-elektronikkiste.de/ads1115 (German)
# https://wolles-elektronikkiste.de/en/ads1115-a-d-converter-with-amplifier (English)
# 
#####################################################################################

from machine import SoftI2C, Pin
from time import sleep
from ADS1115 import *
 
 
ADS1115_ADDRESS = 0x48

i2c = SoftI2C(scl = Pin(22), sda = Pin(21))
adc = ADS1115(ADS1115_ADDRESS, i2c=i2c)

P_in_min = 0
P_in_max = 5
P_out_min = 2     #range pressao 800 a 1060 hpa 
P_out_max = 150

#     Set the voltage range of the ADC to adjust the gain:
#     Please note that you must not apply more than VDD + 0.3V to the input pins!
#     ADS1115_RANGE_6144  ->  +/- 6144 mV
#     ADS1115_RANGE_4096  ->  +/- 4096 mV
#     ADS1115_RANGE_2048  ->  +/- 2048 mV (default)
#     ADS1115_RANGE_1024  ->  +/- 1024 mV
#     ADS1115_RANGE_0512  ->  +/- 512 mV
#     ADS1115_RANGE_0256  ->  +/- 256 mV
adc.setVoltageRange_mV(ADS1115_RANGE_6144)

#     Set the inputs to be compared:
#     ADS1115_COMP_0_1    ->  compares 0 with 1 (default)
#     ADS1115_COMP_0_3    ->  compares 0 with 3
#     ADS1115_COMP_1_3    ->  compares 1 with 3
#     ADS1115_COMP_2_3    ->  compares 2 with 3
#     ADS1115_COMP_0_GND  ->  compares 0 with GND
#     ADS1115_COMP_1_GND  ->  compares 1 with GND
#     ADS1115_COMP_2_GND  ->  compares 2 with GND
#     ADS1115_COMP_3_GND  ->  compares 3 with GND
adc.setCompareChannels(ADS1115_COMP_0_GND)

#     Set number of conversions after which the alert pin will assert
#     - or you can disable the alert:   
#     ADS1115_ASSERT_AFTER_1  -> after 1 conversion
#     ADS1115_ASSERT_AFTER_2  -> after 2 conversions
#     ADS1115_ASSERT_AFTER_4  -> after 4 conversions
#     ADS1115_DISABLE_ALERT   -> disable comparator / alert pin (default) 
# adc.setAlertPinMode(ADS1115_ASSERT_AFTER_1); //uncomment if you want to change the default

#     Set the conversion rate in SPS (samples per second)
#     Options should be self-explaining: 
#     ADS1115_8_SPS 
#     ADS1115_16_SPS  
#     ADS1115_32_SPS 
#     ADS1115_64_SPS  
#     ADS1115_128_SPS (default)
#     ADS1115_250_SPS 
#     ADS1115_475_SPS 
#     ADS1115_860_SPS 
# adc.setConvRate(ADS1115_128_SPS) # uncomment if you want to change the default

#     Set continuous or single shot mode:
#     ADS1115_CONTINUOUS  ->  continuous mode
#     ADS1115_SINGLE     ->  single shot mode (default)
adc.setMeasureMode(ADS1115_SINGLE)

#     Choose maximum limit or maximum and minimum alert limit (window) in volts - alert pin will 
#     assert when measured values are beyond the maximum limit or outside the window 
#     Upper limit first: setAlertLimit_V(MODE, maximum, minimum)
#     In max limit mode the minimum value is the limit where the alert pin assertion will be 
#     be cleared (if not latched).  
#     ADS1115_MAX_LIMIT
#     ADS1115_WINDOW
# adc.setAlertModeAndLimit_V(ADS1115_MAX_LIMIT, 3.0, 1.5)
  
#     Enable or disable latch. If latch is enabled the alert pin will assert until the
#     conversion register is read (getResult functions). If disabled the alert pin assertion
#     will be cleared with next value within limits. 
#     ADS1115_LATCH_DISABLED (default)
#     ADS1115_LATCH_ENABLED
# adc.setAlertLatch(ADS1115_LATCH_ENABLED)

#     Sets the alert pin polarity if active:
#     ADS1115_ACT_LOW  ->  active low (default)   
#     ADS1115_ACT_HIGH ->  active high
# adc.setAlertPol(ADS1115_ACT_LOW)

#     With this function the alert pin will assert, when a conversion is ready.
#     In order to deactivate, use the setAlertLimit_V function  
# adc.setAlertPinToConversionReady()

def readChannel(channel):
    adc.setCompareChannels(channel)
    adc.startSingleMeasurement()
    while adc.isBusy():
        pass
    voltage = adc.getResult_V()
    return voltage

print("ADS1115 Example Sketch - Single Shot Mode")
print("Channel / Voltage [V]: ")
print(" ")

while True:
      P_value = readChannel(ADS1115_COMP_0_GND)
      P = (P_value - P_in_min) * (P_out_max - P_out_min) / (P_in_max - P_in_min) + P_out_min
      print("Channel 0: {:<4.2f}".format(P))
#     print("---------------")
#     
#     voltage = readChannel(ADS1115_COMP_1_GND)
#     print("Channel 1: {:<4.2f}".format(voltage))
#    voltage = readChannel(ADS1115_COMP_0_GND)
#    print("Channel 2: {:<4.2f}".format(voltage))
#     voltage = readChannel(ADS1115_COMP_3_GND)
#     print("Channel 3: {:<4.2f}".format(voltage))
#     print("---------------")
      sleep(.1)
