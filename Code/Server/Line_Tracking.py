import time
from Motor import *
import RPi.GPIO as GPIO
from Ultrasonic import Ultrasonic
class Line_Tracking:
    def __init__(self):
        self.IR01 = 14
        self.IR02 = 15
        self.IR03 = 23
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IR01,GPIO.IN)
        GPIO.setup(self.IR02,GPIO.IN)
        GPIO.setup(self.IR03,GPIO.IN)
        self.ultrasonic_sensor = Ultrasonic()
    def run(self):
        obstacle = (self.ultrasonic_sensor.get_distance() < 5)
        while not obstacle:
            self.LMR=0x00
            if GPIO.input(self.IR01)==True:
                self.LMR=(self.LMR | 4)
            if GPIO.input(self.IR02)==True:
                self.LMR=(self.LMR | 2)
            if GPIO.input(self.IR03)==True:
                self.LMR=(self.LMR | 1)
            print("LMR value: ", self.LMR)
            if self.LMR==2:
                PWM.setMotorModel(700,700,700,700)
            elif self.LMR==4:
                PWM.setMotorModel(-1000,-1000,2000,2000)
            elif self.LMR==6:
                PWM.setMotorModel(-1500,-1500,3500,3500)
            elif self.LMR==1:
                PWM.setMotorModel(2000,2000,-1000,-1000)
            elif self.LMR==3:
                PWM.setMotorModel(3500,3500,-1500,-1500)
            elif self.LMR==7:
                #pass
                PWM.setMotorModel(-1000,-1000,2000,2000)
            elif self.LMR==0:
                PWM.setMotorModel(-600,-600,-600,-600)
            # recheck for obstacle
            obstacle = (self.ultrasonic_sensor.get_distance() < 5)
            print("Is there an obstacle? ", obstacle)
        # stop once obstacle detected
        PWM.setMotorModel(0,0,0,0)

    def at_line(self):
        if GPIO.input(self.IR01)==True:
            return True
        elif GPIO.input(self.IR02)==True:
            return True
        elif GPIO.input(self.IR03)==True:
            return True
        else:
            return False
            
infrared=Line_Tracking()
# Main program logic follows:
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        infrared.run()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program  will be  executed.
        PWM.setMotorModel(0,0,0,0)
