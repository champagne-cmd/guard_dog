import time
import RPi.GPIO as GPIO
from Command import COMMAND as cmd
GPIO.setwarnings(False)
Buzzer_Pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(Buzzer_Pin,GPIO.OUT)
class Buzzer:
    def run(self,command):
        if command!="0":
            GPIO.output(Buzzer_Pin,True)
        else:
            GPIO.output(Buzzer_Pin,False)

    def bark(self):
        for i in range(5):
            self.run('1')
            time.sleep(.5)
            self.run('0')
            time.sleep(.5)
            




