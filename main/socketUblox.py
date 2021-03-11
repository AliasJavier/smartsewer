import pyb
from time import sleep
import io

AF_INET = 2
AF_INET6 = 10

SOCK_DGRAM = 2
SOCK_RAW = 3
SOCK_STREAM = 1






class socket(io.IOBase):
    rx_buf = ""
    rx_bufb = bytearray()
    ok = False
    timeout = 30
    uart2IRQ = None

    def __init__(self, af=AF_INET, type=SOCK_STREAM):
        self.af = af
        self.type = type
        self.gsm = pyb.UART(1, 9600, timeout_char=100, read_buf_len=1000)
        self.rx_bufb = bytearray()
        print("sent", self.gsm.write('AT' + '\r\n'))
        self._wait_for_str("OK")

    def getaddrinfo(self,host, port, af=0, type=0, proto=0, flags=0):
        canonname = flags
        family = (af, (host, port))
        family = self.getaddr(host)
        type = str(port)
        print(family)
        return [family, type, proto, canonname, host]

    def getaddr(self, host):
        self.gsm.write('AT+UDNSRN=0,"'+host+'"\r\n')
        sleep(2)
        string = self.gsm.read()
        print(string)
        string = str(string)
        string = string.split()
        string = string[1]
        address = ''
        i = 0
        while i < len(string):
            if string[i + 1] == 'r':
                break
            address += string[i]
            i += 1
        return address

    def _wait_for_str(self, strtowait):
        rec = ""
        i=0
        while not strtowait in rec:
            rec = self.gsm.read(100)
            if rec is None:
                rec = ""
            else:
              print("waiting rec:", rec)
            sleep(0.1)

    def irq_fun(self, orig):
        rec_bytes = self.gsm.read(self.gsm.any())
        print("r:",rec_bytes)
        if rec_bytes is not None:
            self.rx_bufb += bytearray(rec_bytes)

    def irq_fun_OLD(self, orig):
        rec_bytes = self.gsm.read()
        rec = rec_bytes.decode("ascii")
        print(rec)
        self.rx_buf = self.rx_buf + rec
        self.rx_bufb = self.rx_bufb + rec_bytes
        if "\r\n" in self.rx_buf:
            lines = self.rx_buf.split("\r\n")
            for l in lines:
                if "OK" in l:
                    print("ok received")
                    self.ok = True
                    continue

            if self.rx_buf.endswith("\r\n"):
                self.rx_buf = ""
            else:
                self.rx_buf = lines[-1]

    def close(self):
        print("closing socket")
        sleep(1)
        self.gsm.write("+++")
        sleep(2)
        self.gsm.write('AT+USOCL=0' + '\r\n')
        sleep(1)
        print("Close", self.gsm.read(100))
        self.uart2IRQ = self.gsm.irq(trigger=pyb.UART.IRQ_RXIDLE,
                                     handler=None,
                                     hard=False)

    def bind(self, address):
        print("bind not implemented")
        # no se muy bien (sera una variable)

    def listen(self, backlog=0):
        print("listen not implemented")
        # no se (probablmente un semaforo)

    def accept(self):
        print("accept not implemented")
        # tiene que estar bind y escuchando

    def connect(self, address):
        if self.type == SOCK_STREAM:
          self.gsm.write('AT+USOCO=0,'+address[0]+','+address[1]+'\r\n')
          self._wait_for_str("OK")
          self.gsm.write('AT+USODL=0\r\n')
        else:  # self.type == SOCK_DGRAM:
        
            self.gsm.write('AT+USOCO=1,'+address[0]+','+address[1]+'\r\n')
        print("con")
        self._wait_for_str("CONNECT")
        
        self.uart2IRQ = self.gsm.irq(trigger=pyb.UART.IRQ_RXIDLE,
                                     handler=self.irq_fun,
                                     hard=False)

    def send(self, bytes):
        # len=len(bytes)
        # self.gsm.write('AT+CIPSEND='+len+'\r\n')
        # sleep(1)
        sent = self.gsm.write(bytes)
        return sent

    def recv(self, bufsize):
        res = self.read(bufsize)
        return res

    def sendto(self, bytes, address):
        if self.type == SOCK_STREAM:
            self.gsm.write('AT+USOCO=0,'+address[0]+','+address[1]+'\r\n')
            self._wait_for_str("OK")
            self.gsm.write('AT+USODL=0\r\n')
        else:  # self.type == SOCK_DGRAM:
            self.gsm.write('AT+USOCO=1,'+address[0]+','+address[1]+'\r\n')
        print("sto")
        self._wait_for_str("CONNECT")
        self.uart2IRQ = self.gsm.irq(trigger=pyb.UART.IRQ_RXIDLE,
                                     handler=self.irq_fun,
                                     hard=False)
        # len=len(bytes)
        # self.gsm.write('AT+CIPSEND='+len+'\r\n')
        # sleep(1)
        self.gsm.write(bytes)

    def read(self, size=None):
        if size is None:
            if len(self.rx_bufb) > 0:
                res = self.rx_bufb
                self.rxbufb = bytearray()
                print("read:", res)
                return res
            else:
                print("read: None")
                return None
        else:
            count = self.timeout
            while len(self.rx_bufb) < size and count > 0:
                print("expected:", size, "current", len(self.rx_bufb), "any", self.gsm.any())
                sleep(0.1)
                count = count - 1
            if len(self.rx_bufb) >= size:
                res = self.rx_bufb[:size]
                self.rx_bufb = self.rx_bufb[size:]
                print("read:", res, "remain", len(self.rx_bufb))
                return res
            else:
                return None

    def write(self, buf, size=None):
        if size is None:
            length = len(buf)
            self.gsm.write(buf)
            # print("write:",buf)
        else:
            length = size
            self.gsm.write(buf[:size])
            # print("write:",buf[:size])
        return length

    def readinto(self, buf, nbytes=None):
        if nbytes is None:
            nbytes = len(buf)
        count = self.timeout
        while len(self.rx_bufb) < nbytes and count > 0:
            if self.gsm.any() > 0:
                self.irq_fun(self.gsm)
            # print("needed:",nbytes,"current", len(self.rx_bufb), "any", self.gsm.any())
            sleep(1)
            count = count - 1
        if len(self.rx_bufb) < nbytes:
            print("expected", nbytes, "rec", len(self.rx_bufb))
            nbytes = len(self.rx_bufb)

        if nbytes > 0:
            buf[:] = self.rx_bufb[:nbytes]
            self.rx_bufb = self.rx_bufb[nbytes:]
        else:
            buf = None

        # print("r_i:",buf)

        return nbytes

    def setblocking(self, flag):
        if flag is True:
            print("modo bloqueante")
        else:
            print("modo no bloqueante")

    def settimeout(self, value):
        self.timeout = value






















