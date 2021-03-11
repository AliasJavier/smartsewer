import pyb
from time import sleep
from machine import Pin, I2C


class driver:
    def __init__(self, id=None):
        self.id = id
        self.gsm = pyb.UART(1, 9600, timeout_char=100, read_buf_len=1000)
        self.pwerkey = Pin('X22', Pin.OUT)  # X22,PC3

    def _wait_for_str(self, strtowait):
        rec = ""
        while not strtowait in rec and not "ERROR" in rec:
            rec = self.gsm.read(100)
            if rec is None:
                rec = ""
            else:
              print("waiting rec:", rec)
            sleep(0.1)

    def _power_up(self):
        print("powering up de module")
        self.pwerkey.value(1)
        sleep(1)
        self.pwerkey.value(0)
        sleep(2)
        self.pwerkey.value(1)
        sleep(1)

    def active(self, is_active=None):
        if is_active is True:
            self.gsm.write('AT+CGACT:1\r\n')
            sleep(1)
        if is_active is False:
            self.gsm.write('AT+CGACT:0\r\n')
            sleep(1)
        else:
            self.gsm.write('AT+CGACT=?\r\n')
            sleep(1)

    def connect(self, service_id, pin, apn, user='', key=''):
        rec = ""
        while not "OK" in rec:
            print("sent", self.gsm.write('AT' + '\r\n'))
            rec = self.gsm.read(100)
            print(rec)
            if rec is None:
                rec = ""
            sleep(1)

        self.gsm.write('AT+CREG=1' + '\r\n')

        self._wait_for_str("CREG: 1")
        # self.gsm.write('AT+COPS?'+'\r\n')
        # sleep(2)
        print(self.gsm.read(100))
        print("sent", self.gsm.write('AT+CGATT=1' + '\r\n'))
        self._wait_for_str("OK")
        print(self.gsm.read(100))
        self.gsm.write('AT+UPSD=0,1,"' + apn + '"\r\n')
        sleep(2)
        print(self.gsm.read())
        self.gsm.write('AT+UPSDA=0,1\r\n')
        self._wait_for_str("OK")
        self.gsm.write('AT+UPSDA=0,3\r\n')
        self._wait_for_str("OK")
        self.gsm.write('AT+UPSND=0,0\r\n')
        self._wait_for_str("OK")
        # sleep(2)
        print(self.gsm.read())
        self.gsm.write('AT+UPSND=0,1\r\n')
        self._wait_for_str("OK")
        # sleep(4)
        print(self.gsm.read())
        self.gsm.write('AT+USOCR=6\r\n')
        sleep(2)
        print(self.gsm.read())



    def disconnect(self):
        self.gsm.write('AT+CGATT=0' + '\r\n')
        sleep(1)
        print(self.gsm.read(100))

    def isconnected(self):
        rec = ""
        self.gsm.write('AT+CREG?' + '\r\n')
        rec = self.gsm.read(100)
        print(rec)
        sleep(1)
        if "0,1" in rec:
            return True
        else:
            return False

    def scan(self):
        # por ahora no hay nada que buscar
        print('vacio')

    def status(self, param=None):
        self.gsm.write('AT+CSQ' + '\r\n')
        sleep(1)
        print(self.gsm.read(100))

    def ifconfig(self, ip='', subnet='', gateway='', dns=''):
        self.gsm.write('AT+CIFSR' + '\r\n')
        sleep(4)
        ip = self.gsm.read(100)
        return ip

    def config(self, param=None):
        print('vacio')


















