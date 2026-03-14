"""
----------------------------------------v.2.3 제작 내용----------------------------------------
멀티 프로세싱으로 병령화 시도 - 멀티프로세싱으로는 PyQt와는 안맞음
연결상태 확인 변수 추가
디버깅 코드 추가

UI 설정 코드를 initUI로 이동하여 깔끔하게 처리
"""

import sys
import serial
import multiprocessing
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        

        self.pushButton.clicked.connect(self.showText)
        self.pushButton2.clicked.connect(self.disconnectSerial)
        self.pushButton_BTscan.clicked.connect(self.BT_scan)

        self.pool = multiprocessing.Pool(processes=2)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.checkSerialAndRead)
        self.timer.start(100)

        self.initUI()

    def initUI(self):
        for i in range(1, 14):
            self.CB_port.addItem("COM" + str(i))

        self.CB_baudrate.addItems(["1200","2400", "4800", "9600", "38400", "57600", "115200","230400","460800","921600"])

        self.setWindowTitle("cansat 2024")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))
        self.pixmap = QPixmap("hanbyeol_stars.jpg")
        scaled_pixmap = self.pixmap.scaled(1200, 960, Qt.KeepAspectRatio)
        self.label_image.setPixmap(scaled_pixmap)

        self.ser = None
        self.connect = False

    def checkSerialAndRead(self):
        print(self.connect)
        if self.connect:
            self.updateValue()
 
    def read_data(self):
        try:
            if self.ser and self.ser.isOpen():
                data = self.ser.readline().strip()
                print(f"Received data: {data}")
                return data
        except Exception as e:
            print(f"Error reading data: {e}")
        return None

    def process_data(self, data):
        try:
            if data:
                self.lineEdit_SerialRead.setText(f"Received data: {data}")

                decoded_data = data.decode()

                if decoded_data.isdigit():
                    value = int(decoded_data)
                    print(f"Received numeric data: {value}")
                    self.label_light.setText(f"light: {value}")
                elif decoded_data.startswith('STR:'):
                    print("Received string data!")
                    value = decoded_data[4:]
                    self.label_light.setText(f"light: {value}")
                elif decoded_data.startswith('IMG:'):
                    print("Received image data!")
                    image_data = decoded_data[4:].encode()
                    pixmap = self.get_pixmap_from_data(image_data)
                    self.label_image.setPixmap(pixmap)
                else:
                    print("Data does not start with 'STR:' or 'IMG:'")
        except Exception as e:
            print(f"Error processing data: {e}")

    def updateValue(self):
        print("updateValue")
        result = self.pool.apply_async(self.read_data)
        data = result.get()
        if data:
            self.pool.apply_async(self.process_data, args=(data,))

    def showText(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()

            port = self.CB_port.currentText()
            baudrate = int(self.CB_baudrate.currentText())
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.lineEdit.setText(f"Connected to {port} with {baudrate} baudrate")
            self.connect = True
        except Exception as e:
            self.lineEdit.setText(f"Failed to connect to {self.CB_port.currentText()}")

    def disconnectSerial(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()
                self.lineEdit.setText("Serial disconnected")
                print("Serial disconnected")
                self.connect = False
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
        self.ser.write(b'\r\nAT+BTSCAN\r\n')
        #self.ser.write(b'AT+BTSCAN\r\n')
        print("AT+BTSCAN")

    def ATZ(self):
        self.ser.write(b'\r\nATZ\r\n')
        print("ATZ")

    def AT_F(self):
        self.ser.write(b'\r\nAT&F\r\n')
        print("AT&F")
       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()