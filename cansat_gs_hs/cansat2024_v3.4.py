# hevent
# 이미지 디코딩
# 센서 데이터 실시간 표시
# UI 개선
# CSV 파일로 저장
import numpy as np
import cv2
import sys
import serial
import threading
import time
import datetime as dt
import csv
import os
import base64
import chardet  # chardet 라이브러리 임포트
from queue import Queue
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic
import copy

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

data = ''
csv_data = []
foldername = ''

def read_data(ser, queue, stop_event):
    global data
    while not stop_event.is_set():
        try:    
            if ser and ser.isOpen():
                
                raw_data = ser.read()
                #print(raw_data)

                if  raw_data != b'' and raw_data != b'\r' and raw_data != b'\n':
                    data += str(raw_data)[2:-1]

                if raw_data == b'\n' and len(data)>1:
                    queue.put(data)
                    #print(data)
                    data=''
        except Exception as e:
            print(f"Error reading data: {e}")

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_connect.clicked.connect(self.connectSerial)
        self.pushButton_disconnect.clicked.connect(self.disconnectSerial)
        self.pushButton_BTscan.clicked.connect(self.BT_scan)
        self.pushButton_ATZ.clicked.connect(self.ATZ)
        self.pushButton_115200.clicked.connect(self.UARTCONFIG_115200)
        self.pushButton_921600.clicked.connect(self.UARTCONFIG_921600)
        self.pushButton_sendCMD.clicked.connect(self.chk_user_CMD)
        self.pushButton_save_csv.clicked.connect(self.save_csv)
        self.pushButton_queueClear.clicked.connect(self.queueClear)

        

        self.queue = Queue()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkQueue)
        #
        self.timer.timeout.connect(self.showCurTime)
        self.timer.start(100)

        self.initUI()

    def initUI(self):
        for i in range(1, 14):
            self.CB_port.addItem("COM" + str(i))

        self.CB_baudrate.addItems(["1200","2400", "4800", "9600", "38400", "57600", "115200","230400","460800","921600"])

        self.setWindowTitle("cansat 2024 GS")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))

        self.pixmap = QPixmap("grass")
        scaled_pixmap = self.pixmap.scaled(600, 450, Qt.KeepAspectRatio)
        self.label_image_left.setPixmap(scaled_pixmap)
        self.label_image_right.setPixmap(scaled_pixmap)


        self.show_GPS_map(0,0)

        self.pixmap_3D = QPixmap("cansat_3D")
        scaled_pixmap_3D = self.pixmap_3D.scaled(440, 440, Qt.KeepAspectRatio)
        self.label_image_3D.setPixmap(scaled_pixmap_3D)

        self.ser = None
        self.connect = False
        self.thread = None
        self.stop_event = threading.Event()

        self.IMU_data = ''

        self.folder_name = ''
        self.Lattitue = -1
        self.Longitude = -1
        self.Altitude = -1


    def create_GPS_map(self,Lat,Lon):


        GPSmap = np.zeros((440, 440, 3), dtype=np.uint8)
        color = (255, 255, 255)
        thickness = 2
        radius = [40, 80, 120, 160, 200]
        for R in radius:
            cv2.circle(GPSmap, (220,220), R, color, thickness)

        cv2.circle(GPSmap, (220+int(Lon*10000*11.1), 220-int(Lat*10000*11.1)), 3, (0,255,0), 5)

        GPSmap = cv2.cvtColor(GPSmap, cv2.COLOR_BGR2RGB)
        return GPSmap

    def queueClear(self):
        print(self.queue.qsize())
        self.queue.queue.clear()

    def showCurTime(self):
        self.KST = str(dt.datetime.now())[11:19]
        self.label_gstime.setText("GS Time : "+self.KST)

    def temp_CMD(self):
        text = self.lineEdit_sendCMD.text() 
        self.label_sendCMD.setText(f"send : {text}")
        if self.ser and self.ser.isOpen():
            self.ser.write(f'{text}\r\n'.encode())
            print(f"send : {text}")

    def chk_user_CMD(self):
        cmd = self.lineEdit_sendCMD.text()
        self.send_user_CMD(cmd)

    def send_user_CMD(self, cmd):
        #cmd = self.lineEdit_sendCMD.text() 
        i=8
        while i<len(cmd) and self.ser and self.ser.isOpen():
            self.ser.write(f'{cmd[i-8:i]}'.encode())
            i+=8

        if self.ser and self.ser.isOpen():
            self.ser.write(f'{cmd[i-8:]}\r\n'.encode())
            print(f"send : {cmd}")

        self.label_sendCMD.setText(f"send : {cmd}")
        
    def save_csv(self):
        global csv_data
        print("save_csv")
        now = str(dt.datetime.now())[11:19].replace(':','-')
        with open(f'{self.folder_name}/cansat log {now}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['sensor', 'time', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
            for row in csv_data:
                writer.writerow(row)

    def checkQueue(self):
        if not self.queue.empty():
            data = self.queue.get()
            self.process_data(data)

    def process_data(self, data):
        try:
            global csv_data
            if data:
                #self.lineEdit_SerialRead.setText(f"{data}")
                #print(data)
                if data[0]=='*':
                    value = ('IMU,'+data[1:]).split(',')
                    self.IMU_data = copy.deepcopy(value)
                    
                    value.insert(1,self.KST)
                    csv_data.append(value)

                elif data[0]=='$':
                    value = ['GPS',*(data.split(',')[1:])]
                    self.show_GPS(value)
                    if len(self.IMU_data)>0:
                        self.show_IMU(self.IMU_data)
                
                elif data[0]=='@':
                    l = ['TIME',self.KST,data[1:]]
                    csv_data.append(l)

                # elif data[:2]=='&0':
                #     pass
                    
                # elif data[:2]=='&1':
                #     pass
                
                else:
                    self.check_data(data)
                    

        except Exception as e:
            print(f"Error processing data: {e}")

    def check_data(self, data):
        print(data)
        self.lineEdit_SerialRead.setText(f"{data}, {self.KST}")

        sentence = data.split(' ')
        if sentence[0] == 'CONNECT':
            self.label_Bluetooth_connect.setText("Bluetooth connect : True")
            self.label_Bluetooth_ID.setText(f"Bluetooth ID : {sentence[1]}")
            
            today = str(dt.datetime.now())
            today = today.replace('-','')
            today = today.replace(':','')
            today = today.replace('.','')
            today = today.replace(' ','-')
            current = today[:15] 
            os.makedirs(f"cansat_data_{current[:8]}/{current[9:]}")  

            self.folder_name = f"cansat_data_{current[:8]}/{current[9:]}"
            global foldername
            foldername = self.folder_name

            print(self.folder_name)

        if sentence[0] == 'DISCONNECT':
            self.label_Bluetooth_connect.setText("Bluetooth connect : False")
            self.label_Bluetooth_ID.setText("Bluetooth ID : ")

            self.save_csv()
        

    def show_IMU(self, value):
        try: 
            self.label_yaw.setText(f"yaw : {value[1]}")
            self.label_pitch.setText(f"pitch : {value[2]}")
            self.label_roll.setText(f"roll : {value[3]}")
            self.label_a_X.setText(f"aX : {value[4]}")
            self.label_a_Y.setText(f"aY : {value[5]}")
            self.label_a_Z.setText(f"aZ : {value[6]}")
            self.label_Diff_X.setText(f"DiffX : {value[10]}")
            self.label_Diff_Y.setText(f"DiffY : {value[11]}")
            self.label_Diff_Z.setText(f"DiffZ : {value[12]}")

            # global csv_data
            # csv_data.append(value)

        except Exception as e:
            print(f"IMU error: {e}")

    def show_GPS(self, value):
        try:
            if value[2]!='':
                self.label_Lattitue.setText(f"Lattitue : {value[2]}N")
            if value[4]!='':
                self.label_Longitude.setText(f"Longitude : {value[4]}E")
            if value[9]!='':
                if self.Altitude == -1:
                    self.Altitude = value[9]
                self.label_Altitude.setText(f"Altitude : {value[9]-self.Altitude}")


            if value[2]!='' and value[4]!='':
                if self.Lattitue == -1 and self.Longitude == -1:
                    self.Lattitue = value[2]
                    self.Longitude = value[4]
                
                self.show_GPS_map(int(value[2]-self.Lattitue), int(value[4])-self.Longitude)

            global csv_data
            value.insert(1,self.KST)
            csv_data.append(value)
        
        except Exception as e:
            print(f"GPS error: {e}")

    def show_GPS_map(self, Lat, Lon):
        image = self.create_GPS_map(Lat, Lon)
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        scaled_q_image = QPixmap.fromImage(q_image).scaled(440, 440, Qt.KeepAspectRatio)
        self.label_image_GPS.setPixmap(scaled_q_image)

    def show_image(self, value):
        print("image")

        global csv_data
        csv_data.append(["image","filename"])

    def connectSerial(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()

            port = self.CB_port.currentText()
            baudrate = int(self.CB_baudrate.currentText())
            try:
                self.ser = serial.Serial(port, baudrate, timeout=1)
                self.lineEdit.setText(f"Connected to {port} with {baudrate} baudrate")
                self.label_Port.setText(f"Port: {port}")
                self.label_Baudrate.setText(f"Baudrate: {baudrate}")
                self.label_Serial_connect.setText("Serial connect : True")
                print(f"Connected to {port} with {baudrate} baudrate")
                self.connect = True
                
                if self.thread is None:
                    self.stop_event.clear()
                    self.thread = threading.Thread(target=read_data, args=(self.ser, self.queue, self.stop_event), daemon=True)
                    self.thread.start()

            except serial.SerialException as e:
                self.lineEdit.setText(f"Failed to connect to {port}: {e}")
                print(f"Failed to connect to {port}: {e}")
                self.ser = None

        except Exception as e:
            self.lineEdit.setText(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")
    
    def disconnectSerial(self):
        try:
            if self.ser and self.ser.isOpen():
                self.stop_event.set()  # 스레드 중지 이벤트 설정
                self.thread.join(timeout=1)  # 스레드 종료 대기
                self.thread = None

                self.ser.close()
                self.label_Port.setText("Port: ")
                self.label_Baudrate.setText("Baudrate: ")
                self.lineEdit.setText("Serial disconnected")
                print("Serial disconnected")
                self.label_Serial_connect.setText("Serial connect : False")
                self.connect = False

        except Exception as e:
            print(f"{e}")

    # def get_pixmap_from_data(self, image_data):
    #     try:
    #         image = QImage.fromData(image_data)
    #         pixmap = QPixmap.fromImage(image)
    #         return pixmap
    #     except Exception as e:
    #         print(f"Error converting image data: {e}")
    #         return self.pixmap

    def BT_scan(self):
        self.send_user_CMD('AT+BTSCAN')

    def ATZ(self):
        self.send_user_CMD('ATZ')

    def AT_F(self):
        self.send_user_CMD('AT_F')
    
    def UARTCONFIG_115200(self):
        self.send_user_CMD('AT+UARTCONFIG,115200,N,1')

    def UARTCONFIG_921600(self):
        self.send_user_CMD('AT+UARTCONFIG,921600,N,1')

if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

    
    # global csv_data
    if len(csv_data)!=0:
        print("save_csv")
        now = str(dt.datetime.now())[11:19].replace(':','-')
        with open(f'{foldername}/cansat log {now}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['sensor', 'time', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
            for row in csv_data:
                writer.writerow(row)

