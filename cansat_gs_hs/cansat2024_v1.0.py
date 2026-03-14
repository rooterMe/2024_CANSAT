"""
----------------------------------------v.1.0 제작 내용----------------------------------------
코드에서 직접 포트와 통신속도를 성정하여 연결
아두이노와 시리얼 통신해서 데이터가 시리얼로 잘 수신되는지 확인하는 프로그램
"""


from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui
import serial

class YourApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 1400, 700)
        self.setWindowTitle("cansat 2024")

        self.chk = 0

        self.initUI()

    def initUI(self):
        self.label2 = QLabel("Initial Value")
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setFont(QtGui.QFont('Hack', 50))

        self.label3 = QLabel("Text")
        self.label3.setAlignment(Qt.AlignCenter)
        self.label3.setFont(QtGui.QFont('Hack', 50))

        label_layout = QVBoxLayout()
        label_layout.addWidget(self.label2)
        label_layout.addWidget(self.label3)

        self.setLayout(label_layout)

        button = QPushButton("Press Button!")
        button.clicked.connect(self.button_clicked)
        button.setFont(QtGui.QFont('Hack', 15))
        label_layout.addWidget(button, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        self.arduino = serial.Serial('COM4', 9600, timeout=1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateValue)
        self.show()

    def updateValue(self):
        if self.chk == 1:
            value = self.arduino.readline().decode().strip()
            self.label2.setText(f"light : {value}")

    def button_clicked(self):
        print("Button Clicked")
        self.chk = 1
        self.label3.setText(f"Count {self.chk}")
        self.timer.start(2)

if __name__ == '__main__':
    app = QApplication([])
    ex = YourApp()
    app.exec_()
 