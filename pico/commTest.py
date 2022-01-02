# Basic Pi -> Pico communication test
# This part to be run on the pico

from machine import Pin
import machine
import time

led=Pin(25, Pin.OUT)
uart = machine.UART(0, 115200)
print(uart)

uart.write("Hello from pico\n")
time.sleep(0.2)

while True:
    if uart.any():
        print("Data received")
        rawIn = uart.readline()
        #print(rawIn)
        # Raw data is as a byte stream. Convert
        # Need to use a try/except as control characters may cause an issue
        try:
            dataIn = rawIn.decode('utf-8').strip()
            # Remove new lines
            #dataIn.strip()
            print("Incoming :", dataIn)
        except:
            pass
    led.toggle()
    print("LED status = ", led.value())
    x = led.value()
    uart.write(f"LED status {x}\n")
    time.sleep(0.5)