from random import randint
import random
import datetime


class SerialSim:
    start_time = 0
    tele_count_fusee = 0
    tele_time_max = 1149574
    tele_multiplier = 0
    gps_time_max = 1169235
    gps_multiplier = 0
    gps_count_fusee = 0
    fuse_list_tele = []
    fuse_list_gps = []

    def __init__(self, tel_or_gps, fusee_data):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())
        self.tel = tel_or_gps
        self.fusee = fusee_data
        if self.fusee:
            if self.tel:
                with open('../Fusee-Fete/raw_telemetry_fuseefete.txt', 'r') as f:
                    content = f.readlines()
            else:
                with open('../Fusee-Fete/raw_gps_fuseefete.txt', 'r') as f:
                    content = f.readlines()
            self.manage_content(content, self.tel)
            # x = 'debug'
        pass

    def manage_content(self, content, tel):
        for s in content:
            if s != '\n' and s != 'Raw Data:\n' and s != '________________________________________\n':
                t = s.strip('\n')
                try:
                    u = int(t)
                except:
                    u = -100000000
                if u > -90 and u < -40:
                    pass
                else:
                    if tel:
                        self.fuse_list_tele.append(t)
                    else:
                        self.fuse_list_gps.append(t)

    def get_multiplier(self, tele):
        if tele:
            return self.tele_multiplier*self.tele_time_max
        else:
            return self.gps_multiplier*self.gps_time_max
        pass

    def readline(self):
        # print('tele: {}      gps: {}'.format(self.tele_count_fusee, self.gps_count_fusee))
        if self.tel:
            if self.fusee:
                if self.tel:
                    if self.tele_count_fusee >= len(self.fuse_list_tele):
                        self.tele_multiplier = self.tele_multiplier + 1
                        self.tele_count_fusee = 0
                    c = self.tele_count_fusee
                    # if self.tele_count_fusee == (len(self.fuse_list_tele) - 1):
                    self.tele_count_fusee = self.tele_count_fusee + 1
                    return self.fuse_list_tele[c]
                else:
                    if self.gps_count_fusee >= len(self.fuse_list_gps):
                        self.gps_multiplier = self.gps_multiplier + 1
                        self.gps_count_fusee = 0
                    c = self.gps_count_fusee
                    self.gps_count_fusee = self.gps_count_fusee + 1
                    return self.fuse_list_gps[c]
            else:
                # return 'S45.505520,-73.576042,679274,-3.48,2.203880,B,9.95,17.79,0.187500,-73,E'  # self.simulate_gps()
                return self.simulate_telemetry()
        else:
            return self.simulate_gps()

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
        counter_gps = 0.1
        lat = 32 + (counter_gps ** 2) * 0.001
        long = -107 + (counter_gps ** 2) ** 0.002

        """ Generate random telemetry data """
        alt = randint(min_random, max_random) + random.random()
        temp = randint(-100, max_random) + random.random()
        vel = randint(min_random, max_random) + random.random()
        gyro_x = randint(min_random, max_random) + random.random()
        acc = randint(min_random, max_random) + random.random()
        sat = randint(min_random, max_random) + random.random()
        rssi = randint(-200, 200)
        global start_time
        current_time = round(datetime.datetime.utcnow().timestamp()) - start_time
        return [lat+(current_time % 5000)+random.random(), long+(current_time % 5000)+random.random(), current_time, alt, vel, sat, acc, temp, gyro_x, rssi]
