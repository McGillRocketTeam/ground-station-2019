import time

import model.datastorage as DataStorage
import views.plots as Plots
import serial
from random import randint
import random
import re
import datetime
import math

"""
data format: Slat,long,alt,time,temp,vel,acc,sat,E
backup GPS data: lat, long, alt, sat#
"""
telemetry_data_length = 8  # Current length of telemetry data string
gps_data_length = 5 #Current length of gps data string
counter_gps = 0  # Counter to generate decent GPS data for test only
ground_lat = 0  # Ground station latitude
ground_long = 0  # Ground station longitude
ground_alt = 0  # Ground station altitude


class Parser:
    start_time = 0

    def __init__(self, data_storage, plots):
        self.data_storage = data_storage
        self.plots = plots

        # TODO Add port setup for GPS
        # TODO Automated port check setup

        # self.port = "COM5"
        # ls /dev/tty.*
        #use above to find port of arduino on mac
        # self.port = "/dev/tty.usbserial-A104IBE7"
        # self.port = "/dev/tty.usbmodem14201"
        self.port = "/dev/tty.usbmodem14101"

        self.port2 = "/dev/tty.usbmodem14101"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 3  # sec
        #Serial setup for
        # ser = serial.Serial(self.port, self.baud, self.byte, self.parity, self.stopbits)
        # self.serial_telemetry = ser
        # if not ser.isOpen():
        #     ser.open()
        # else:
        #     pass

        # ser2 = serial.Serial(self.port2, self.baud, self.byte, self.parity, self.stopbits)
        # self.serial_gps = ser2
        # if not ser2.isOpen() :
        #     ser2.open()
        # else:
        #     pass

    def parse(self):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())

        telemetry_data = ''
        gps_data = ''
        counter_antenna = 0
        loop_control = True

        while loop_control:
            # time.sleep(0.5)
            real_data = False  # Controls if data is simulated or from actual serial reader
            if real_data:
                telemetry_data += self.serial_telemetry.read().decode('utf-8')
                # gps_data += self.serial_gps.read().decode('utf-8')
                print(telemetry_data)
                print(gps_data)
            else:
                telemetry_data += self.simulate_serial()
                gps_data += self.sim_gps()
                print(telemetry_data)
                print(gps_data)

            """ Save raw data to files """
            self.data_storage.save_raw_data(telemetry_data)
            # self.data_storage.save_raw_data(gps_data)

            # processing for full telemetry data
            result = self.parseFull((telemetry_data, telemetry_data_length))
            print(result)
            return_data = self.processParsed((result, (200, 300), counter_antenna, telemetry_data, True, True))
            telemetry_data = return_data[0]
            counter_antenna = return_data[1]

            # processing for gps:
            # gps_result = self.parseFull((gps_data, gps_data_length))
            # print('gps::')
            # print(gps_result)
            # return_gps_data = self.processParsed((gps_result,(200,300),counter_antenna,gps_data,False, False))
            # gps_data = return_gps_data[0]


    def find_angle(self, data):
        '''calculate antenna direction given rocket coordinates and ground station coordinates'''
        angle = [] # Ordered as angle from east, then angle from ground
        # coordinates of ground station and rocket
        ground_x = ground_lat
        ground_y = ground_long
        rocket_x = float(data[0])
        rocket_y = float(data[1])
        rocket_alt = float(data[2])
        # Covert to decimal degrees
        '''rocket_x = self.convert_DMS_to_DD(rocket_x)
        rocket_y = self.convert_DMS_to_DD(rocket_y)
        rocket_alt = self.convert_DMS_to_DD(rocket_alt)
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
        phi = (180/math.pi)*math.atan((rocket_alt - ground_alt)/d)
        # TODO: format phi and theta better, how many decimal places?
        angle.append(phi)

        return angle

    def convert_DMS_to_DD(self, degMin):
        """ Converts degree minutes seconds into decimal degrees """
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
            dataList = [parseHelpedData[0][0:dataLength]]

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
                # remainingData = ''
                return (-1,remainingData)
                # if len(splitData) != (stringLength+1):
                #     return (-1, remainingData)
                # else:
                #     return (parsed,remainingData)
                # return ([],actualData)
            else:
                remainingData = splitData[1]
            #TODO: fix: infinite loop when string ends with partial data piece

            # if len(re.split(r',',remainingData)) < 12:
            #     break
            # print(parsed)
            # print(remainingData)
        return parsed, remainingData

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

    def simulate_serial(self):
        random_data = self.generate_random_data_array()

        return 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + str(random_data[4]) + ',' + str(random_data[5]) + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',E'

    def generate_random_data_array(self):
        global counter_gps

        min_random = 0
        max_random = 100

        """ Create decent GPS coordinates for test """
        counter_gps += 0.1
        lat = 32 + (counter_gps ** 2) * 0.001
        long = -107 + (counter_gps ** 2) ** 0.002

        """ Generate random telemetry data """
        alt = randint(min_random, max_random) + random.random()
        temp = randint(-100, max_random) + random.random()
        vel = randint(min_random, max_random) + random.random()
        acc = randint(min_random, max_random) + random.random()
        sat = randint(min_random, max_random) + random.random()
        global start_time
        current_time = round(datetime.datetime.utcnow().timestamp()) - start_time

        return [lat, long, alt, current_time, temp, vel, acc, sat]

    def processParsed(self, data):
        """
        errorCodeTuple: (200,300)
        updateantenna: true if we want to update antenna values
        full_data: true if we want to process the full data
        :param data: (result,(errorCodesTuple), counter_antenna, telemetry_data, updateantenna, full_data
        :return: new telemetry_data, new counter_antenna
        """

        result = data[0]
        e1 = data[1][0]
        e2 = data[1][1]
        counter_antenna = data[2]
        t_data = data[3]
        update_antenna = data[4]
        full_data = data[5]
        if result[0] == e1 or result[0] == e2:
            for data_chunk in result[1]:
                # print(data_chunk)
                if full_data:
                    gps_data_chunk = [data_chunk[0], data_chunk[1], data_chunk[7]]

                    """ Save telemetry data"""
                    self.data_storage.save_telemetry_data(data_chunk)
                    self.data_storage.save_gps_data(gps_data_chunk)

                    """ Plot telemetry data and update GUI """
                    try:
                        self.plots.plot_telemetry_data(data_chunk)
                    except:
                        print("Error plotting telemetry data")
                    try:
                        self.plots.plot_gps_data(data_chunk)
                    except:
                        print("Error plotting GPS data")
                    try:
                        self.plots.update_plots()
                    except:
                        print("Error updating plots")
                    if update_antenna:
                        counter_antenna += 1
                    if counter_antenna % 2 == 0 and update_antenna:  # Is 1000 the best number for this?
                        antenna_angle = self.find_angle(gps_data_chunk)
                        self.plots.antennaAngle.configure(
                            text='ANTENNA ANGLE: ' + str(antenna_angle[0]) + ' (xy), ' + str(antenna_angle[1]) + ' (z)')
                    if result[0] == e1:
                        t_data = result[2]
                        pass
                    elif result[0] == e2:  # empty
                        t_data = ''
                        pass
                else :
                    try:
                        self.data_storage.save_gps_data(data_chunk)
                    except:
                        print('Error saving parsed gps backup data')
        else:
            # TODO: log errors
            pass
        return t_data, counter_antenna

    def test_serial_missingdata(self):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())
        time.sleep(2)
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + ',' + str(random_data[5]) + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',E'
        p = self.parseFull((string,telemetry_data_length))
        print(p)
        self.data_storage.save_telemetry_data(p[1])
        pass

    def sim_gps(self):
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',E'
        return string
    
    def log_parse(self, data):

        print(data, file=open("../storage/parselog.txt", "a"))
        # f = open("../storage/parselog.txt", "a")
        # f.write(data)
        # f.close()
        pass

def main():
    data_storage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(data_storage, plots)
    parser.parse()


if __name__ == "__main__":
    main()
