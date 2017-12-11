from startiot import Startiot
from pytrack import Pytrack
from L76GNSS import L76GNSS
from SHT10 import SHT10
import pycom
import time

data_pin = 'P10'
sck_pin = 'P9'

pycom.heartbeat(False)
pycom.rgbled(0x000000)
time.sleep(0.2)
pycom.rgbled(0xFF0000)
time.sleep(0.2)
pycom.rgbled(0x000000)
time.sleep(0.2)
pycom.rgbled(0xFF0000)
time.sleep(0.2)
pycom.rgbled(0x000000)
time.sleep(0.2)
pycom.rgbled(0xFF0000)
time.sleep(0.2)
pycom.rgbled(0x000000)

pt = Pytrack()

sht = SHT10(data_pin, sck_pin)
tmp = sht.readTemp()
hum = sht.readHum()

if (tmp is None or hum is None):
    print("no data")
    pt.setup_sleep(10) # 3600
else:
    print("data")
    pycom.rgbled(0x00FF00)
    time.sleep(2)

    gps = L76GNSS(pytrack=pt, timeout=30)
    iot = Startiot()

    if iot.connect():
        lat, lng = gps.coordinates()
        bat = pt.read_battery_voltage()

        #if lat is not None and lng is not None:

        print("sending to mic")

        pycom.rgbled(0x00FF00)
        time.sleep(1)
        pycom.rgbled(0x0000FF)
        time.sleep(1)
        pycom.rgbled(0x00FF00)
        time.sleep(1)
        pycom.rgbled(0x0000FF)
        time.sleep(1)

        iot.send("{},{},{},{},{}".format(lat, lng, tmp, hum, bat))

    pt.setup_sleep(10) # 1200

pt.go_to_sleep()