"""
----------------------------------------v.2.2 제작 내용----------------------------------------
명령어 함수 추가
"""

import sys
import serial
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtWidgets import *
from PyQt6 import uic


form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #for i in range(1, 14):
            #self.CB_port.addItem("COM" + str(i))
        self.CB_port.addItem("COM6")

        #self.CB_baudrate.addItems(["1200","2400", "4800", "9600", "38400", "57600", "115200","230400","460800","921600"])
        self.CB_baudrate.addItems(["115200","230400","460800","921600"])

        self.pushButton.clicked.connect(self.showText)
        self.pushButton2.clicked.connect(self.disconnectSerial)
        self.pushButton_BTscan.clicked.connect(self.BT_scan)


        self.ser = None
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValue)
        self.timer.start(100)

        #if self.ser.isOpen():
            #print(self.ser.in_waiting)


        self.setWindowTitle("cansat 2024")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))
        self.pixmap = QPixmap("hanbyeol_stars.jpg")
        scaled_pixmap = self.pixmap.scaled(1200, 960, Qt.KeepAspectRatio)
        self.label_image.setPixmap(scaled_pixmap)

    def updateValue(self):
        try:
            if self.ser and self.ser.isOpen():
                data = self.ser.read()
                print(f"Received data: {data}")

                self.lineEdit_SerialRead.setText(f"Received data: {data}")

                decoded_data = data.decode()
                print(decoded_data)
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
                #else:
                    #print("Data does not start with 'STR:' or 'IMG:'")

        except Exception as e:
            print(f"Error updating value: {e}")

    def showText(self):
        try:
            if self.ser and self.ser.isOpen():
                self.ser.close()

            print('a')
            port = self.CB_port.currentText()
            print('b')
            baudrate = int(self.CB_baudrate.currentText())
            print('c')
            self.ser = serial.Serial(port, baudrate, timeout=5)
            print('d')
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
        
    def BT_scan(self):
        self.ser.write(b'\r\nAT+BTSCAN\r\n')
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
