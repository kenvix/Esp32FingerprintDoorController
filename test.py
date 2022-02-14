from machine import Pin, Timer, PWM
import gpios
from config import gpioconfig
import time

print("fuck buggy micropython PWM!!!")

# while True:
#     pwm = PWM(Pin(gpioconfig.DOOR_MOTOR_PIN), freq=50, duty=26)
#     time.sleep(1.5)
#     pwm.deinit()
#     pwm = PWM(Pin(gpioconfig.DOOR_MOTOR_PIN), freq=50, duty=128)
#     time.sleep(1.5)
#     pwm.deinit()

pwm = PWM(Pin(gpioconfig.DOOR_MOTOR_PIN), freq=50, duty=128)
while True:
    pwm.duty(26)
    pwm.freq(50)
    time.sleep(1.8)
    pwm.duty(128)
    pwm.freq(50)
    time.sleep(1.8)