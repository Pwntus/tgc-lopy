from time import sleep
from machine import Pin



class SHT10:
    Commands = {'Temperature': 0b00000011,
                'Humidity': 0b00000101,
                'ReadStatusRegister': 0b00000111,
                'WriteStatusRegister': 0b00000110,
                'SoftReset': 0b00011110,
                'NoOp': 0b00000000}

#    RESOLUTION = {'High': [14, 12], 'Low': [12, 8]}
#    VDD = {'5V': 5, '4V': 4, '3.5V': 3.5, '3V': 3, '2.5V': 2.5}

    def __init__(self, data_pin, sck_pin):
        self.data_pin = Pin(data_pin, mode = Pin.IN, pull = Pin.PULL_UP)
        #self.data_pin = data_pin
        self.sck_pin = Pin(sck_pin, mode = Pin.IN, pull = Pin.PULL_UP)
        #self.sck_pin = sck_pin


        self.tempCmd = 0b00000011
        self.humCmd = 0b00000101

        self.sleepTime = 0.010


    def readTemp(self):
        D1 = -39.7   #-40.0
        D2 = 0.01    # FINN UT!

        raw_temp = self.readTempRaw()
        if raw_temp is None:
            return(None)
        temp = (raw_temp * D2) + D1
        return(temp)

    def readHum(self):
        ret = True
        C1 = -2.0468        #-4.0
        C2 = 0.0367         #0.0405
        C3 = -0.0000015955  #-0.0000028
        T1 = 0.01           #0.01
        T2 = 0.00008        #0.00008


        if self.sendCommandSHT(self.humCmd) == False:
            ret = False
        if self.waitForResultSHT() == False:
            ret = False
        val = self.getData16SHT()
        self.skipCrcSHT()

        linearHum = C1 + (C2 * val) + (C3 * val * val)

        temp = self.readTemp()
        if temp is None:
            return(None)
        correctedHum = (temp - 25.0) * (T1 + T2 * val) + linearHum

        if ret == False:
            return(None)
        return(correctedHum)

    def readTempRaw(self):
        ret = True
        if self.sendCommandSHT(self.tempCmd) == False:
            ret = False
        if self.waitForResultSHT() == False:
            ret = False
        val = self.getData16SHT()
        self.skipCrcSHT()

        if ret == False:
            return(None)

        return(val)

    def shiftIn(self, numBits):
        ret = 0

        for x in range(numBits):
            self.sck_pin(1)
            sleep(self.sleepTime)
            ret = ret * 2 + self.data_pin()
            self.sck_pin(0)

        return(ret)

    def shiftOut(self, msg, numBits):
        ret = True
        self.data_pin.mode(Pin.OUT)

        writeMask = 0b10000000

        for x in range(numBits):
            if (msg & writeMask) != 0:
                self.data_pin(1)
            else:
                self.data_pin(0)
            sleep(self.sleepTime)
            self.sck_pin(1)
            sleep(self.sleepTime)
            self.sck_pin(0)
            writeMask = writeMask >> 1

        self.data_pin.mode(Pin.IN)
        self.data_pin.pull(Pin.PULL_UP)
        sleep(self.sleepTime)
        self.sck_pin(1)
        sleep(self.sleepTime)
        if self.data_pin() == 1:
            print("ERROR! shitOut")
            ret = False
        self.sck_pin(0)
        return(ret)


    def sendCommandSHT(self, cmd):
        ret = True
        #PINMODE! OUTPUT
        self.data_pin.mode(Pin.OUT)
        self.sck_pin.mode(Pin.OUT)

        self.data_pin(1)
        self.sck_pin(1)
        self.data_pin(0)
        self.sck_pin(0)
        self.sck_pin(1)
        self.data_pin(1)
        self.sck_pin(0)

        if self.shiftOut(cmd, 8) == False:
            ret = False

        self.sck_pin(1)
        #PINMODE DATA INPUT
        self.data_pin.mode(Pin.IN)
        self.data_pin.pull(Pin.PULL_UP)
        ack = self.data_pin()
        if ack == 0:
            print("ERROR! sendCommandSHT")
            ret = False
        return(ret)

    def waitForResultSHT(self):
        ret = True
        #PINMODE DATA INPUT
        self.data_pin.mode(Pin.IN)
        self.data_pin.pull(Pin.PULL_UP)
        for x in range(100):
            sleep(self.sleepTime)
            ack = self.data_pin()
            if ack == 0:
                break
        if ack == 1:
            print("ERROR! waitForResultSHT")
            ret = False
        return(ret)

    def getData16SHT(self):
        #PINMODE DATA IN CLOCK OUTPUT
        self.data_pin.mode(Pin.IN)
        self.data_pin.pull(Pin.PULL_UP)
        self.sck_pin.mode(Pin.OUT)
        val = self.shiftIn(8)
        val *= 256

        #PINMODE DATA OUTPUT
        self.data_pin.mode(Pin.OUT)
        self.data_pin(1)
        self.data_pin(0)
        self.sck_pin(1)
        self.sck_pin(0)

        #PINMODE DATA IN
        self.data_pin.mode(Pin.IN)
        self.data_pin.pull(Pin.PULL_UP)
        val |= self.shiftIn(8)

        return(val)

    def skipCrcSHT(self):
        #PINMODE OUTPUT
        self.data_pin.mode(Pin.OUT)
        self.sck_pin.mode(Pin.OUT)

        self.data_pin(1)
        self.sck_pin(1)
        self.sck_pin(0)
