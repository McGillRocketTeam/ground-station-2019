import serial


class Parser:
    def __init__(self):
        self.port = "COM5"
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
            print('com5 is open', ser.isOpen())
            while True:
                data=ser.read(1000)
                result = self.parse(data)
                if result == 200:
                    #TODO: display data (asynchronously)
                    pass
                else:
                    #TODO: log errors
                    pass

    def parse(self, data):
        status = 500 #error codes or correlation id
        print(len(data))
        if len(data) == 1000: #TODO: implement parsing logic here
            return 200
        return status


def main():
    parser = Parser()

if __name__ == "__main__":
    main()
