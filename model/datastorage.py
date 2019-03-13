#!/usr/bin/python
import csv
import datetime


class DataStorage:
    def __init__(self):
        """ Create parse telemetry and gps files, as well as raw data files """
        with open('../storage/dataTelemetry.csv', 'w+') as csvfile_telemetry:
            file_writer = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Altitude', 'Time', 'Temperature', 'Velocity', 'Acceleration', 'Satelites'])
            csvfile_telemetry.close()
        with open('../storage/dataGps.csv', 'w+') as csvfile_gps:
            file_writer = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(['Current Time', 'Latitude', 'Longitude', 'Number of Satellites'])
            csvfile_gps.close()
        with open('../storage/rawData.txt', 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()

    def save_telemetry_data(self, data):
        """ Appends new telemetry data to end of the file """
        file = open("../storage/dataTelemetry.csv", "a+")
        file_writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 8:  # TODO: Consider scenarios where the input data is different
            now = datetime.datetime.now()
            file_writer.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]])  # This is the current format for saving the telemetry data
        file.close()

    def save_gps_data(self, data):
        """ Appends new GPS data to end of the file """
        file = open("../storage/dataGps.csv", "a+")
        file_writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 3:  # TODO: Consider scenarios where the input data is different
            now = datetime.datetime.now()
            file_writer.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2]])
        file.close()

    def save_raw_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        try:
            if isinstance(data, (list, tuple)):
                with open("../storage/rawData.txt", 'a+') as rawData:
                    for x in data:
                        rawData.write(x)
                        rawData.write("\n")
                    rawData.write("\n")
                    rawData.close()
            else:
                with open("../storage/rawData.txt", 'a+') as rawData:
                    rawData.write(data)
                    rawData.write("\n\n")
                    rawData.close()

        except TypeError as e:
            with open("../storage/rawData.txt", 'a+') as rawData:
                s = str(e)
                rawData.write(s)
                rawData.write("\n\n")
                rawData.close()


""" For testing purposes only:
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
"""

