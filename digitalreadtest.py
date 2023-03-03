from machine import Pin
from time import sleep

button = Pin(4, Pin.IN)

while True:
  print(button.value())
  sleep(0.1)