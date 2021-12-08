'''
Main file for guard dog
Launches server, termination, and battery threads to initiate guard dog service
'''

from threading import Thread, Condition
#from Code.Client.Thread import stop_thread
from Thread import *
from ADC import *
from Line_Tracking import Line_Tracking
from server import Server
from Ultrasonic import * 
from Buzzer import *
from Led import *
#import io
#import numpy as np
import logging
import sys
sys.path.insert(0, './windows')
#import cv2

# setup logging 
logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-2s) %(message)s',
)

class GuardDog:
    def __init__(self, cond):
        self.ultrasonic = Ultrasonic()
        self.line_tracking = Line_Tracking()
        self.buzzer = Buzzer()
        self.motor = Motor()
        self.led = Led()
        self.wake_up = Condition()
        self.patrol_over = cond


    # connects to client, recieves motor commands based on facial recognition analysis on client
    # turns the car towards the intruder until ...
    def attack(self,server):
        with self.wake_up:
            self.wake_up.wait()

        self.motor.setMotorModel(750,750,750,750) # move forward

        try:
            try:
                server.connection1,server.client_address1 = server.server_socket1.accept()
                print ("Client connection successful !")
            except:
                print ("Client connect failed")
            restCmd=""
            server.server_socket1.close()
            while True:
                try:
                    AllData=restCmd+server.connection1.recv(1024).decode('utf-8')
                except:
                    if server.tcp_Flag:
                        server.Reset()
                    break
                print(AllData)
                if len(AllData) < 5:
                    restCmd=AllData
                    if restCmd=='' and server.tcp_Flag:
                        server.Reset()
                        break
                restCmd=""
                if AllData=='':
                    break
                else:
                    cmdArray=AllData.split("\n")
                    if(cmdArray[-1] != ""):
                        restCmd=cmdArray[-1]
                        cmdArray=cmdArray[:-1]     
            
                for oneCmd in cmdArray:
                    data=oneCmd.split("#")
                    if data==None:
                        continue
                    elif (cmd.CMD_MOTOR in data):
                        try:
                            logging.debug("%s", data[1])
                            data1=int(data[1])
                            data2=int(data[2])
                            data3=int(data[3])
                            data4=int(data[4])
                            if data1==None or data2==None or data2==None or data3==None:
                                continue
                            self.motor.setMotorModel(data1,data2,data3,data4)
                        except:
                            pass

        except Exception as e: 
            logging.debug("exception")
            print(e)
        server.StopTcpServer()  


    # upon notification from 'wake_up', continuously beeps until 'patrol_over' condition is fired    
    def bark(self):
        with self.wake_up:
            self.wake_up.wait()

        while(True):
            self.buzzer.run('1')
            time.sleep(.5)
            self.buzzer.run('0')
            time.sleep(.5)

    # upon notification from 'wake_up', flashes led's until 'patrol_over' condition is fired 
    def patrol_lights(self):
        with self.wake_up:
            self.wake_up.wait()
        # logging.debug("lights start now")
    
        while(True):
            self.led.colorWipe(self.led.strip, Color(255, 0, 0))  # Red wipe
            self.led.colorWipe(self.led.strip, Color(0, 0, 255))  # Blue wipe

        # self.led.colorWipe(self.led.strip, Color(0,0,0),10)
        # logging.debug("lights off now")

    # uses the ultrasonic to check for anything within X cm away from the sensor, notifies wake up condition
    def check_for_motion(self, dist_in_cm):
        logging.debug("waiting for motion...")
        detected = False
        while(not detected):
            if(self.ultrasonic.get_distance() <= dist_in_cm):
                detected = True
                logging.debug("Object recognized within %d cm", dist_in_cm)
                with self.wake_up:
                    self.wake_up.notifyAll()

    def line_stop(self):
        with self.wake_up:
            self.wake_up.wait()

        # check if perimeter line reached while on patrol
        while not self.line_tracking.at_line():
            continue
        self.motor.setMotorModel(0,0,0,0) # when line reached, stop and signal patrol over

        with self.patrol_over:
            self.patrol_over.notifyAll()

    
    # initiates the ultrasonic, buzzer, led, and attack threads
    def initiate_protocol(self,server):
        self.motor.setMotorModel(0,0,0,0) # make sure the car isnt moving start
        wake_up = Condition()

        ultrasonic_thread = Thread(name="Ultrasonic Thread", target=self.check_for_motion, args=[5])
        buzzer_thread = Thread(name="Buzzer Thread", target=self.bark, daemon=True)
        led_thread = Thread(name="Led Thread", target=self.patrol_lights, daemon=True)
        attack_thread = Thread(name="Attack Thread", target=self.attack, args=[server], daemon=True)
        line_stop_thread = Thread(name="Line Stop Thread", target=self.line_stop)

        time.sleep(3) #todo buffer period to get everything in order for testing 
        ultrasonic_thread.start()
        buzzer_thread.start()
        led_thread.start()
        attack_thread.start()
        line_stop_thread.start()

        # patrol_over = false
        # while(not patrol_over):
        with self.patrol_over:
            self.patrol_over.wait()

        stop_thread(buzzer_thread)
        stop_thread(led_thread)
        stop_thread(attack_thread)
        
        self.buzzer.run('0')
        self.motor.setMotorModel(0,0,0,0)
        self.led.colorWipe(self.led.strip, Color(0,0,0),10)
        
            
        # todo this will be removed
        # time.sleep(5)
        # self.motor.setMotorModel(0,0,0,0)
        # sys.exit()




def return_home():
    motor = Motor()
    tracker = Line_Tracking()
    # check to see if already at perimeter
    if tracker.at_line():
        # pause 5 seconds to record where perpetrator flees
        time.sleep(5)
        tracker.run()
    else:
        # go forward until line reached
        motor.setMotorModel(750,750,750,750)
        while not tracker.at_line():
            continue
        motor.setMotorModel(0,0,0,0) # stop
        tracker.run()


def terminate_guard_dog_protocol(patrol_over):
    with patrol_over:
        patrol_over.wait()
    # when patrol finished, go to perimeter line and follow it back to the dog house
    return_home()

def monitor_battery(patrol_over):
    adc = Adc()
    patrolling = True
    while patrolling:
        # read the battery voltage
        power = adc.recvADC(2)*3.0
        # if voltage below 7 V, initiate return to home by signalling on cond. var.
        if power < 7.0:
            logging.debug("Battery running low, returning to dog house")
            patrolling = False
            with patrol_over:
                patrol_over.notifyAll()

def init_guard_dog(server, patrol_over):
    # initialize guard dog object
    dog = GuardDog(patrol_over)
    dog.initiate_protocol(server)

    #time.sleep(20) #todo might need to get rid of this

def video_stream(patrol_over, server):
    video_thread = Thread(target=server.sendvideo, daemon=True) # daemon=True to make thread terminate as soon as guard dog protocol below terminates
    with patrol_over:
        patrol_over.wait()
    # pause 5 seconds to continue recording perpetrator fleeing
    time.sleep(5)
    stop_thread(video_thread)


if __name__ == '__main__':

    # initialize condition variable to indicate whether dog is on patrol or not 
    # to synchronize battery and termination threads
    patrol_over = Condition()

    # initialize and launch server
    server = Server()
    server.StartTcpServer()

    # launch battery thread to continuously monitor battery and take action if battery level drops 
    # below acceptable voltage
    battery_thread = Thread(name="Battery Thread", target=monitor_battery, args=[patrol_over])
    # launch server thread to receive video stream from guard dog
    server_thread = Thread(name="Server Thread", target=init_guard_dog, args=[server, patrol_over])
    # launch thread to return to dog house
    return_thread = Thread(name="Return Thread", target=terminate_guard_dog_protocol, args=[patrol_over])
    video_thread = Thread(name="Video Stream Thread", target=video_stream, args=[patrol_over, server])

    # battery_thread.start()
    server_thread.start()
    return_thread.start()
    #video_thread.start()


    # server_thread.join()
    # logging.debug("server thread joined")
    
