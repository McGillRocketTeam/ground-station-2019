import time

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import controller.serial_sim as serial_sim
import serial
from random import randint
import random
import re
import datetime
import math

"""
telemetry long data format: Slat,long,time,alt,vel,sat,acc,temp,gyro_x,RSSI,E\n
backup GPS data: Slat,long,time,gps_alt,gps_speed,sat,E\n
"""

telemetry_data_length = 10  # Length of big telemetry data string
gps_data_length = 6  # Length of gps data string

counter_gps = 0  # Counter to generate decent GPS data for test only
ground_lat = 32.940394  # Ground station latitude
ground_long = -106.920134  # Ground station longitude
ground_alt = 0  # Ground station altitude


class Parser(QObject):
    start_time = 0

    dataChanged = pyqtSignal(list)

    def __init__(self, data_storage_in):
        super().__init__()

        self.full_telemetry = True  # Controls if receiver is for full telemetry or just gps redundancy
        self.port_from_file = False  # Controls if the port is read from a file
        self.real_data = False  # Controls if data is simulated or from actual serial reader
        self.replot_data = False  # Controls if we want to use caladan data
        self.fuseefete = False  # Controls if we want to use fuseefete data

        self.data_storage = data_storage_in
        self.antenna_angle = [0, 0]

        if not self.real_data:  # If fake data, simulate it
            if self.full_telemetry:
                self.serial_telemetry = serial_sim.SerialSim(True, self.fuseefete)
            else:
                self.serial_gps = serial_sim.SerialSim(False, self.fuseefete)
            if self.fuseefete:
                self.telemetry_data_length = 8

        if self.real_data:
            self.port_full = ''
            self.port_gps = ''
        if self.port_from_file and self.real_data:  # If real data, get the ports used from the port finder
            if self.full_telemetry:
                f = open("../storage/serial/full_telemetery.txt", "r")
                self.port_full = f.readline()
                if len(self.port_full) == 0:
                    print('Error reading port')
            else:
                f = open("../storage/serial/gps_backup.txt", "r")
                self.port_gps = f.readline()
                if len(self.port_gps) == 0:
                    print('Error reading port')
            f.close()

        self.baud = 19200
        self.baud_combo = 38400
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 0.2

        # Setup for telemetry serial
        if self.real_data and self.full_telemetry:
            ser = serial.Serial(self.port_full, self.baud_combo, self.byte, self.parity, self.stopbits, self.timeout)
            self.serial_telemetry = ser
            if not ser.isOpen():
                ser.open()
            else:
                pass

        # Setup for gps serial
        if self.real_data and not self.full_telemetry:
            ser2 = serial.Serial(self.port_gps, self.baud, self.byte, self.parity, self.stopbits, self.timeout)
            self.serial_gps = ser2
            if not ser2.isOpen():
                ser2.open()
            else:
                pass

        if self.real_data:
            self.current_ser = self.serial_telemetry if self.full_telemetry else self.serial_gps
        else:
            self.current_ser = None

    @pyqtSlot()
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
            if self.real_data:  # Dealing with real data
                failure = False
                if self.full_telemetry:  # Read line from full telemetry port
                    try:
                        telemetry_data = self.serial_telemetry.readline().decode('utf-8')
                        print(telemetry_data)
                    except:
                        failure = True
                elif not self.full_telemetry:  # Read line from gps redundancy port
                    try:
                        gps_data = self.serial_gps.readline().decode('utf-8')
                        print(gps_data)
                    except:
                        failure = True
                if failure:
                    continue

            else:  # Dealing with fake data
                if self.replot_data:  # Replot previous flight
                    self.replot_flight()
                    break
                else:  # Simulate data
                    time.sleep(0.3)
                    if self.full_telemetry:
                        telemetry_data = self.simulate_telemetry()
                        print('parser(190): {}'.format(telemetry_data))
                    elif not self.full_telemetry:
                        gps_data = self.simulate_gps()
                        print('parser(190): {}'.format(gps_data))

            """ Save raw data to files """
            if self.full_telemetry:
                self.data_storage.save_raw_telemetry_data(telemetry_data)
            else:
                self.data_storage.save_raw_gps_data(gps_data)

            """ Process telemetry data """
            if self.full_telemetry:
                result = self.split_array(telemetry_data, telemetry_data_length)
                if self.fuseefete and result[0] == 400:
                    result[1][0] = result[1][0].strip('S')
                    to_send = result[1][0:-1]

                    if len(to_send) == 9:
                        time.sleep(0.0025)
                        to_send[5] = int(to_send[5], 16)
                        to_send[2] = float(to_send[2]) + self.serial_telemetry.get_multiplier(self.full_telemetry)
                        self.process_parsed(result[1], counter_antenna, True)
                        self.dataChanged.emit(to_send)
                if result[0] == 200:  # Successfully parsed
                    self.process_parsed(result[1], counter_antenna, True)
                    self.dataChanged.emit(result[1])
            else:
                """ Process gps data """
                gps_result = self.split_array(gps_data, gps_data_length)
                if gps_result[0] == 200:  # Successfully parsed
                    self.process_parsed(gps_result[1], counter_antenna, False)
                    self.dataChanged.emit(gps_result[1])

            counter_antenna += 1
            self.dataChanged.emit(self.antenna_angle)

    def split_array(self, data, string_length):
        """
        :param data: datastring to split
        :param string_length: length of string (telemetry or gps)
        :return:
        """
        """
        Error Codes: 
        500 error converting occured
        200 data was successfully parsed
        400 no data was parsed from the string
        """
        split_data = re.split(',', data)

        if not len(split_data) == string_length + 1:  # Invalid array length
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
        """ Save data and calculate antenna angles"""
        if is_telemetry:
            self.data_storage.save_telemetry_data(data)

            if counter_antenna % 50 == 0:  # Is 1000 the best number for this?
                try:
                    self.antenna_angle = self.find_angle(data)
                    print(str(self.antenna_angle) + '\n')
                    self.data_storage.save_antenna_angles(self.antenna_angle, data[2])
                except:
                    print("Error calculating antenna angle")
        else:
            self.data_storage.save_gps_data(data)

    def convert_string_list_float(self, data):
        if len(data) == telemetry_data_length:
            data[5] = int(data[5], 16)
        listout = [float(x) for x in data]
        return listout

    def replot_flight(self):
        """ Read from a previous flight """
        file = open("../storage/telemetry/2019-05-07-20-06-29_data_telemetry.csv", "r")  # Open data file for plotting
        pull_data = file.read()
        data_list = pull_data.split('\n')
        first_line = True
        for eachLine in data_list:
            if first_line:
                first_line = False  # Don't read data if first line, since it is the header
            elif len(eachLine) > 1:
                saved_time, lat, long, alt, time, temp, vel, acc, sat = eachLine.split(',')
                telemetry_data = [lat, long, time, alt, vel, sat, acc, temp, temp]
                try:
                    self.plots.plot_telemetry_data(telemetry_data)
                except:
                    print("Error plotting telemetry data")
                #yield 0.05
        file.close()

    def find_angle(self, data):
        '''calculate antenna direction given rocket coordinates and ground station coordinates'''
        angle = []  # Ordered as angle from east, then angle from ground
        # coordinates of ground station and rocket
        ground_x = ground_long
        ground_y = ground_lat
        rocket_x = float(data[1])  # Rocket long
        rocket_y = float(data[0])  # Rocket lat
        rocket_alt = float(data[3])

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
        d = 2*6371000*math.asin(math.sqrt(math.pow((math.sin((rocket_y-ground_y)/2)), 2) + math.cos(ground_y)*math.cos(rocket_y)*math.pow(math.sin((rocket_x-ground_x)/2), 2)))
        phi = (180/math.pi)*math.atan((rocket_alt - ground_alt)/d)
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
               str(random_data[3]) + ',' + str(random_data[4]) + ',' + str('D') + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',' + str(random_data[8]) +\
               ',' + str(random_data[5]) + ',E\n'

    def simulate_gps(self):
        """
        :return: a string starting with 'S' followed by 4 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',' + str('E') + ',E\n'
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
        gyro_x = randint(min_random, max_random) + random.random()
        acc = randint(min_random, max_random) + random.random()
        sat = randint(min_random, max_random) + random.random()
        global start_time
        current_time = round(datetime.datetime.utcnow().timestamp()) - start_time
        return [lat, long, current_time, alt, vel, sat, acc, temp, gyro_x]

    def simulate_telemetry(self):
        """"
        :return:  a string starting with 'S' followed by 8 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        return 'S' + str(random_data[0])[0:10] + ',' + str(random_data[1])[0:10] + ',' + str(random_data[2])[0:8] + ',' + \
               str(random_data[3])[0:8] + ',' + str(random_data[4])[0:8] + ',' + str('D')[0:8] + ',' + \
               str(random_data[6])[0:8] + ',' + str(random_data[7])[0:8] + ',' + str(random_data[8])[0:8] +\
               ',' + str(random_data[-1]) + ',E\n'

    def simulate_gps(self):
        """
        :return: a string starting with 'S' followed by 4 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',' + str('F') + ',' + str(random_data[5]) + ',E\n'
        return string
