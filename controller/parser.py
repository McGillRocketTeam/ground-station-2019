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
data format: Slat,long,alt,time,temp,vel,acc,sat,E\n
backup GPS data: lat, long, alt, sat#
"""
telemetry_data_length_big = 8  # Length of big telemetry data string
telemetry_data_length_small = 3  # Length of small telemetry data string
gps_data_length = 5  # Length of gps data string
counter_gps = 0  # Counter to generate decent GPS data for test only
ground_lat = 0  # Ground station latitude
ground_long = 0  # Ground station longitude
ground_alt = 0  # Ground station altitude


class Parser:
    start_time = 0

    def __init__(self, data_storage_in, plots_in):
        self.data_storage = data_storage_in
        self.plots = plots_in

        # TODO Automated port check setup

        # ls /dev/tty.*
        # use above to find port of arduino on mac

        self.port = "/dev/tty.usbserial-00002014"
        self.port2 = "/dev/tty.usbmodem14101"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 3

        # Setup for telemetry serial
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
        Contains the main while loop used to repeatedly parse the received data
        """
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())

        telemetry_data = ''
        gps_data = ''
        counter_antenna = 0
        loop_control = True

        while loop_control:
            real_data = False  # Controls if data is simulated or from actual serial reader
            caladan_data = False  # Controls if we want to use caladan data
            if real_data:
                telemetry_data = self.serial_telemetry.readline().decode('utf-8')
                # gps_data = self.serial_gps.readline().decode('utf-8')
            else:  # Fake data
                if caladan_data:
                    self.read_from_file()
                else:
                    telemetry_data = self.simulate_telemetry()
                    gps_data = self.simulate_gps()

            """ Save raw data to files """
            self.data_storage.save_raw_data(telemetry_data)
            self.data_storage.save_raw_data(gps_data)

            """ Process telemetry data """
            result = self.split_telemetry_array(telemetry_data, telemetry_data_length_big, telemetry_data_length_small)
            self.log_parse(result)
            print(result)
            if result[0] == 200:  # Successfully parsed
                self.process_parsed(result[1], counter_antenna, True)

            """ Process gps data """
            gps_result = self.split_gps_array(gps_data, gps_data_length)
            self.log_parse(result)
            print(gps_result)
            if result[0] == 200:  # Successfully parsed
                self.process_parsed(result[1], counter_antenna, False)

            counter_antenna += 1

    def split_telemetry_array(self, data, big_length, small_length):
        """
        :param data: datastring to split
        :param small_length: length of small telemetry string
        :param big_length: length of big telemetry string
        :return:
        """
        """
        Error Codes: 
        500 error converting occured
        200 data was successfully parsed
        400 no data was parsed from the string
        """
        split_data = re.split(',', data)

        if not len(split_data) == big_length + 1 and not len(split_data) == small_length + 1:  # Invalid array length
            return 400, split_data

        split_data[0] = split_data[0][1:]  # Remove S from datastring
        split_data = split_data[0:-1]  # Remove E from datastring
        try:
            self.convert_string_list_float(split_data)  # Try converting to values to float right away to catch errors
            return 200, split_data
        except:
            return 500, split_data

    def split_gps_array(self, data, gps_length):
        """
        :param data: datastring to split
        :param gps_length: length of gps redundancy string
        :return:
        """
        """
        Error Codes: 
        500 error converting occured
        200 data was successfully parsed
        400 no data was parsed from the string
        """
        split_data = re.split(',', data)

        if not len(split_data) == gps_length + 1:  # Invalid array length
            return 400, split_data

        split_data[0] = split_data[0][1:]  # Remove S from datastring
        split_data = split_data[0:-1]  # Remove E from datastring
        try:
            self.convert_string_list_float(split_data)  # Try converting to values to float right away to catch errors
            return 200, split_data
        except:
            return 500, split_data

    def process_parsed(self, data, counter_antenna, is_telemetry):
        """
        :param data: parsed flight data
        :param counter_antenna: current counter for antenna updating
        :param is_telemetry: indicates if dealing with telemetry string, or with gps redundancy string
        """
        """ Save and plot data"""
        if is_telemetry:
            self.data_storage.save_telemetry_data(data)
            try:
                self.plots.plot_telemetry_data(data)
            except:
                print("Error plotting telemetry data")
        else:
            self.data_storage.save_gps_data(data)
            try:
                self.plots.plot_gps_data(data)
            except:
                print("Error plotting GPS data")
        try:
            self.plots.update_plots()
        except:
            print("Error updating plots")

        # if counter_antenna % 2 == 0:  # Is 1000 the best number for this?
        #     antenna_angle = self.find_angle(gps_data_chunk)
        #     self.plots.antennaAngle.configure(
        #         text='ANTENNA ANGLE: ' + str(antenna_angle[0]) + ' (xy), ' + str(antenna_angle[1]) + ' (z)')

    def convert_string_list_float(self, data):
        listout = [float(x) for x in data]
        return listout

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
               str(random_data[6]) + ',' + str(random_data[7]) + ',E\n'

    def simulate_gps(self):
        """
        :return: a string starting with 'S' followed by 4 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',E\n'
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

    def log_parse(self, data):
        # f = open("../storage/parselog.txt", "a")
        # f.write(data[0])
        # f.write(data[1])
        # f.close()
        pass


def main():
    data_store = data_storage.DataStorage()
    plots_instance = plots.Plots()
    parser = Parser(data_store, plots_instance)
    parser.parse()


if __name__ == "__main__":
    main()
