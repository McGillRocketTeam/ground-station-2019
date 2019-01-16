import serial, os, pty
from model import datastorage
import model.datastorage as DataStorage
import views.plots as Plots
from random import randint
import random
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
        readData = ''
        loopControl = False
        while loopControl:
            # telemetry_data = ser.read(1000)
            simData = True #Controls if data is simulated or from actual serial reader
            if simData:
                readData += self.serialSim()
                pass
            else:
                #read serial input
                pass
            telemetry_data = [str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100))]

            result = self.parse(readData)
            if result[0] == 200 or result[0] == 300:
                #TODO: update data storage and telemetry data to account for full telemetry data
                print(len(result[1]))
                for dataChunk in result[1]:
                    datastorage.save_telemetry_data(dataChunk)
                    plots.plotTelemetryData(dataChunk)

                    pass
                # Save data to file
                datastorage.save_telemetry_data(telemetry_data)
                # Save gps data as well!
                # Display data (asynchronously)
                plots.plotTelemetryData(telemetry_data)

                #update readData so it only contains unparsed text
                readData = result[2]
            else:
                # TODO: log errors
                pass

    def parse(self, data):
        """
        :param data: the string of text that should be parsed
        :return: a tuple containing (status, listOfParsedData, remainingString)
        status: status code: 200 means parse was successful
        listOfParsedData: a list containing lists of length 8 (the telemetry data)
        remainingString: the data that was not able to be parsed at the end of the data string
        """
        status = 500  # error codes or correlation id
        """
        Error Codes: 
        500 error occured
        200 data was successfully parsed, remainingString is non-empty
        300 data was successfully parsed, remaining string is empty
        400 no data was parsed from the string
        """
        parseHelpedData = self.parseHelper(data)

        if parseHelpedData[0] == -1:
            dataList = []
            status = 400
        else:
            dataList = [parseHelpedData[0][0:8]]

        while len(re.split(r',',parseHelpedData[1])) > 9:
            parseHelpedData = self.parseHelper(parseHelpedData[1])
            dataList.append(parseHelpedData[0][0:8])
            pass
        if len(dataList) > 0:  # TODO: implement parsing logic here
            if len(parseHelpedData) == 1:
                return (300,dataList,'')
            else:
                return (200,dataList, parseHelpedData[1])
        return (status,)

    # def parseHelperFull(self, data):
    #     return self.parseHelper((data,8))

    def parseHelper(self, data):
        '''this function takes in a string of any length, and returns a tuple,
        where slot 0 is the current array of seperated values from one telemetry reading
        if slot 0 contains the int -1, then there was no data to be parsed
        slot 1 is the remaining string
        '''
        #Takes the first set of data from the data string, or removes the garbage from the front of it
        print("Parse helper")
        print(data)
        splitData = re.split(r"S",data,1)
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
        while len(parsed) != 9 :
            print(parsed)
            splitData = re.split(r"S",remainingData,1)
            parsed = re.split(r",",splitData[0])
            if len(splitData) == 1:
                remainingData = ''
            else:
                remainingData = splitData[1]
            #TODO: fix: infinite loop when string ends with partial data piece

            # if len(re.split(r',',remainingData)) < 12:
            #     break
            # print(parsed)
            # print(remainingData)
            pass
        return (parsed,remainingData)

    def gpsParseHelper(self, data):
        pass

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

        # To read data written to slave serial
        return os.read(master, 1000).decode('utf-8')

    def gpsSim(self):
        #setup serial sim
        master, slave = pty.openpty()
        s_name = os.ttyname(slave)
        ser = serial.Serial(s_name)

        ser.write(bytes('S', 'utf-8'))

        randomGpsData = self.genRandomGpsData()

        for i in range(0,3):
            ser.write(bytes(str(randomGpsData[i]), 'utf-8'))
            if i == 2:
                ser.write(bytes(',E', 'utf-8'))
            else:
                ser.write(bytes(',', 'utf-8'))

        return os.read(master, 1000).decode('utf-8')



    def getSerialData(self):
        return self.serialSim()
        #TODO: implement actual fetching of serial data

    def genRandomDataArray(self):
        minLat = -90
        maxLat = 90
        minRand = 0
        maxRand = 9000000
        lat = randint(minLat, maxLat)
        long = randint(2*minLat, 2*maxLat)
        alt = randint(minRand, maxRand)
        time = randint(minRand, maxRand)
        temp = randint(-273, maxRand)
        vel = randint(minRand, maxRand)
        acc = randint(minRand, maxRand)
        sat = randint(minRand, maxRand)
        intList = [lat,long,alt,time,temp,vel,acc,sat]
        floatList = [(i + random.random()) for i in intList]
        return floatList

    def genRandomGpsData(self):
        lat = randint(-90,90) + random.random()
        long = randint(-180,180) + random.random()
        sat = randint(0,200)
        return [lat,long,sat]


    def testMethod(self):
        # test = 'jadjbeSSS19EE3E38,3S$23'
        # test += self.serialSim()
        # test += self.serialSim()
        # # test += 'abeESSSjdj'
        # test += self.serialSim()
        # # test += 'abeqSSEE1.232,242.2,44.3'
        # test += self.serialSim()
        # test = test[0:len(test)-15]
        # test += 'E'
        # # test += 'abcbsdlehEES,See'
        # print("testData:" + test)
        # testparsed = self.parse(test)
        # print(testparsed)
        # print(self.parse(testparsed[2]))
        # '''+ self.serialSim()'''
        test = self.serialSim()
        self.parseHelper(test)

        t1 = self.gpsSim()
        print(t1)



def main():
    datastorage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(datastorage, plots)


if __name__ == "__main__":
    main()
