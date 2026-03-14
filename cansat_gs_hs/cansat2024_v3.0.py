"""
----------------------------------------v.3.0 제작 내용----------------------------------------

캔위성이랑 연결하는거 까지 제작 완료

연결은 성공 했는데 수신한 데이터 decode가 제대로 안돼서 출력됨

입력 큐 처리가 느림
시리얼 연결을 끊어도 남아있는 큐 때문에 데이터가 계속 들어옴. 스레드 처리때문에 오류가능성 있음. 데이터 입력 부분에 시리얼 연결 조건문 있는데도 오류남
많은 데이터 큐 때문에 User CMD에 대한 피드백을 볼 수가 없음

시리얼을 끊었다가 다시 연결해도 남아있는 큐 때문에 큐 클리어하는 함수를 만들었는데, 큐 클리어를 하면 터짐
-> 캔위성과 재연결을 해도 명령에 대한 대답을 못봄 (명령에 대한 답장이 안옴 or 답장은 왔는데 출력에서 오류남)

현재시간을 출력하는거 만드는 도중 오류가 남

----------------------------------------앞으로 해야할 것----------------------------------------

1. 캔위성 블루투스 연결
- 수신 데이터에 따른 decode 방식 변경
- 수신 데이터 종류 분류 후 UI 송출
- 시리얼 큐 문제 해결

2. UI 개편
- GPS 데이터 표시 추가
- 캔위성 3D 자세 표시 추가
- 센서값 데이터 출력 위치 조정
- 이미지 데이터 출력 위치 조정
- UI 현재 시간 표시
- 수신 데이터 로그 기능 추가
- User CMD 위치 조정
- 시리얼 연결 위치 조정
"""

import sys
import serial
import threading
import time
# import chardet
from queue import Queue
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

def read_data(ser, queue):
    while True:
        try:
            if ser and ser.isOpen():
                data = ser.readline().strip()
                #print(f"Received data: {data}")
                queue.put(data)
        except Exception as e:
            print(f"Error reading data: {e}")

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.showText)
        self.pushButton2.clicked.connect(self.disconnectSerial)
        self.pushButton_BTscan.clicked.connect(self.BT_scan)
        self.pushButton_sendCMD.clicked.connect(self.button_event)
        self.pushButton_queueClear.clicked.connect(self.queueClear)

        self.queue = Queue()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkQueue)
        #self.timer.timeout.connect(self.showCurTime)
        self.timer.start(100)

        self.initUI()

    def initUI(self):
        for i in range(1, 14):
            self.CB_port.addItem("COM" + str(i))

        self.CB_baudrate.addItems(["1200","2400", "4800", "9600", "38400", "57600", "115200","230400","460800","921600"])

        self.setWindowTitle("cansat 2024")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))
        self.pixmap = QPixmap("hanbyeol_stars.jpg")
        # scaled_pixmap = self.pixmap.scaled(1200, 960, Qt.KeepAspectRatio)
        # self.label_image.setPixmap(scaled_pixmap)
        scaled_pixmap = self.pixmap.scaled(600, 450, Qt.KeepAspectRatio)
        self.label_image_left.setPixmap(scaled_pixmap)

        self.ser = None
        self.connect = False
        self.thread = None

    def queueClear(self):
        print(self.queue.qsize())
        self.queue.queue.clear()

    def showCurTime(self):
        self.lineEdit_curTime.setText(time.time())

    def button_event(self):
        text = self.lineEdit_sendCMD.text() 
        self.label_sendCMD.setText(f"send : {text}")
        if self.ser and self.ser.isOpen():
            self.ser.write(f'{text}\r\n'.encode())
            print(f"send : {text}")


    def checkQueue(self):
        if not self.queue.empty():
            data = self.queue.get()
            self.process_data(data)

    def process_data(self, data):
        try:
            if data:
                self.lineEdit_SerialRead.setText(f"Received data: {data} , {time.time()}")
                value = data.decode()
                
                print(value)

                # result = chardet.detect(data)
                # encoding = result['encoding']
                # print(f"Detected encoding: {encoding}")

                # decoded_data = data.decode(encoding)
                # print(f"Decoded data: {decoded_data}")
                # self.label_light.setText(f"light: {decoded_data}")

        except Exception as e:
            print(f"Error processing data: {e}")



    def showText(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()

            port = self.CB_port.currentText()
            baudrate = int(self.CB_baudrate.currentText())
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.lineEdit.setText(f"Connected to {port} with {baudrate} baudrate")
            print(f"Connected to {port} with {baudrate} baudrate")
            self.connect = True

            if self.thread is None:
                self.thread = threading.Thread(target=read_data, args=(self.ser, self.queue), daemon=True)
                self.thread.start()

        except Exception as e:
            self.lineEdit.setText(f"Failed to connect to {self.CB_port.currentText()}")
            print(f"Failed to connect to {self.CB_port.currentText()}")

    def disconnectSerial(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()
                self.lineEdit.setText("Serial disconnected")
                print("Serial disconnected")
                self.connect = False

            if self.thread is not None:
                self.thread.join(timeout=1)
                self.thread = None

        except Exception as e:
            print(f"{e}")

    def get_pixmap_from_data(self, image_data):
        try:
            image = QImage.fromData(image_data)
            pixmap = QPixmap.fromImage(image)
            return pixmap
        except Exception as e:
            print(f"Error converting image data: {e}")
            return self.pixmap

    def BT_scan(self):
        if self.ser and self.ser.isOpen():
            self.ser.write(b'AT+BTSCAN\r\n')
            print("AT+BTSCAN")

    def ATZ(self):
        if self.ser and self.ser.isOpen():
            self.ser.write(b'AT\r\n')
            print("AT")

    def AT_F(self):
        if self.ser and self.ser.isOpen():
            self.ser.write(b'AT&F\r\n')
            print("AT&F")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
