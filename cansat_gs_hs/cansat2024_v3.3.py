# hevent
# 이미지 디코딩
# 센서 데이터 실시간 표시
# UI 개선
# CSV 파일로 저장

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

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

data = ''
csv_data = []


def read_data(ser, queue, stop_event):
    global data
    while not stop_event.is_set():
        try:
            if ser and ser.isOpen():
                
                raw_data = ser.read()
                # print(raw_data)

                if  raw_data != b'' and raw_data != b'\r' and raw_data != b'\n':
                    data += str(raw_data)[2:-1]

                if raw_data == b'\n' and len(data)>1:
                    queue.put(data)
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
        # self.pushButton_sendCMD.clicked.connect(self.temp_CMD)
        self.pushButton_queueClear.clicked.connect(self.queueClear)

        self.folder_name = ''

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
        self.pixmap = QPixmap("Picture_240613_183559")
        scaled_pixmap = self.pixmap.scaled(600, 450, Qt.KeepAspectRatio)
        self.label_image_left.setPixmap(scaled_pixmap)
        self.label_image_right.setPixmap(scaled_pixmap)
        #self.label_image.setPixmap(self.pixmap)

        self.pixmap_gps = QPixmap("GPS_map_4")
        scaled_pixmap_gps = self.pixmap_gps.scaled(440, 440, Qt.KeepAspectRatio)
        self.label_image_GPS.setPixmap(scaled_pixmap_gps)

        self.pixmap_3D = QPixmap("cansat_3D")
        scaled_pixmap_3D = self.pixmap_3D.scaled(440, 440, Qt.KeepAspectRatio)
        self.label_image_3D.setPixmap(scaled_pixmap_3D)

        self.ser = None
        self.connect = False
        self.thread = None
        self.stop_event = threading.Event()

    def queueClear(self):
        print(self.queue.qsize())
        self.queue.queue.clear()

    def showCurTime(self): #datetime 사용?
        cur_time = time.time()%(60*60*24)
        HH = str(int(cur_time//3600))
        hh = str((int(cur_time//3600)+9)%24)
        MM = str(int((cur_time%3600)//60))
        SS = str(int((cur_time%3600)%60))
        UTC = HH.zfill(2) + ":" + MM.zfill(2) + ":" + SS.zfill(2)
        KST = hh.zfill(2) + ":" + MM.zfill(2) + ":" + SS.zfill(2)
        self.label_UTC.setText("UTC Time : "+UTC)
        self.label_KST.setText("KST(GPS) : "+KST)

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
        
    

    def checkQueue(self):
        if not self.queue.empty():
            data = self.queue.get()
            self.process_data(data)

    def process_data(self, data):
        try:
            if data:
                self.lineEdit_SerialRead.setText(f"{data}")
                print(data)
                if data[0]=='*':
                    value = ('IMU,'+data[1:]).split(',')
                    self.show_IMU(value)

                elif data[0]=='$':
                    value = ['GPS',*(data.split(',')[1:])]
                    self.show_GPS(value)
                
                #elif value[0][0]=='':
                    #self.show_image(value)
                
                else:
                    self.check_data(data)

        except Exception as e:
            print(f"Error processing data: {e}")

    def check_data(self, data):
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
            os.mkdir(f"cansat_data_{current}")

            self.folder_name = f'cansat_data_{current}'

        if sentence[0] == 'DISCONNECT':
            self.label_Bluetooth_connect.setText("Bluetooth connect : False")
            self.label_Bluetooth_ID.setText("Bluetooth ID : ")

            global csv_data

            with open(f'{self.folder_name}/example.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sensor', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
                for row in csv_data:
                    writer.writerow(row)
        

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

            global csv_data
            csv_data.append(value)
        except Exception as e:
            print(f"IMU error: {e}")

    def show_GPS(self, value):
        try:
            self.label_Lattitue.setText(f"Lattitue : {value[2]}N")
            self.label_Longitude.setText(f"Longitude : {value[4]}E")
            self.label_Altitude.setText(f"Altitude : {value[9]}")
            global csv_data
            csv_data.append(value)
        except Exception as e:
            print(f"GPS error: {e}")


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


