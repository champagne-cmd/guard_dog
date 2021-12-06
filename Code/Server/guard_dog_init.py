'''
Main file for guard dog
Launches server, client, and battery threads to initiate guard dog service
'''

from threading import Thread, Condition
#from Code.Client.Thread import stop_thread
from Thread import *
from ADC import *
from Line_Tracking import Line_Tracking
from server import Server
from Ultrasonic import * 
from Buzzer import *

class GuardDog:
    def __init__(self):
        self.ultrasonic = Ultrasonic()
        self.line_tracking = Line_Tracking()
        self.buzzer = Buzzer()

    # def run(self):
    #     buzzer_thread = Thread(target=self.buzzer.bark)
    #     buzzer_thread.start()

def return_home():
    tracker = Line_Tracking()
    tracker.run() # need to modify to stop once ultrasonic sensors detect box in path

def terminate_guard_dog_protocol(on_patrol, client_thread, server_thread, server):
    with on_patrol:
        on_patrol.wait()

        # stop all other threads and server once no longer on patrol
        stop_thread(client_thread)
        stop_thread(server_thread)
        server.server_socket.shutdown(2)
        server.server_socket1.shutdown(2)
        server.StopTcpServer()

        # make dog return to house
        return_home()

def monitor_battery(on_patrol):
    adc = Adc()
    patrolling = True
    with on_patrol:
        while patrolling:
            # read the battery voltage
            power = adc.recvADC(2)*3.0
            # if voltage below 7 V, initiate return to home by signalling on cond. var.
            if power < 7.0:
                print("Battery running low, returning to dog house")
                patrolling = False
                on_patrol.notifyAll()

def init_guard_dog(server):
    # initialize guard dog object?

    # start in dormant state (perhaps states incapsulated in guard dog object)

    # transition to attack state upon detection of motion/faceg

    # return to dog house upon meeting perimeter
    pass


if __name__ == '__main__':
    gd = GuardDog()
    gd.run()

    # # initialize condition variable to indicate whether dog is on patrol or not
    # on_patrol = Condition()

    # # initialize and launch server
    # server = Server()
    # server.startTcpServer()

    # # launch battery thread to continuously monitor battery and take action if battery level drops 
    # # below acceptable voltage
    # battery_thread = Thread(target=monitor_battery, args=(on_patrol))
    # # launch server thread to receive video stream from guard dog
    # server_thread = Thread(target=server.readdata)
    # # launch client thread to initiate guard dog protocol
    # client_thread = Thread(target=init_guard_dog, args=(server))
    # # launch thread to shut down other threads if return to dog house initiated
    # return_thread = Thread(target=terminate_guard_dog_protocol, args=(on_patrol, client_thread, server_thread, server))

    # battery_thread.start()
    # server_thread.start()
    # client_thread.start()
    # return_thread.start()