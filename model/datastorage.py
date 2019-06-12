#!/usr/bin/python
import csv
import time
import os


class DataStorage:

    def __init__(self):
        """ Set up folders if user does not have them """
        if not (os.path.isdir("../storage")):
            os.mkdir("../storage")

        if not (os.path.isdir("../storage/telemetry")):
            os.mkdir("../storage/telemetry")

        if not (os.path.isdir("../storage/gps")):
            os.mkdir("../storage/gps")

        if not (os.path.isdir("../storage/raw_telemetry")):
            os.mkdir("../storage/raw_telemetry")

        if not (os.path.isdir("../storage/raw_gps")):
            os.mkdir("../storage/raw_gps")

        if not (os.path.isdir("../storage/antenna_angles")):
            os.mkdir("../storage/antenna_angles")

        if not (os.path.isdir("../storage/serial")):
            os.mkdir("../storage/serial")


        cur_time = time.strftime("%Y-%m-%d-%H-%M-%S")

        """ Create parse telemetry and gps files, as well as raw data files """
        self.telemetry_file_name = cur_time + "_data_telemetry.csv"
        with open('../storage/telemetry/' + self.telemetry_file_name, 'w+') as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Time', 'Altitude', 'Velocity', 'Satelites', 'Acceleration', 'Temperature', 'GyroX'])
            csvfile_telemetry.close()

        self.gps_file_name = cur_time + "_data_gps.csv"
        with open('../storage/gps/' + self.gps_file_name, 'w+') as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Time', 'GPS_Altitude', 'GPS_Speed', 'Number of Satellites'])
            csvfile_gps.close()

        self.raw_telemetry_file_name = cur_time + "_raw_data.txt"
        with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

        self.raw_gps_file_name = cur_time + "_raw_data.txt"
        with open('../storage/raw_gps/' + self.raw_gps_file_name, 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

        self.antenna_angles_file_name = cur_time + "_antenna_angles.txt"
        with open('../storage/antenna_angles/' + self.antenna_angles_file_name, 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

    def save_telemetry_data(self, data):
        """ Appends new telemetry data to end of the file """
        with open('../storage/telemetry/' + self.telemetry_file_name, "a+") as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if len(data) == 9 or len(data) == 10:  # TODO: Consider scenarios where the input data is different
                file_writer.writerow([time.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]])  # This is the current format for saving the telemetry data
            csvfile_telemetry.close()

    def save_gps_data(self, data):
        """ Appends new GPS data to end of the file """
        with open('../storage/gps/' + self.gps_file_name, "a+") as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if len(data) == 6 or len(data) == 7:  # TODO: Consider scenarios where the input data is different
                file_writer.writerow([time.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5]])
            csvfile_gps.close()

    def save_raw_telemetry_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        try:
            if isinstance(data, (list, tuple)):
                with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                    for x in data:
                        rawData.write(x)
                        rawData.write("\n")
                    # rawData.write(str(rssi) + "\n")  # Save RSSI data at the end
                    rawData.close()
            else:
                with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                    rawData.write(data)
                    # rawData.write(str(rssi) + "\n")  # Save RSSI data at the end
                    rawData.close()

        except TypeError as e:
            with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                s = str(e)
                rawData.write(s)
                rawData.write("\n")
                rawData.close()

    def save_raw_gps_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        try:
            if isinstance(data, (list, tuple)):
                with open('../storage/raw_gps/' + self.raw_gps_file_name, 'a+') as rawData:
                    for x in data:
                        rawData.write(x)
                        rawData.write("\n")
                    # rawData.write(str(rssi) + "\n")
                    rawData.close()
            else:
                with open('../storage/raw_gps/' + self.raw_gps_file_name, 'a+') as rawData:
                    rawData.write(data)
                    # rawData.write(str(rssi) + "\n")
                    rawData.close()

        except TypeError as e:
            with open('../storage/raw_gps/' + self.raw_gps_file_name, 'a+') as rawData:
                s = str(e)
                rawData.write(s)
                rawData.write("\n")
                rawData.close()

    def save_antenna_angles(self, data, time):
        # TODO: Solve for more edge cases if there are any?
        try:
            if isinstance(data, (list, tuple)):
                with open('../storage/antenna_angles/' + self.antenna_angles_file_name, 'a+') as rawData:
                    for x in data:
                        rawData.write(str(x))
                        rawData.write("\n")
                    rawData.write(str(time) + "\n")  # Save time under
                    rawData.close()
            else:
                with open('../storage/antenna_angles/' + self.antenna_angles_file_name, 'a+') as rawData:
                    rawData.write(str(data))
                    rawData.write(str(time) + "\n")  # Save time under
                    rawData.close()

        except TypeError as e:
            with open('../storage/antenna_angles/' + self.antenna_angles_file_name, 'a+') as rawData:
                s = str(e)
                rawData.write(s)
                rawData.write("\n")
                rawData.close()
