import serial
import model.datastorage as DataStorage
import views.plots as Plots


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
            # data = ser.read(1000)
            data = ['1', '3']
            result = self.parse(data)
            if result == 200:
                # Save data to file
                datastorage.save(data)
                # Display data (asynchronously)
                plots.plotTelemetryData(data)
            else:
                # TODO: log errors
                pass

    def parse(self, data):
        status = 500  # error codes or correlation id
        print(len(data))
        if len(data) == 2:  # TODO: implement parsing logic here
            return 200
        return status


def main():
    datastorage = DataStorage.DataStorage()
    plots = Plots.Plots()
    parser = Parser(datastorage, plots)


if __name__ == "__main__":
    main()
