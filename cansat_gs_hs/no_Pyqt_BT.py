import serial
from queue import Queue
import datetime as dt
Rx_Queue = Queue()
Tx_Queue = Queue()

global BT_serial
global BT_Buf
global BT_Raw_Data
global Rx_Data

global Received_Data

# ------------------------------------------------- Serial Connection -------------------------------------------------


def BT_connect(baudrate):
    global BT_serial
    # connect to Firmtech FB755AS
    BT_serial = serial.Serial(port='COM4', baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0.001)
# BT_serial = serial.Serial(port='/dev/ttyAMA0', baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0.001)


def BT_Port_Speed_Set(baudrate):
    global BT_serial

    # reset Baud rate
    BT_serial.close()

    # when connect to usb
    # BT_serial = serial.Serial('/dev/ttyUSB0', baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0.001)

    # when connect to GPIO pins (tx4,rx5)
# BT_serial = serial.Serial(port='/dev/ttyAMA0', baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0.001)
    BT_serial = serial.Serial(port='COM5', baudrate=baudrate, bytesize=8, parity='N', stopbits=1, timeout=0.001)

# ---------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------- Bluetooth Command -------------------------------------------------

def BT_ATZ():  # BT Software Reset
    print("BT ATZ")
    BT_serial.write(b'ATZ\r')
    BT_Rx_Op()


def BT_ATF():  # BT Hard Reset / Factory Reset
    print("BT ATF")
    BT_serial.write(b'AT&F\r')
    BT_Rx_Op()

    BT_Port_Speed_Set(9600)


def BT_AT():  # BT Connection Status
    print("BT AT")
    BT_serial.write(b'AT\r')
    BT_Rx_Op()


def BT_921600():  # Set BT Baud Rate 921600 and Reconnect BT
    print("BT 921600")
    BT_serial.write(b'AT+UARTCONFIG,921600,N,1,0\r')
    BT_Rx_Op()

    BT_Port_Speed_Set(921600)

    BT_ATZ()


def BT_115200():  # Set BT Baud Rate 115200 and Reconnect BT
    print("BT 115200")
    BT_serial.write(b'AT+UARTCONFIG,115200,N,1,0\r\n')
    BT_Rx_Op()

    BT_Port_Speed_Set(115200)

    BT_ATZ()


def BT_9600():  # Set BT Baud Rate 9600 and Reconnect BT
    print("BT 9600")
    BT_serial.write(b'AT+UARTCONFIG,9600,N,1,0\r\n')
    BT_Rx_Op()

    BT_Port_Speed_Set(9600)
    BT_ATZ()


def BT_INFO():  # Answer BT INFO
    print("BT INFO")
    BT_serial.write(b'AT+BTINFO?\r')
    BT_Rx_Op()  # For Setting Data
    BT_Rx_Op()  # For OK


def BT_INQ():  # This Function Takes Time / Search BT Waiting to Connect
    print("BT INQ")
    global Received_Data
    Received_Data = ""
    BT_CANCEL()
    BT_serial.write(b'AT+BTINQ?\r')

    while Received_Data != 'OK':
        Received_Data = BT_Rx_Op()


def BT_LAST():  # Answer Last Connected BT Address
    print("BT LAST")
    BT_serial.write(b'AT+BTLAST?\r')
    BT_Rx_Op()


def BT_Sensitivity_Test_Start():  # BT Sensitivity Test Start
    print("BT Sensitivity Test Start")
    BT_STOP()

    BT_serial.write(b'AT+BTRSSI,1\r')
    BT_Rx_Op()  # For OK
    BT_Rx_Op()  # For Test Data


def BT_Sensitivity_Test_Stop():  # BT Sensitivity Test Stop
    print("BT Sensitivity Test Stop")
    BT_STOP()

    BT_serial.write(b'AT+BTRSSI,0\r')
    BT_Rx_Op()


def BT_MODE3():  # BT Set Mode 3
    print("BT MODE3")
    BT_CANCEL()

    BT_serial.write(b'AT+BTMODE,3\r')
    BT_Rx_Op()

    BT_ATZ()
    return


def BT_MODE0():  # BT Set Mode 0
    print("BT MODE0")
    BT_CANCEL()

    BT_serial.write(b'AT+BTMODE,0\r')
    BT_Rx_Op()

    BT_ATZ()
    return


def BT_STOP():  # BT Stop / Use When BT is Online
    print("BT STOP")
    BT_serial.write(b'+++\r')  # str.encode('+')
    BT_Rx_Op()


def BT_ATO():  # BT Set to Online
    print("BT ATO")
    BT_serial.write(b'ATO\r')


def BT_CANCEL():  # BT Force quit
    print("BT CANCEL")
    BT_serial.write(b'AT+BTCANCEL\r')
    BT_Rx_Op()


def BT_SCAN():  # Set BT Standby
    print("BT SCAN")
    BT_serial.write(b'AT+BTSCAN\r')
    BT_Rx_Op()


def BT_ATD():  # BT Reconnect
    print("BT ATD")
    BT_serial.write(b'ATD\r')
    BT_Rx_Op()

def BT_ATD0001955BA300():  # BT Reconnect
    print("BT ATD0001955BA300")
    BT_serial.write('ATD0001955BA300\r\n'.encode())
    BT_Rx_Op()


def BT_ATH():  # BT Disconnect
    print("BT ATH")
    BT_serial.write(b'ATH\r')
    BT_Rx_Op()

# ---------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------ Bluetooth Operation ------------------------------------------------

def BT_Init_Set():  # BT Initial Setting / When First Connected
    BT_connect(9600)
    BT_ATF()
    BT_9600()
    BT_ATZ()
    BT_MODE3()
    BT_921600()


def BT_Init():  # BT Init / When Turned On
    BT_connect(921600)
    BT_SCAN()
    BT_INFO()


def BT_Tx_Byte(data):  # BT Tx Byte
    BT_serial.write(str.encode(data))


def BT_Trans_UART_Until(cnt):
    for loop_cnt in range(cnt):
        BT_Tx_Byte(Tx_Queue.get())


def BT_Rx_Op():  # BT Rx Operation / TODO : Make System Parallel

    global BT_Buf  # for esd110
    global Rx_Data
    global BT_Raw_Data

    BT_Buf = ""
    Rx_Data = ""
    # read esd110 value
    while True:
        while BT_serial.inWaiting():

            BT_Raw_Data = BT_serial.read()

            if BT_Raw_Data != b'\r' and BT_Raw_Data != b'\n':
                BT_Buf += str(BT_Raw_Data)  # buffering
                BT_Buf = BT_Buf.replace("'", "")  # remove (') and (b)
                BT_Buf = BT_Buf.replace("b", "")

                Rx_Queue.put(BT_Buf)

            # print(f'BT Buf : {BT_Buf}')  # for Debug

            if BT_Raw_Data == b'\n' and Rx_Queue.qsize() > 1:
                for index in range(Rx_Queue.qsize()):
                    Rx_Data += Rx_Queue.get()

                print(Rx_Data)
                return Rx_Data

            BT_Buf = ""


if __name__ == "__main__":

    BT_connect(921600)

    if BT_serial.is_open:
        print("BT OPEN")
    else:
        print("BT NOT OPEN")

    # TODO : BT Loop
    BT_ATD0001955BA300()
    while True:
        BT_Rx_Op()
        print(dt.datetime.now())
        
