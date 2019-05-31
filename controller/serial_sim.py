from random import randint
import random
import datetime


class SerialSim:
    start_time = 0
    fuse_list = []
    def __init__(self, tel_or_gps, fusee_data):
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())
        self.tel = tel_or_gps
        self.fusee = fusee_data
        if self.fusee:
            if self.tel:
                pass
            else:
                pass
        pass

    def readline(self):
        if self.tel:
            return self.simulate_telemetry()
        else:
            return self.simulate_gps()

    def simulate_telemetry(self):
        """"
        :return:  a string starting with 'S' followed by 8 random numbers separated by commas ending with 'E'
        """
        random_data = self.generate_random_data_array()

        return 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + str(random_data[4]) + ',' + str('D') + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',' + str(random_data[8]) +\
               ',' + str('12345') + ',E\n'

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
        global start_time
        current_time = round(datetime.datetime.utcnow().timestamp()) - start_time
        return [lat, long, current_time, alt, vel, sat, acc, temp, gyro_x]
