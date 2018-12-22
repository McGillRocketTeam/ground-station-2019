import serial, os, pty
from model import datastorage
import model.datastorage as DataStorage
import views.plots as Plots
from random import randint
import re

"""
data format: $ lat long alt time temp vel acc sat
"""
class Parser:
    def __init__(self, datastorage, plots):
        """
        self.port = "COM2"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 1  # sec
        ser = serial.Serial(self.port, self.baud, self.byte, self.parity, self.stopbits)
        self.ser = ser
        if not ser.isOpen():
            ser.open()
        else:
        """
        # print('com5 is open', ser.isOpen())
        self.testMethod()
        #TODO: account for errors in the data being sent and read

        loopControl = True
        while loopControl:
            # telemetry_data = ser.read(1000)
            telemetry_data = [str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100))]
            randomData = self.serialSim()
            result = self.parse(randomData)
            if result == 200:
                # Save data to file
                datastorage.save_telemetry_data(telemetry_data)
                # Save gps data as well!
                # Display data (asynchronously)
                plots.plotTelemetryData(telemetry_data)
            else:
                # TODO: log errors
                pass

    def parse(self, data):
        status = 500  # error codes or correlation id

        print(len(data))
        if len(data) == 5:  # TODO: implement parsing logic here
            return (200,)
        return (status,)

    def parseHelper(self, data):
        #this function takes in a string of any length, and returns a tuple,
        #where slot 0 is the current array of seperated values from one telemetry reading
        #if slot 0 contains the int -1, then there was no data to be parsed
        #slot 1 is the remaining string
        splitData = re.split(r"S",data,1)
        # print(splitData)
        remainingData = ''
        if len(splitData) == 2:
            remainingData = splitData[1]
        else:
            splitTry = re.split(r",",splitData[0])
            if len(splitTry) == 9:
                return (splitTry,"")
            else:
                return (-1,splitData[0])
        parsed = re.split(r",",splitData[0])
        # print(parsed)
        while len(parsed) != 9:
            splitData = re.split(r"S",remainingData,1)
            parsed = re.split(r",",splitData[0])
            remainingData = splitData[1]
            # print(parsed)
            # print(remainingData)
            pass
        return (parsed,remainingData)

    def serialSim(self):
        #setup serial simulator
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        ser = serial.Serial(s_name)

        # Write to the device the marker of the start of the data
        ser.write(bytes('S','utf-8'))

        # Gets randomly generated data
        randData = self.genRandomDataArray()

        # Writes random data seperated by commas, ending with a pound sign
        for i in range(0,8):
            ser.write(bytes(str(randData[i]), 'utf-8'))
            if i == 7:
                ser.write(bytes(',E', 'utf-8'))
            else:
                ser.write(bytes(',', 'utf-8'))
            i += 1

        # To read data written to slave serial
        return os.read(master, 1000).decode('utf-8')

    def getSerialData(self):
        return self.serialSim()
        #TODO: implement actual fetching of serial data

    def genRandomDataArray(self):
        minLat = 0
        maxLat = 100
        minRand = 0
        maxRand = 9000000
        lat = randint(minLat, maxLat)
        long = randint(minLat, maxLat)
        alt = randint(minRand, maxRand)
        time = randint(minRand, maxRand)
        temp = randint(-273, maxRand)
        vel = randint(minRand, maxRand)
        acc = randint(minRand, maxRand)
        sat = randint(minRand, maxRand)
        return [lat,long,alt,time,temp,vel,acc,sat]

    def testMethod(self):
        test = 'jadjbeSSS19EE3E38,3S$23'
        test += self.serialSim()
        test += self.serialSim()
        # test += 'abeESSSjdj'
        test += self.serialSim()
        test += self.serialSim()
        print("testData:" + test)
        dataRecieved = self.parseHelper(test)
        data2 = self.parseHelper(dataRecieved[1])
        while dataRecieved[1] != '':
            dataRecieved = self.parseHelper(dataRecieved[1])
            print(dataRecieved)


def main():
    datastorage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(datastorage, plots)


if __name__ == "__main__":
    main()
