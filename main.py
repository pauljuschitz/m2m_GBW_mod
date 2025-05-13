# sanity check to see if we can make the onboard LED flash
from machine import Pin # type: ignore
import time

led = Pin(10, Pin.OUT)

while True:
    led.value(not led.value())
    time.sleep(0.5)