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

    # Appends the data to the end of the file
    def save_telemetry_data(self, data):
        file = open("../storage/dataTelemetry.csv", "a+")
        filewriter = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        if len(data) == 5:  # TODO: Consider scenarios where the input data is different
            now = datetime.datetime.now()
            filewriter.writerow([now.strftime("%Y-%m-%d %H:%M"), data[0], data[1], data[2], data[3], data[4]])
            # TODO: Possibly reformat the time to include seconds etc...
        file.close()

    # Saves gps data
    def save_gps_data(self, data):
        #TODO: finish
        pass


# For testing purposes only
if __name__ == '__main__':
    storage = DataStorage()
    list1 = ["Time1", "Temp1", "Alt1", "Vel1", "Acc1"]
    listdata = ["2", "20", "30", "40", "78"]
    storage.save_telemetry_data(list1)
    storage.save_telemetry_data(listdata)
