from serial import Serial
from random import randrange
import time

port = Serial('COM3', 9600, timeout=5)
while True:
    #port.write(str(randrange(7)).encode())
    port.write(str(45).encode())
    #print(port.readline(5))
    time.sleep(0.01)
