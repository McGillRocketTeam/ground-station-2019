import model.datastorage as DataStorage
import views.plots as Plots
from random import randint
import random
import re
import datetime
import time
import math

"""
data format: Slat,long,alt,time,temp,vel,acc,sat,E
backup data: lat, long, alt, sat#
"""

# Values for ground station coordinates
groundlat = 0
groundlong = 0
groundalt = 0
countergps = 0


class Parser:
    start_time = 0

    def __init__(self, datastorage, plots):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())

        """self.port = "COM5"
        # ls /dev/tty.*
        #use above to find port of arduino on mac
        self.port = "/dev/tty.usbserial-A104IBE7"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 3  # sec
        ser = serial.Serial(self.port, self.baud, self.byte, self.parity, self.stopbits)
        self.ser = ser
        if not ser.isOpen():
            ser.open()
        else:
            pass"""
        readData = ''

        counterAntenna = 0
        loopControl = True
        while loopControl:
            # time.sleep(0.8)
            # telemetry_data = ser.read(1000)
            simData = True #Controls if data is simulated or from actual serial reader
            if simData:
                #print(self.ser.read())
                #readData += self.ser.read().decode('utf-8')
                #print(readData)
                readData = self.serialSim()
                print(readData)
            else:
                #read serial input
                pass
            #TODO: save the full telemetry string here
            datastorage.save_raw_data(readData)
            #telemetry_data = [str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100))]

            result = self.parseFull((readData,8))
            if result[0] == 200 or result[0] == 300:
                #TODO: update data storage and telemetry data to account for full telemetry data
                # print(len(result[1]))
                for dataChunk in result[1]:
                    print(dataChunk)
                    gpsDataChunk = []
                    gpsDataChunk.append(dataChunk[0])
                    gpsDataChunk.append(dataChunk[1])
                    gpsDataChunk.append(dataChunk[7])
                    datastorage.save_telemetry_data(dataChunk)
                    datastorage.save_gps_data(gpsDataChunk)
                    plots.plot_telemetry_data(dataChunk)
                    plots.plot_gps_data(dataChunk)
                    plots.update_plots()

                    counterAntenna +=1
                    if counterAntenna%2 == 0: # Is 1000 the best number for this?
                        antennaAngle = self.findAngle(dataChunk)
                        plots.antennaAngle.configure(text='ANTENNA ANGLE: ' + str(antennaAngle[0]) + ' (xy), ' + str(antennaAngle[1]) + ' (z)')


                    pass
                # Save data to file
                #datastorage.save_telemetry_data(telemetry_data)
                # Save gps data as well!
                # Display data (asynchronously)
                #plots.plotTelemetryData(telemetry_data)

                #update readData so it only contains unparsed text
                readData = result[2]
            else:
                # TODO: log errors
                pass

    def findAngle(self, data):
        '''calculate antenna direction given rocket coordinates and ground station coordinates'''
        angle = [] # Ordered as angle from east, then angle from ground
        # coordinates of ground station and rocket
        ground_x = groundlat
        ground_y = groundlong
        rocket_x = float(data[0])
        rocket_y = float(data[1])
        rocket_alt = float(data[2])
        # Covert to decimal degrees
        '''rocket_x = self.DMStoDD(rocket_x)
        rocket_y = self.DMStoDD(rocket_y)
        rocket_alt = self.DMStoDD(rocket_alt)
        '''
        # Convert DecDegs to radians
        ground_x = (math.pi/180)*ground_x
        ground_y = (math.pi/180)*ground_y
        rocket_x = (math.pi/180)*rocket_x
        rocket_y = (math.pi/180)*rocket_y
        # Compute theta
        theta = 0.0
        t = (180/math.pi)*math.atan((rocket_y - ground_y)/(rocket_x-ground_x))
        if rocket_x < ground_x and rocket_y > ground_y: # Rocket is NW from ground station
            theta = 180+t
        elif rocket_x < ground_x and rocket_y < ground_y: # Rocket is SW from ground station
            theta = 180+t
        elif rocket_x > ground_x and rocket_y < ground_y: # Rocket is SE from ground station
            theta = 360+t
        elif rocket_x > ground_x and rocket_y > ground_y: # Rocket is NE from ground station
            theta = t

        angle.append(theta)

        # Compute phi
        # Distance between origin and P, projection of rocket onto xy-plane
        d = 2*6371000*math.asin(math.sqrt(math.pow((math.sin((rocket_y-ground_y)/2)), 2) + math.cos(ground_x)*math.cos(rocket_x)*math.pow(math.sin((rocket_x-ground_x)/2), 2)))
        phi = (180/3.14)*math.atan((rocket_alt - groundalt)/d)
        #TODO: format phi and theta better, how many decimal places?
        angle.append(phi)

        return angle

    def DMStoDD(self, degMin):
        '''converts degree minutes seconds into decimal degrees'''
        min = 0.0
        decDeg = 0.0
        min = math.fmod(degMin, 100.0)
        degMin = (degMin / 100)
        decDeg = degMin + (min / 60)
        return decDeg

    def parseFull(self, data):
        """
        :param data: the string of text that should be parsed in a tuple with length of datastring
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
        dataString = data[0]
        dataLength = data[1]
        parseHelpedData = self.parseHelper((dataString,dataLength))

        if parseHelpedData[0] == -1:
            dataList = []
            status = 400
        else:
            dataList = [parseHelpedData[0][0:8]]

        while len(re.split(r',',parseHelpedData[1])) > (dataLength+1):
            parseHelpedData = self.parseHelper((parseHelpedData[1],dataLength))
            if parseHelpedData[0] == -1:
                break
            dataList.append(parseHelpedData[0][0:dataLength])
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
        #split the data tuple into the actual data, and the length of the data string
        actualData = data[0]
        stringLength = data[1]
        #Takes the first set of data from the data string, or removes the garbage from the front of it
        splitData = re.split(r"S",actualData,1)
        remainingData = ''
        if len(splitData) == 2:
            remainingData = splitData[1]
        else:
            splitTry = re.split(r",",splitData[0])
            if len(splitTry) == (stringLength+1):
                return (splitTry,"")
            else:
                return (-1,splitData[0])
        parsed = re.split(r",",splitData[0])
        while len(parsed) != (stringLength+1) :
            splitData = re.split(r"S",remainingData,1)
            parsed = re.split(r",",splitData[0])
            if len(splitData) == 1:
                remainingData = ''
                #return (-1,remainingData)
                # return ([],actualData)
            else:
                remainingData = splitData[1]
            #TODO: fix: infinite loop when string ends with partial data piece

            # if len(re.split(r',',remainingData)) < 12:
            #     break
            # print(parsed)
            # print(remainingData)
        return (parsed,remainingData)

    # def parseGps(self, data):
    #     #TODO: fix parsing if there are more than 2 data strings
    #     """
    #             :param data: the string of text that should be parsed
    #             :return: a tuple containing (status, listOfParsedData, remainingString)
    #             status: status code: 200 means parse was successful
    #             listOfParsedData: a list containing lists of length 8 (the telemetry data)
    #             remainingString: the data that was not able to be parsed at the end of the data string
    #             """
    #     gpsStatus = 50  # error codes or correlation id
    #     """
    #     Error Codes:
    #     50 error occured
    #     20 data was successfully parsed, remainingString is non-empty
    #     30 data was successfully parsed, remaining string is empty
    #     40 no data was parsed from the string
    #     """
    #     parseHelpedData = self.parseHelperGps(data)
    #
    #     if parseHelpedData[0] == -1:
    #         dataList = []
    #         gpsStatus = 40
    #     else:
    #         dataList = [parseHelpedData[0][0:3]]
    #
    #     while len(re.split(r',', parseHelpedData[1])) > 4:
    #         parseHelpedData = self.parseHelperGps(parseHelpedData[1])
    #         dataList.append(parseHelpedData[0][0:3])
    #         print(dataList)
    #         pass
    #     if len(dataList) > 0:  # TODO: implement parsing logic here
    #         if len(parseHelpedData) == 1:
    #             return (30, dataList, '')
    #         else:
    #             return (20, dataList, parseHelpedData[1])
    #     return (gpsStatus,)
    #     pass

    # def parseHelperGps(self, data):
    #     return self.parseHelper((data,3))


    def serialSim(self):
        # #setup serial simulator
        # master, slave = pty.openpty()
        # s_name = os.ttyname(slave)
        # ser = serial.Serial(s_name)
        #
        # # Write to the device the marker of the start of the data
        # ser.write(bytes('S','utf-8'))

        # Gets randomly generated data
        randData = self.genRandomDataArray()

        # # Writes random data seperated by commas, ending with a pound sign
        # for i in range(0,8):
        #     ser.write(bytes(str(randData[i]), 'utf-8'))
        #     if i == 7:
        #         ser.write(bytes(',E', 'utf-8'))
        #     else:
        #         ser.write(bytes(',', 'utf-8'))
        #
        # # To read data written to slave serial
        # return os.read(master, 1000).decode('utf-8')
        global start_time
        return 'S' + str(randData[0]) + ',' + str(randData[1]) + ',' + str(randData[2]) + ',' + str(randData[3]) + ',' + str(randData[4]) + ',' + str(randData[5]) + ',' + str(randData[6]) + ',' + str(randData[7]) + ',E'


    def getSerialData(self):
        return self.serialSim()
        #TODO: implement actual fetching of serial data

    def genRandomDataArray(self):
        minLat = 32
        maxLat = 33
        minLong = -107
        maxLong = -106
        minRand = 0
        maxRand = 100
        global countergps
        countergps += 0.1
        lat = 32 + (countergps ** 2) * 0.001
        long = -107 + (countergps ** 2) ** 0.002

        alt = randint(minRand, maxRand) + random.random()
        time = randint(minRand, maxRand)
        temp = randint(0, maxRand) + random.random()
        vel = randint(minRand, maxRand) + random.random()
        acc = randint(minRand, maxRand) + random.random()
        sat = randint(minRand, maxRand) + random.random()
        global start_time
        time = round(datetime.datetime.utcnow().timestamp()) - start_time
        intList = [lat,long,alt,time,temp,vel,acc,sat]
        #intList = [time,temp,alt,vel,acc,lat,long,sat]
        #floatList = [(i + random.random()) for i in intList]
        return intList
        # return intList

    def genRandomGpsData(self):
        global countergps
        countergps += 0.1
        lat = 32 + (countergps ** 2) * 0.001
        long = -107 + (countergps ** 2) ** 0.002
        alt = randint(0,50000) + random.random()
        sat = randint(0,200)
        return [lat,long,alt,sat]


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
        test += self.serialSim()
        for x in range(10):
            test += self.serialSim()
            # test =  test[:-randint(1,33)]
        tr = self.parseFull((test,8))
        print(tr)

        t2 = self.parseFull((tr[2],8))
        print(t2)


        print("Gps sim")
        t1 = self.gpsSim()
        print(t1)
        for x in range(20):
            t1 += self.gpsSim()
            t1 = t1[:-randint(1,15)] #removes a random amount from the end of the string
        t1 += self.gpsSim()
        t1 += self.gpsSim()
        t1 += self.gpsSim()
        print(t1)
        # tp = self.parseHelperGps(t1)
        # print(tp)

        tf = self.parseFull((t1,4))
        print(tf)




def main():
    datastorage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(datastorage, plots)


if __name__ == "__main__":
    main()
