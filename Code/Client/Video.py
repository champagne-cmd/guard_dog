#!/usr/bin/python 
# -*- coding: utf-8 -*-
from posix import listdir
import numpy as np
import cv2
import socket
import io
import sys
import struct
import os
import time
from PIL import Image
from multiprocessing import Process
from Command import COMMAND as cmd



class VideoStreaming:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(r'haarcascade_frontalface_default.xml')
        self.video_Flag=True
        self.connect_Flag=False
        self.face_x=0
        self.face_y=0
        self.count = 0
        self.intervalChar='#'
        self.endChar='\n'

    def StartTcpClient(self,IP):
        self.client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def StopTcpcClient(self):
        try:
            self.client_socket.shutdown(2)
            self.client_socket1.shutdown(2)
            self.client_socket.close()
            self.client_socket1.close()
        except:
            pass

    def IsValidImage4Bytes(self,buf): 
        bValid = True
        if buf[6:10] in (b'JFIF', b'Exif'):     
            if not buf.rstrip(b'\0\r\n').endswith(b'\xff\xd9'):
                bValid = False
        else:        
            try:  
                Image.open(io.BytesIO(buf)).verify() 
            except:  
                bValid = False
        return bValid


    def face_detect(self,img):
        if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray,1.3,1)
            if len(faces)>0 :
                for (x,y,w,h) in faces:
                    self.face_x=float(x+w/2.0)
                    self.face_y=float(y+h/2.0)
                    img= cv2.circle(img, (int(self.face_x),int(self.face_y)), int((w+h)/4), (0, 255, 0), 2)
            else:
                self.face_x=0
                self.face_y=0
        
        print("face x position: " + str(self.face_x))
        if(self.face_x == 0):
            self.send_Keep_Straight()
        elif(self.face_x < 192.5):
            print("turning left")
            self.send_Turn_Left()
        elif(self.face_x > 207.5):
            print("turning right")
            self.send_Turn_Right()
        else: 
            self.send_Keep_Straight()

        time.sleep(.15)


        
    def send_Turn_Right(self):
        Turn_Right=self.intervalChar+str(1000)+self.intervalChar+str(1000)+self.intervalChar+str(-750)+self.intervalChar+str(-750)+self.endChar
        self.sendData(cmd.CMD_MOTOR+Turn_Right)
    
    def send_Turn_Left(self):
        Turn_Left=self.intervalChar+str(-750)+self.intervalChar+str(-750)+self.intervalChar+str(1000)+self.intervalChar+str(1000)+self.endChar
        self.sendData(cmd.CMD_MOTOR+ Turn_Left)

    def send_Keep_Straight(self):
        Keep_Straight=self.intervalChar+str(650)+self.intervalChar+str(650)+self.intervalChar+str(650)+self.intervalChar+str(650)+self.endChar
        self.sendData(cmd.CMD_MOTOR+ Keep_Straight)
    
    def streaming(self,ip):
        stream_bytes = b' '
        try:
            self.client_socket.connect((ip, 8000))
            self.connection = self.client_socket.makefile('rb')
        except:
            #print "command port connect failed"
            pass
        
        # removes all images from previous runs
        for image in os.listdir("./images/"):
            os.remove(os.path.join("./images/", image))


        img_array = []
        
        while True:
            try:
                stream_bytes= self.connection.read(4) 
                leng=struct.unpack('<L', stream_bytes[:4])
                jpg=self.connection.read(leng[0])
                if self.IsValidImage4Bytes(jpg):
                            image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                            if self.video_Flag:
                                self.face_detect(image)
                                self.video_Flag=False

                            filename = './images/image' + str(self.count) + ".jpg"
                            cv2.imwrite(filename,image)
                            self.count += 1
                            img_array.append(image)
                
            except Exception as e:
                print (e)
                height, width, layers = img_array[0].shape
                size = (width, height)
                out = cv2.VideoWriter('project.mp4',cv2.VideoWriter_fourcc(*'MP4V'), 3, size)
                for i in range(len(img_array)):
                    out.write(img_array[i])
                out.release()
                break
                  
    def sendData(self,s):
        if self.connect_Flag:
            self.client_socket1.send(s.encode('utf-8'))

    def recvData(self):
        data=""
        try:
            data=self.client_socket1.recv(1024).decode('utf-8')
        except:
            pass

        return data

    def socket1_connect(self,ip):
        try:
            self.client_socket1.connect((ip, 5000))
            self.connect_Flag=True
            print ("Connecttion Successful !")
        except Exception as e:
            print ("Connect to server Faild!: Server IP is right? Server is opend?")
            self.connect_Flag=False

if __name__ == '__main__':
    pass

