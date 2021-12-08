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
import io
import numpy as np
import logging
import sys
sys.path.insert(0, './windows')
import cv2

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

        self.motor.setMotorModel(-750,-750,-750,-750) # move forward

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

        #todo add line tracking stuff here  

    # upon notification from 'wake_up', continuously beeps until 'patrol_over' condition is fired    
    def bark(self):
        with self.wake_up:
            self.wake_up.wait()

        for i in range(5): #todo change this condition to check for patrol_over
            self.buzzer.run('1')
            time.sleep(.5)
            self.buzzer.run('0')
            time.sleep(.5)

    # upon notification from 'wake_up', flashes led's until 'patrol_over' condition is fired 
    def patrol_lights(self):
        with self.wake_up:
            self.wake_up.wait()
        # logging.debug("lights start now")
    
        for i in range(15): #todo should continue until it recieves patrol over notifcation
            self.led.colorWipe(self.led.strip, Color(255, 0, 0))  # Red wipe
            self.led.colorWipe(self.led.strip, Color(0, 0, 255))  # Blue wipe

        self.led.colorWipe(self.led.strip, Color(0,0,0),10)
        # logging.debug("lights off now")

    # uses the ultrasonic to check for anything within X cm away from the sensor, notifies wake up condition
    def check_for_motion(self, dist_in_cm):
        logging.debug("in check for motion")
        detected = False
        while(not detected):
            if(self.ultrasonic.get_distance() <= dist_in_cm):
                detected = True
                logging.debug("Object recognized within $d")
                with self.wake_up:
                    self.ake_up.notifyAll()
    
    # initiates the ultrasonic, buzzer, led, and attack threads
    def initiate_protocol(self,server):
        self.motor.setMotorModel(0,0,0,0) # make sure the car isnt moving start
        wake_up = Condition()

        ultrasonic_thread = Thread(name="Ultrasonic Thread", target=self.check_for_motion)
        buzzer_thread = Thread(name="Buzzer Thread", target=self.bark)
        led_thread = Thread(name="Led Thread", target=self.patrol_lights)
        attack_thread = Thread(name="Attack Thread", target=self.attack, args=[server], daemon=True)

        time.sleep(3) #todo buffer period to get everything in order for testing 
        ultrasonic_thread.start()
        buzzer_thread.start()
        led_thread.start()
        attack_thread.start()

        # ultrasonic_thread.join()
        # led_thread.join()
        # buzzer_thread.join()
        # logging.debug("buzzer joined")

        # todo this will be removed
        time.sleep(5)
        self.motor.setMotorModel(0,0,0,0)
        sys.exit()



def return_home():
    tracker = Line_Tracking()
    tracker.run() # need to modify to stop once ultrasonic sensors detect box in path

def terminate_guard_dog_protocol(on_patrol, server_thread, server):
    with on_patrol:
        on_patrol.wait()

        # stop all other threads and server once no longer on patrol
        stop_thread(server_thread) 
        # ^ this may not work - may need to initialize global bool to pass to all 
        # threads and have each check bool with each loop execution
        server.server_socket.shutdown(2)
        server.server_socket1.shutdown(2)
        server.StopTcpServer()

        # make dog return to house
        return_home()

def monitor_battery(on_patrol):
    adc = Adc()
    patrolling = True
    while patrolling:
        # read the battery voltage
        power = adc.recvADC(2)*3.0
        # if voltage below 7 V, initiate return to home by signalling on cond. var.
        if power < 7.0:
            logging.debug("Battery running low, returning to dog house")
            patrolling = False
            with on_patrol:
                on_patrol.notifyAll()

def init_guard_dog(server, patrol_over):
    video_thread = Thread(target=server.sendvideo, daemon=True) # daemon=True to make thread terminate as soon as guard dog protocol below terminates
    video_thread.start()

    # initialize guard dog object
    dog = GuardDog(patrol_over)
    dog.initiate_protocol(server)

    time.sleep(20) #todo might need to get rid of this


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
    # launch thread to shut down other threads if return to dog house initiated
    return_thread = Thread(name="Return Thread", target=terminate_guard_dog_protocol, args=[patrol_over, server_thread, server])

    # battery_thread.start()
    server_thread.start()
    # return_thread.start()


    # server_thread.join()
    # logging.debug("server thread joined")
    

