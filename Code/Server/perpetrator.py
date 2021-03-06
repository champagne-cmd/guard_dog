from Motor import Motor
from servo import Servo
import time

def head_on_attack():
    motor = Motor()
    motor.setMotorModel(700,700,700,700)
    time.sleep(2.5)
    motor.setMotorModel(-800,-800,-800,-800)
    time.sleep(3.5)
    motor.setMotorModel(0,0,0,0)

def side_attack():
    motor = Motor()
    servo = Servo()
    # set servo angle so that face at 90 degrees to the right (facing guard dog)
    servo.setServoPwm('0',180)
    time.sleep(2)
    motor.setMotorModel(600,600,600,600)
    time.sleep(7)
    motor.setMotorModel(0,0,0,0)
    servo.setServoPwm('0',90)

if __name__ == '__main__':
    import sys
    if len(sys.argv)<2:
        print ("Parameter error: Please enter the attack sequence")
        exit() 
    if sys.argv[1] == 'head-on':
        print("Initiating head-on attack...")
        head_on_attack()
    elif sys.argv[1] == 'side':
        print("Initiating side attack...")
        side_attack()
    else:
        print("Not valid attack sequence, terminating...")
     
