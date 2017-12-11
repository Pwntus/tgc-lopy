from startiot import Startiot
from pytrack import Pytrack
from L76GNSS import L76GNSS
from SHT10 import SHT10
from time import sleep
import pycom

data_pin = 'P10'
sck_pin = 'P9'

pycom.heartbeat(False)
pycom.rgbled(0x000000)

pt = Pytrack()

sht = SHT10(data_pin, sck_pin)
tmp = sht.readTemp()
hum = sht.readHum()

if (tmp is None or hum is None):
    pt.setup_sleep(3600) # 3600
else:
    gps = L76GNSS(pytrack=pt, timeout=30)
    iot = Startiot()

    if iot.connect(blocking=True, timeout=15):
        lat, lng = gps.coordinates()
        bat = pt.read_battery_voltage()

        # if lat is not None and lng is not None:

        pycom.rgbled(0xFF0000)
        iot.send("{},{},{},{},{}".format(lat, lng, tmp, hum, bat))
        sleep(5) # MUST use sleep. Else socket send won't work b4 a deep-sleep.

    pt.setup_sleep(10) # 1200

pt.go_to_sleep()