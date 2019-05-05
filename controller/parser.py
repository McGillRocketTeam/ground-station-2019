import time

import model.datastorage as data_storage
import views.plots as plots
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
gps_data_length = 5  # Current length of gps data string
counter_gps = 0  # Counter to generate decent GPS data for test only
ground_lat = 0  # Ground station latitude
ground_long = 0  # Ground station longitude
ground_alt = 0  # Ground station altitude


class Parser:
    start_time = 0

    def __init__(self, data_storage_in, plots_in):
        self.data_storage = data_storage_in
        self.plots = plots_in

        # TODO Add port setup for GPS
        # TODO Automated port check setup

        # self.port = "COM5"
        # ls /dev/tty.*
        # use above to find port of arduino on mac
        # self.port = "/dev/tty.usbserial-A104IBE7"
        # self.port = "/dev/tty.usbmodem14201"
        self.port = "/dev/tty.usbmodem14101"

        self.port2 = "/dev/tty.usbmodem14101"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 3  # sec
        # setup for telemetry serial
        # ser = serial.Serial(self.port, self.baud, self.byte, self.parity, self.stopbits)
        # self.serial_telemetry = ser
        # if not ser.isOpen():
        #     ser.open()
        # else:
        #     pass

        # Setup for gps serial
        # ser2 = serial.Serial(self.port2, self.baud, self.byte, self.parity, self.stopbits)
        # self.serial_gps = ser2
        # if not ser2.isOpen():
        #     ser2.open()
        # else:
        #     pass

    def parse(self):
        """
        Contains the main while loop is used to repeatedly parse the received data
        :return: no return data
        """
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())

        telemetry_data = ''
        gps_data = ''
        counter_antenna = 0
        loop_control = True

        while loop_control:
            # time.sleep(0.5)
            real_data = False  # Controls if data is simulated or from actual serial reader
            caladan_data = False  # Controls if we want to use caladan data
            if real_data:
                # telemetry_data += self.serial_telemetry.read(size=1000).decode('utf-8')
                # gps_data += self.serial_gps.read(size=1000).decode('utf-8')

                print(telemetry_data)
                print(gps_data)
            else:  # Fake data
                if caladan_data:
                    self.read_from_file()
                else:
                    telemetry_data += self.simulate_telemetry()
                    gps_data += self.simulate_gps()
                    print(telemetry_data)
                    print(gps_data)

            """ Save raw data to files """
            self.data_storage.save_raw_data(telemetry_data)
            # self.data_storage.save_raw_data(gps_data)

            """ Process telemetry data """
            # processing for full telemetry data:
            result = self.parse_full((telemetry_data, telemetry_data_length))
            print(result)
            return_data = self.process_parsed((result, (200, 300), counter_antenna, telemetry_data, True, True))
            telemetry_data = return_data[0]
            counter_antenna = return_data[1]

            """ Process gps data """
            # processing for gps:
            # gps_result = self.parse_full((gps_data, gps_data_length))
            # print('gps::')
            # print(gps_result)
            # return_gps_data = self.process_parsed((gps_result,(200,300),counter_antenna,gps_data,False, False))
            # gps_data = return_gps_data[0]

    def process_parsed(self, data):
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
                    elif result[0] == e2:  # empty
                        t_data = ''
                else:
                    try:
                        self.data_storage.save_gps_data(data_chunk)
                    except:
                        print('Error saving parsed gps backup data')
        else:
            # TODO: log errors
            pass
        return t_data, counter_antenna

    def parse_full(self, data):
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
        data_string = data[0]
        data_length = data[1]
        parse_helped_data = self.parse_helper((data_string,data_length))

        if parse_helped_data[0] == -1:
            data_list = []
            status = 400
        else:
            data_list = [parse_helped_data[0][0:data_length]]

        while len(re.split(r',',parse_helped_data[1])) > (data_length+1):
            parse_helped_data = self.parse_helper((parse_helped_data[1],data_length))
            if parse_helped_data[0] == -1:
                break
            data_list.append(parse_helped_data[0][0:data_length])
            pass
        if len(data_list) > 0:  # TODO: implement parsing logic here
            if len(parse_helped_data) == 1:
                return 300, data_list, ''
            else:
                return 200, data_list, parse_helped_data[1]
        return status,


    def parse_helper(self, data):
        """
        this function takes in a string of any length, and returns a tuple,
        where slot 0 is the current array of separated values from one telemetry reading
        if slot 0 contains the int -1, then there was no data to be parsed
        slot 1 is the remaining string
        :param data: tuple(actual_data,string_length)
        actual_data is the string to be parsed
        string_length is the number of values separated by commas in the string
        :return: tuple(array, string)
        array is the list of values that were separated by commas in the input string
        string is the remaining string that was not able to be parsed
        """
        # split the data tuple into the actual data, and the length of the data string
        actual_data = data[0]
        string_length = data[1]
        # Takes the first set of data from the data string, or removes the garbage from the front of it
        split_data = re.split(r"S", actual_data, 1)
        remaining_data = ''
        if len(split_data) == 2:
            remaining_data = split_data[1]
        else:
            split_try = re.split(r",", split_data[0])
            if len(split_try) == (string_length+1):
                return split_try, ""
            else:
                return -1, split_data[0]
        parsed = re.split(r",", split_data[0])
        while len(parsed) != (string_length+1):
            split_data = re.split(r"S", remaining_data, 1)
            parsed = re.split(r",", split_data[0])
            if len(split_data) == 1:
                # remaining_data = ''
                return (-1, remaining_data)
                # if len(splitData) != (stringLength+1):
                #     return (-1, remaining_data)
                # else:
                #     return (parsed,remaining_data)
                # return ([],actualData)
            else:
                remaining_data = split_data[1]
            #TODO: fix: infinite loop when string ends with partial data piece

            # if len(re.split(r',',remaining_data)) < 12:
            #     break
            # print(parsed)
            # print(remaining_data)
        return parsed, remaining_data

    def parse_help_fast(self, data):
        '''

        :param data: Tuple (d0, d1):
        d0 is a string to be parsed
        d1 is the number of commas in the complete telemetry string
        :return:
        -1 if insufficient number of commas, S or E

        '''
        # split the data tuple into the actual data, and the length of the data string
        string_input = data[0]
        number_commas = data[1]
        # string_list = list(string_input)
        s_number = 0
        # s_locations = []
        e_number = 0
        comma_number = 0
        for char in string_input:
            if char == ',':
                comma_number += 1
            elif char == 'S':
                s_number += 1
            elif char == 'E':
                e_number += 1
            if s_number > 1 and e_number > 1 and comma_number > number_commas:
                break
            pass
        # print('S: {}  E: {}  ,: {}'.format(s_number, e_number, comma_number)) # TODO: remove debug code
        if s_number < 1 or e_number < 1 or comma_number < number_commas:
            return -1, string_input
        split_input = re.split('S', string_input, 1)
        if len(split_input) == 1:
            return -1, string_input
        working_string = split_input[1]
        values = re.split(',', working_string, number_commas)
        return values, ''
        pass

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
        if abs(rocket_x - ground_x) < math.pow(10, -9) and rocket_y > ground_y: # Rocket is directly N from ground station
            theta = 90
        elif abs(rocket_x - ground_x) < math.pow(10, -9) and rocket_y < ground_y: # Rocket is directly S from ground station
            theta = 270
        elif rocket_x > ground_x and abs(rocket_y - ground_y) < math.pow(10, -9): # Rocket is directly E from ground station
            theta = 0
        elif rocket_x < ground_x and abs(rocket_y - ground_y) < math.pow(10, -9): # Rocket is directly W from ground station
            theta = 180
        elif rocket_x < ground_x and rocket_y > ground_y: # Rocket is NW from ground station
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

    def convert_DMS_to_DD(self, deg_min):
        """ Converts degree minutes seconds into decimal degrees """
        min_val = 0.0
        dec_deg = 0.0
        min_val = math.fmod(deg_min, 100.0)
        deg_min = (deg_min / 100)
        dec_deg = deg_min + (min_val / 60)
        return dec_deg

    def simulate_telemetry(self):
        """"
        :return:  a string starting with 'S' followed by 8 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        return 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + str(random_data[4]) + ',' + str(random_data[5]) + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',E'

    def simulate_gps(self):
        """
        :return: a string starting with 'S' followed by 4 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',E'
        return string

    def generate_random_data_array(self):
        """
        Generates a array with 8 elements to simulate data
        [lat, long, alt, current_time, temp, vel, acc, sat]
        :return: list of length 8 with random data (except time increments)
        """
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

    def read_from_file(self):
        """ Read from caladan sim test file """
        file = open("../tests/CaladanSimData/CALADAN_DATA_GROUND_STATION.csv", "r")  # Open data file for plotting
        pull_data = file.read()
        data_list = pull_data.split('\n')
        first_line = True
        for eachLine in data_list:
            if first_line:
                first_line = False  # Don't read data if first line, since it is the header
            elif len(eachLine) > 1:
                lat, long, alt, time, temperature, altitude, velocity, acceleration, sat, vv, va, m, t, a = eachLine.split(
                    ',')  # Split each line by comma
                telemetry_data = [lat, long, alt, time, temperature, altitude, velocity, acceleration, sat]
                data_gps = [lat, long, sat]
                try:
                    self.plots.plot_telemetry_data(telemetry_data)
                except:
                    print("Error plotting telemetry data")
                try:
                    self.plots.plot_gps_data(data_gps)
                except:
                    print("Error plotting gps data")
                try:
                    self.plots.update_plots()
                except:
                    print("Error updating plots")

        file.close()

    def test_serial_missingdata(self):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())
        time.sleep(2)
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + ',' + str(random_data[5]) + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',E'
        p = self.parse_full((string, telemetry_data_length))
        print(p)
        self.data_storage.save_telemetry_data(p[1])

    def log_parse(self, data):
        print(data, file=open("../storage/parselog.txt", "a"))
        # f = open("../storage/parselog.txt", "a")
        # f.write(data)
        # f.close()
        pass


def main():
    data_store = data_storage.DataStorage()
    plots_instance = plots.Plots()
    parser = Parser(data_store, plots_instance)
    parser.parse()


if __name__ == "__main__":
    main()
