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
import picamera
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
    def __init__(self):
        self.ultrasonic = Ultrasonic()
        self.line_tracking = Line_Tracking()
        self.buzzer = Buzzer()
        self.motor = Motor()
        self.led = Led()
        

    def initiate_protocol(self,server):
        self.motor.setMotorModel(0,0,0,0) # make sure the car isnt moving start
        wake_up = Condition()

        ultrasonic_thread = Thread(name="Ultrasonic Thread", target=self.ultrasonic.check_for_motion, args=[wake_up])
        buzzer_thread = Thread(name="Buzzer Thread", target=self.buzzer.bark, args=[wake_up])
        led_thread = Thread(name="Led Thread", target=self.led.patrolLights, args=[wake_up])
        attack_thread = Thread(name="Attack Thread", target=self.attack, args=[wake_up, server], daemon=True)

        time.sleep(1) #todo buffer period to get everything in order for testing 
        ultrasonic_thread.start()
        # buzzer_thread.start()
        led_thread.start()
        attack_thread.start()

        ultrasonic_thread.join()
        logging.debug("ultrasonic thread joined")
        led_thread.join()
        logging.debug("led thread joined")
        # buzzer_thread.join()
        # logging.debug("buzzer joined")

        # todo this will be removed
        time.sleep(5)
        self.motor.setMotorModel(0,0,0,0)
        sys.exit()
        

    def attack(self, wake_up, server):
        with wake_up:
            wake_up.wait()

        self.motor.setMotorModel(-2000,-2000,-2000,-2000) # move forward

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



        # use face detection to steer car
        # stream = io.BytesIO()
        # with picamera.PiCamera() as camera:
        #     camera.resolution = (400,300)      # pi camera resolution
        #     camera.framerate = 15
            # read stream from camera as image
            # for foo in camera.capture_continuous(stream, 'jpeg', use_video_port = True):
                # stream.seek(0)
                # b = stream.read()
                # length=len(b)
                # if length >5120000:
                #     continue
                # image = cv2.imdecode(np.frombuffer(b, dtype=np.uint8), cv2.IMREAD_COLOR)
                # # find face coordinates in image
                # (x, y) = self.face_detect(image)
                # logging("x: %s", x)

                # use face coordinates to steer car if face detected 
                # (boundary values used in servo controlling code - Main.py, ln 603-620)
                # if int(x) == 0:
                #     logging.debug("forward")
                #     # no face detected, move forward
                #     self.motor.setMotorModel(2000,2000,2000,2000)
                # elif float(x) < 192.5:
                #     logging.debug("left")
                #     # turn left
                #     self.motor.setMotorModel(-500,-500,2000,2000)
                # elif float(x) > 207.5:
                #     logging.debug("right")
                #     # turn right
                #     self.motor.setMotorModel(2000,2000,-500,-500)
                # else:
                #     logging.debug("forward, no face")
                #     # face centered in frame, continue forward motion
                #     self.motor.setMotorModel(2000,2000,2000,2000)

                # if boundary line detected, stop car and initiate return home sequence
                

    def face_detect(self,img):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray,1.3,5)
        face_x, face_y = None, None
        if len(faces)>0 :
            for (x,y,w,h) in faces:
                face_x=float(x+w/2.0)
                face_y=float(y+h/2.0)
        else:
            face_x=0
            face_y=0

        return face_x, face_y



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

def init_guard_dog(server, cond):
    video_thread = Thread(target=server.sendvideo, daemon=True) # daemon=True to make thread terminate as soon as guard dog protocol below terminates
    video_thread.start()

    # initialize guard dog object
    dog = GuardDog()
    dog.initiate_protocol(server)

    time.sleep(20)


if __name__ == '__main__':

    # initialize condition variable to indicate whether dog is on patrol or not 
    # to synchronize battery and termination threads
    on_patrol = Condition()

    # initialize and launch server
    server = Server()
    server.StartTcpServer()

    # launch battery thread to continuously monitor battery and take action if battery level drops 
    # below acceptable voltage
    battery_thread = Thread(name="Battery Thread", target=monitor_battery, args=[on_patrol])
    # launch server thread to receive video stream from guard dog
    server_thread = Thread(name="Server Thread", target=init_guard_dog, args=[server, on_patrol])
    # launch thread to shut down other threads if return to dog house initiated
    return_thread = Thread(name="Return Thread", target=terminate_guard_dog_protocol, args=[on_patrol, server_thread, server])

    # battery_thread.start()
    
    server_thread.start()
    # return_thread.start()


    # server_thread.join()
    # logging.debug("server thread joined")
    

