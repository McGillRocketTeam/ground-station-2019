import time
import serial
from random import randint
import random
import re
import datetime
import math
import string
from controller.parser import Parser as parser
import model.datastorage as data_storage
import views.plots as plots

counter_gps = 0  # Counter to generate decent GPS data for test only


class ParserTester:
    start_time = 0

    def __init__(self, data_store_in, plots_in, parse_in):
        """

        :param data_store_in:
        :param plots_in:
        :param parse_in:
        """
        global start_time
        start_time = round(datetime.datetime.utcnow().timestamp())
        self.data_store = data_store_in
        self.plot = plots_in
        self.parse = parse_in
        self.one_at_a_string = ''

    def test_full(self):
        """

        :return:
        """
        print('Normal String:')
        print(self.simulate_serial())
        #
        # self.random_char()
        # st1 = self.consistent_string_modification(10000)
        # self.consistent_string_mod_test(0, 15, 5)
        # print(st1)
        # TODO: mostly send changes in the data, then ocassionally send the full string to recalibrate
        print("modified data string:")
        st1 = self.modified_data_string(1, 'zzTop')
        print(st1)

        print("test with missing:")
        self.test_with_missing_one_at_time(("random", 1, ''))
        pass

    def random_test(self):
        pass

    def test_with_missing_one_at_time(self, data):
        """

        :param data:
        data[0] is number of chars to remove
        data[1] is number of loops to do, or true for infinite loop
        data[2] is character to insert
        :return:
        """
        def in_loop(num_to_remove, str_in):
            """

            :param num_to_remove:
            :param str_in:
            :return:
            """
            str_out = str_in
            # str_out += self.modified_data_string(num_to_remove
            str_out += self.one_at_a_time(num_to_remove, char_to_insert)
            result = parser.parse_full(self.parse, (str_out, 8))
            # LOG
            parser.log_parse(self.parse, (str_out, result))
            # parser.log_parse(self.parse, result)
            counter_antenna = 0
            if result[0] == 200 or result[0] == 300:
                str_out = result[2]
            print(str_out)
            print(result)
            return str_out
        num = data[0]
        loop = data[1]
        char_to_insert = data[2]
        str1 = ''
        if loop > 0 or loop <= 0:
            for i in range(loop):
                if str.isdigit(num):
                    str1 = in_loop(num, str1)
                else:
                    str1 = in_loop(randint(0, 15), str1)
                pass
        elif loop == True:
            while loop:
                if str.isdigit(num):
                    str1 = in_loop(num, str1)
                else:
                    str1 = in_loop(randint(0, 15), str1)
                    pass
        pass

    def one_at_a_time(self, num_to_remove, char_to_insert):
        """

        :param num_to_remove:
        :param char_to_insert:
        :return:
        """
        if not self.one_at_a_string:
            self.one_at_a_string = self.modified_data_string(num_to_remove, char_to_insert)
            tr = self.one_at_a_string[0]
            self.one_at_a_string = self.one_at_a_string[1:len(self.one_at_a_string)]
            return tr
            pass
        else:
            tr = self.one_at_a_string[0]
            self.one_at_a_string = self.one_at_a_string[1:len(self.one_at_a_string)]
            return tr
            pass
        pass

    def consistent_string_modification(self, char_num_to_remove):
        """

        :param char_num_to_remove:
        :return:
        """
        str_in = self.simulate_serial()
        if char_num_to_remove < 0:
            n = char_num_to_remove % -len(str_in)
            str_in = str_in[0:n]
            pass
        elif char_num_to_remove > 0:
            n = char_num_to_remove % len(str_in)
            str_in = str_in[n:len(str_in)]
            pass
        return str_in

    def consistent_string_mod_test(self, range_min, range_max, repeat_num):
        """

        :param range_min:
        :param range_max:
        :param repeat_num:
        :return:
        """
        def parse_manager(to_remove, str_in):
            str_out = str_in
            # str_out += self.modified_data_string(num_to_remove
            str_out += self.consistent_string_modification(to_remove)
            result = parser.parse_full(self.parse, (str_out, 8))
            # LOG
            parser.log_parse(self.parse, (str_out, result))
            # parser.log_parse(self.parse, result)
            counter_antenna = 0
            if result[0] == 200 or result[0] == 300:
                str_out = result[2]
            print(str_out)
            print(result)
            return str_out

        def con_in_loop(repeat_num_inner):
            for j in range(0, repeat_num_inner):

                pass
            pass
        for i in range(range_min, range_max):
            pass
        for i in range(-range_max, -range_min):
            pass
        pass

    def random_char(self):
        s = string.ascii_uppercase + string.ascii_lowercase + string.digits
        rand = randint(0, len(s))
        return s[rand]

    def modified_data_string(self, num_char_to_remove, char_to_insert):
        """

        :param num_char_to_remove:
        :return:
        """
        # data is the number of characters to remove from the string
        str_in = self.simulate_serial()
        # str_in = "abcdefg"
        if num_char_to_remove > (len(str_in) - 3) or num_char_to_remove < 0:
            raise Exception("Invalid Input, must have value between 0 and length of string-3")
        for i in range(num_char_to_remove):
            if char_to_insert == 'random':
                insert = self.random_char()
                pass
            else:
                insert = char_to_insert
            r = randint(0, len(str_in)-3)
            p1 = str_in[0:r]
            p2 = str_in[r+1:len(str_in)]
            str_in = p1 + insert + p2

        return str_in

    def  generate_random_data_array(self):
        """

        :return:
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

    def sim_gps(self):
        random_data = self.generate_random_data_array()

        string = 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
                 str(random_data[3]) + ',' + str(random_data[4]) + ',E'
        return string

    def simulate_serial(self):
        random_data = self.generate_random_data_array()

        return 'S' + str(random_data[0]) + ',' + str(random_data[1]) + ',' + str(random_data[2]) + ',' + \
               str(random_data[3]) + ',' + str(random_data[4]) + ',' + str(random_data[5]) + ',' + \
               str(random_data[6]) + ',' + str(random_data[7]) + ',E'


def main():
    """

    """
    data_store = data_storage.DataStorage()
    plot = plots.Plots()
    prs = parser(data_storage, plots)
    pt = ParserTester(data_store, plot, prs)
    pt.test_full()


if __name__ == "__main__":
    main()
