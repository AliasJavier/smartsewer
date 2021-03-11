import nic_Ublox
import pyb
from umqttsimple_ublox import MQTTClient
from machine import Pin
from time import sleep
from ota_updater import OTAUpdater

led = Pin('X18', Pin.OUT)
led.value(1)
sleep(0.1)
led.value(0)
sleep(0.1)
led.value(1)
sleep(1)


CHARGEPIN = 'X19' #PC0
MEASUREPIN = 'X20' #PC1
DISCHARGEPIN = 'X21' #PC2

adc = pyb.ADC(MEASUREPIN)              # create an analog object from a pin
val = adc.read()                # read an analog value

# create an output pin on pin #0
cpin = Pin(CHARGEPIN, Pin.OUT)
dpin = Pin(DISCHARGEPIN, Pin.OUT)

dpin.value(0)
cpin.value(0)

# set the value low then high
sleep(1)

nic=nic_Ublox.driver()
#nic.power_up()
nic.connect(service_id=1, pin='1111', apn='orangeworld')

ota_updater = OTAUpdater('https://github.com/AliasJavier/ble_code')
ota_updater.check_for_update_to_install_during_next_reboot()
ota_updater.download_and_install_update_if_available()

host='smart_sw_1'
client = MQTTClient(host, 'safeworker-iot-hub.azure-devices.net',keepalive=60,ssl=True, port=8883,
                     user='safeworker-iot-hub.azure-devices.net/smart_sw_1/?api-version=2018-06-30',
                     password='SharedAccessSignature sr=safeworker-iot-hub.azure-devices.net%2Fdevices%2Fsmart_sw_1&sig=mI6Big1hv3ZICp0lYt4Qe%2FYFNIY9QuzGLtura6fr2no%3D&se=2695370191')
#client = MQTTClient('pqrst', 'test.mosquitto.org',keepalive=60,ssl=True, port=8883)
#client = MQTTClient('pqrst', 'mqtt.flespi.io',keepalive=60,ssl=True, port=8883,
               #      user='kdBFvuSVHMw8bA2yWTftfXgXnH3OH2FR44mpp38UFuTGSL3Es6WxT2k7zcL44eLW',
                #     password='')
client.connect()

for i in range(100):
  cpin.value(1)
  buf = bytearray(100)                # create a buffer of 100 bytes
  adc.read_timed(buf, 10000)             # read analog values into buf at 10Hz
                                      #   this will take 10 seconds to finish
  print(buf)

  count=0
  for i in buf:
    count=count+1
    if i > 0xfe:
      break
  client.publish('devices/smart_sw_1/messages/events/', '{"device_id": "'+host+'",\n"smartsewer": '+
                  str(count)+'}')
  print('{"device_id": "'+host+'",\nsmartsewer": '+
                  str(count)+'}')
  sleep(2)
  #for i in range(100):
  #  val = adc.read()                # read an analog value
  #  print(val)
  cpin.value(0)
  sleep(1)






