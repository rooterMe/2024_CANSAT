import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("qtds_test.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        for i in range(1,14):
            self.COMN.addItem("COM"+str(i))

        self.pushButton.clicked.connect(self.showText)

    def showText(self):
        self.lineEdit.setText(self.COMN.currentText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
