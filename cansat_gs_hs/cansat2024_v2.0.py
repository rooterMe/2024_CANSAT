"""
----------------------------------------v.2.0 제작 내용---------------------------------------- 
Qt 디자이너로 UI 틀 제작
아이콘,타이틀 설정 / 사진 위치 지정 등 기본적인 인터페이스 추가
UI에서 포트와 통신속도를 설정후 버튼을 통해 연결 시도 가능
연결 시도 결과를 UI에 텍스트로 표시
수신한 데이터가 있다면 표시
disconnect 버튼 추가
"""

import sys
import serial
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("cansat2024_QtDs.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        for i in range(1, 14):
            self.CB_port.addItem("COM" + str(i))

        self.CB_baudrate.addItems(["2400", "4800", "9600", "38400", "57600", "115200"])

        self.pushButton.clicked.connect(self.showText)
        self.pushButton2.clicked.connect(self.disconnectSerial)  # Connect pushButton2 to the disconnectSerial method

        self.ser = None 

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValue)
        self.timer.start(100)  
        
        self.setWindowTitle("cansat 2024")
        self.setWindowIcon(QIcon('cansat_icon_tmp.png'))
        pixmap = QPixmap("hanbyeol_stars.jpg")
        scaled_pixmap = pixmap.scaled(1200, 960, Qt.KeepAspectRatio)
        self.label_image.setPixmap(scaled_pixmap)

    def updateValue(self):
        try:
            if self.ser:
                value = self.ser.readline().decode().strip()
                self.label_light.setText(f"light: {value}")
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
            print(f"Error disconnecting serial: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
