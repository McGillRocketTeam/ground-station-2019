#!/usr/bin/python
import csv
import datetime

class DataStorage:

    # Creates a new file where the data will be stored
    def __init__(self):
        with open('../storage/dataTelemetry.csv', 'w+') as csvfile_telemetry:
            filewriter = csv.writer(csvfile_telemetry, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Current Time', 'Time', 'Temperature', 'Altitude', 'Velocity', 'Acceleration'])
            csvfile_telemetry.close()
        with open('../storage/dataGps.csv', 'w+') as csvfile_gps:
            filewriter = csv.writer(csvfile_gps, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Current Time', 'Latitude', 'Longitude', 'Number of Satellites'])
            csvfile_gps.close()
        with open ('../storage/rawData.txt', 'w+') as rawData:
            rawData.write("Raw Data:\n____________________"
                          "____________________\n")
            rawData.close()


    # Appends the data to the end of the file
    def save_telemetry_data(self, data):
        file = open("../storage/dataTelemetry.csv", "a+")
        filewriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # NOTE: len(data) should have a length of 5
        if len(data) == 8:  # TODO: Consider scenarios where the input data is different
          
            now = datetime.datetime.now()
            ## This is the current format for saving the telemetry data
            filewriter.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]])
        file.close()

    def save_gps_data(self, data):
        file = open("../storage/dataGps.csv", "a+")
        filewriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 3:
            now = datetime.datetime.now()
            filewriter.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2]])
        file.close()

    def save_raw_data(self, data):
        # TODO: Solve for more edge cases if there are any?
        try:
            if (isinstance(data, (list, tuple))):
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

