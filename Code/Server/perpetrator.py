from Motor import Motor
from servo import Servo
import time

def head_on_attack():
    motor = Motor()
    motor.setMotorModel(700,700,700,700)
    time.sleep(5)
    motor.setMotorModel(-800,-800,-800,-800)
    time.sleep(8)
    motor.setMotorModel(0,0,0,0)

def side_attack():
    motor = Motor()
    servo = Servo()
    # set servo angle so that face at 90 degrees to the right (facing guard dog)
    servo.setServoPwm(0,90)
    time.sleep(2)
    motor.setMotorModel(700,700,700,700)
    time.sleep(10)
    motor.setMotorModel(0,0,0,0)
    servo.setServoPwm(0,0)

if __name__ == '__main__':
    # initial head-on attack
    head_on_attack()

    # pause to allow for vehicle readjustment
    time.sleep(15)

    # initiate side attack (user repositions vehicle to side of track)
    side_attack()
     
