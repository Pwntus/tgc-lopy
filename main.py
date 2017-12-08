#from startiot import Startiot
from sht10 import SHT10

import pycom
import machine
from time import sleep

from pytrack import Pytrack
from startiot import Startiot
from L76GNSS import L76GNSS

data_pin = 'P10'
sck_pin = 'P9'

pycom.heartbeat(False) # disable the blue blinking
pycom.rgbled(0x000000)
pt = Pytrack()

sht = SHT10(data_pin, sck_pin)
tmp = sht.readTemp()
hum = sht.readHum()

if (tmp is None or hum is None):
    print("no data")
    pt.setup_sleep(3600)
else:
    print("data")
    gps = L76GNSS(pytrack=pt, timeout=30)
    iot = Startiot()

    if iot.connect(timeout=15):
        lat, lng = gps.coordinates()
        bat = pt.read_battery_voltage()

    #    if lat is not None and lng is not None:
    #        print("sending to mic")
        print("sending to mic")
        iot.send("{},{},{},{},{}".format(lat, lng, tmp, hum, bat))

    pt.setup_sleep(1200)

pt.go_to_sleep()
