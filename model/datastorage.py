#!/usr/bin/python
import csv
import datetime
import os

cur_time = ""

class DataStorage:

    def __init__(self):
        """ Create parse telemetry and gps files, as well as raw data files """
        if (os.path.isdir("../storage")) == False:
            os.mkdir("../storage")
        now = datetime.datetime.now
        cur_time = now.strftime("%Y-%m-%d-%H-%M-%S")
        file_name = cur_time + "_data_telemetry.csv"
        with open('../storage/' + file_name, 'w+') as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Altitude', 'Time', 'Temperature', 'Velocity', 'Acceleration', 'Satelites'])
            csvfile_telemetry.close()
        file_name = cur_time + "_data_gps.csv"
        with open('../storage/' + file_name, 'w+') as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Number of Satellites', 'Altitude'])
            csvfile_gps.close()
        file_name = cur_time + "_raw_data.txt"
        with open('../storage/' + file_name, 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

    def save_telemetry_data(self, data):
        """ Appends new telemetry data to end of the file """
        file_name = cur_time + "_data_telemetry.csv"
        file = open('../storage/' + file_name, "a+")
        file_writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 8:  # TODO: Consider scenarios where the input data is different
            now = datetime.datetime.now
            file_writer.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]])  # This is the current format for saving the telemetry data
        file.close()

    def save_gps_data(self, data):
        """ Appends new GPS data to end of the file """
        file_name = cur_time + "_data_gps.csv"
        file = open('../storage/' + file_name, "a+")
        file_writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 5:  # TODO: Consider scenarios where the input data is different
            now = datetime.datetime.now()
            file_writer.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4]])
        file.close()

    def save_raw_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        file_name = cur_time + "_raw_data.txt"
        try:
            if isinstance(data, (list, tuple)):
                with open('../storage/' + file_name, 'a+') as rawData:
                    for x in data:
                        rawData.write(x)
                        rawData.write("\n")
                    rawData.write("\n")
                    rawData.close()
            else:
                with open('../storage/' + file_name, 'a+') as rawData:
                    rawData.write(data)
                    rawData.write("\n\n")
                    rawData.close()

        except TypeError as e:
            with open('../storage/' + file_name, 'a+') as rawData:
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


