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

        cur_time = time.strftime("%Y-%m-%d-%H-%M-%S")

        """ Create parse telemetry and gps files, as well as raw data files """
        self.telemetry_file_name = cur_time + "_data_telemetry.csv"
        with open('../storage/telemetry/' + self.telemetry_file_name, 'w+') as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Altitude', 'Time', 'Temperature', 'Velocity', 'Acceleration', 'Satelites'])
            csvfile_telemetry.close()

        self.gps_file_name = cur_time + "_data_gps.csv"
        with open('../storage/gps/' + self.gps_file_name, 'w+') as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Number of Satellites', 'Altitude'])
            csvfile_gps.close()

        self.raw_telemetry_file_name = cur_time + "_raw_data.txt"
        with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

    def save_telemetry_data(self, data):
        """ Appends new telemetry data to end of the file """
        with open('../storage/telemetry/' + self.telemetry_file_name, "a+") as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if len(data) == 8:  # TODO: Consider scenarios where the input data is different
                file_writer.writerow([time.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]])  # This is the current format for saving the telemetry data
            csvfile_telemetry.close()

    def save_gps_data(self, data):
        """ Appends new GPS data to end of the file """
        with open('../storage/gps/' + self.gps_file_name, "a+") as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            if len(data) == 5:  # TODO: Consider scenarios where the input data is different
                file_writer.writerow([time.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4]])
            csvfile_gps.close()

    def save_raw_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        try:
            if isinstance(data, (list, tuple)):
                with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                    for x in data:
                        rawData.write(x)
                        rawData.write("\n")
                    rawData.write("\n")
                    rawData.close()
            else:
                with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                    rawData.write(data)
                    rawData.write("\n\n")
                    rawData.close()

        except TypeError as e:
            with open('../storage/raw_telemetry/' + self.raw_telemetry_file_name, 'a+') as rawData:
                s = str(e)
                rawData.write(s)
                rawData.write("\n\n")
                rawData.close()


 # For testing purposes only:
if __name__ == '__main__':
    storage = DataStorage()
    list1 = ["Time1", "Temp1", "Alt1", "Vel1", "Acc1"]
    listdata = ["2", "20", "30", "40", "78"]
    storage.save_telemetry_data(list1)
    storage.save_telemetry_data(listdata)
    storage.save_raw_data(("neco", "neco", "zaseneco"))
    storage.save_raw_data(None)
    storage.save_raw_data("thisisa string")
    storage.save_raw_data(listdata)


