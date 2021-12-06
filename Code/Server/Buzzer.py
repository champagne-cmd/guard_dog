import time
import RPi.GPIO as GPIO
from Command import COMMAND as cmd
import logging

# setup logging 
logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-2s) %(message)s',
)


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

    def bark(self, cond):
        logging.debug("bark is waiting")
        with cond:
            cond.wait()


        logging.debug("should bark now")
        for i in range(5):
            self.run('1')
            time.sleep(.5)
            self.run('0')
            time.sleep(.5)
            




