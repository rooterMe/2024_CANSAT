"""
----------------------------------------v.2.1 제작 내용----------------------------------------
수신한 데이터의 종류(문자, 숫자, 이미지)에 따라 UI에 표시 추가
BT_SCAN 버튼 추가
"""

import sys
import serial
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        for i in range(1, 14):
            self.CB_port.addItem("COM" + str(i))

        self.CB_baudrate.addItems(["1200","2400", "4800", "9600", "38400", "57600", "115200","230400","460800","921600"])

        self.pushButton.clicked.connect(self.showText)
        self.pushButton2.clicked.connect(self.disconnectSerial)
        self.pushButton_BTscan.clicked.connect(self.BT_scan)

        self.ser = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValue)
        self.timer.start(100)



        self.setWindowTitle("cansat 2024")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))
        self.pixmap = QPixmap("hanbyeol_stars.jpg")
        scaled_pixmap = self.pixmap.scaled(1200, 960, Qt.KeepAspectRatio)
        self.label_image.setPixmap(scaled_pixmap)

    def BT_scan(self):
        self.ser.write(b'\r\nAT+BTSCAN\r\n')
        #self.ser.write(b'AT+BTSCAN\r\n')
        print("AT+BTSCAN")
    
    def updateValue(self):
        try:
            if self.ser and self.ser.isOpen():
                data = self.ser.readline().strip()
                print(f"Received data: {data}")

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
            print(f"Error updating value: {e}")

    def showText(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()

            port = self.CB_port.currentText()
            baudrate = int(self.CB_baudrate.currentText())
            self.ser = serial.Serial(port, baudrate, timeout=1)
            self.lineEdit.setText(f"Connected to {port} with {baudrate} baudrate")
        except Exception as e:
            self.lineEdit.setText(f"Failed to connect to {self.CB_port.currentText()}")

    def disconnectSerial(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()
                self.lineEdit.setText("Serial disconnected")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
