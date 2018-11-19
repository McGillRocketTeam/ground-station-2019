import serial
from model import datastorage
import model.datastorage as DataStorage
import views.plots as Plots
from random import randint


class Parser:
    def __init__(self, datastorage, plots):
        """
        self.port = "COM2"
        self.baud = 9600
        self.byte = serial.EIGHTBITS
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = 1  # sec
        ser = serial.Serial(self.port, self.baud, self.byte, self.parity, self.stopbits)
        self.ser = ser
        if not ser.isOpen():
            ser.open()
        else:
        """
        # print('com5 is open', ser.isOpen())
        while True:
            # telemetry_data = ser.read(1000)
            telemetry_data = [str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100)), str(randint(0, 100))]
            result = self.parse(telemetry_data)
            if result == 200:
                # Save data to file
                datastorage.save_telemetry_data(telemetry_data)
                # Save gps data as well!
                # Display data (asynchronously)
                plots.plotTelemetryData(telemetry_data)
            else:
                # TODO: log errors
                pass

    def parse(self, data):
        status = 500  # error codes or correlation id
        print(len(data))
        if len(data) == 5:  # TODO: implement parsing logic here
            return 200
        return status


def main():
    datastorage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(datastorage, plots)


if __name__ == "__main__":
    main()
