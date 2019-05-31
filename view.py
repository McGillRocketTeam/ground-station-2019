import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QGridLayout, QLCDNumber)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer
import pyqtgraph as pg
import qdarkstyle
import utm
import numpy as np
from controller import parser
from model import datastorage

class view(QWidget):

    def __init__(self):
        super().__init__()


        self.data_storage = datastorage.DataStorage()
        self.parser = parser.Parser(self.data_storage)
        self.thread = QThread()

        self.parser.dataChanged.connect(self.append_data)
        self.parser.moveToThread(self.thread)

        self.thread.started.connect(self.parser.parse)
        self.thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.plot_data)
        self.timer.start(100)

        self.lastUpdate = pg.ptime.time()
        self.avgFps = 0.0

        self.initUI()

    def initUI(self):
        pg.setConfigOptions(antialias=False)  ## expensive ass setting for fps but yolo
        """Declare layouts"""
        hbox_Window = QHBoxLayout(self)
        vbox_LogoAndGraphs = QVBoxLayout()

        hbox_Logo = QHBoxLayout()
        hbox_Graphs = QHBoxLayout()
        vbox_inner_Graphs = QVBoxLayout() # vbox for non-position graphs
        vbox_Indicators = QVBoxLayout()
        hbox_position = QHBoxLayout()

        """Declare widgets"""

        self.fps_label = QLabel()

        self.altitude_graph = pg.PlotWidget(title='Altitude', left='Height', bottom='Time')
        self.temperature_graph = pg.PlotWidget(title='Temperature', left='Temperature', bottom='Time')
        self.velocity_graph = pg.PlotWidget(title='Velocity', left='Velocity', bottom='Time')
        self.acceleration_graph = pg.PlotWidget(title='Acceleration', left='Acceleration', bottom='Time')
        self.position_graph = pg.PlotWidget(title='Position', left='Y Coordinate', bottom='X Coordinate')

        # self.altitude_graph.setClipToView(True) # OPTIMIZATION OPTIONS
        # self.altitude_graph.setDownsampling(mode='peak')
        # self.temperature_graph.setClipToView(True)
        # self.temperature_graph.setDownsampling(mode='peak')
        # self.velocity_graph.setClipToView(True)
        # self.velocity_graph.setDownsampling(mode='peak')
        # self.acceleration_graph.setClipToView(True)
        # self.acceleration_graph.setDownsampling(mode='peak')
        # self.position_graph.setClipToView(True)
        # self.position_graph.setDownsampling(mode='peak')
        # self.altitude_graph.setRange(xRange=[0, 10])
        # self.altitude_graph.setLimits(xMax=100)

        self.altitude_LCD = QLCDNumber(self)
        self.temperature_LCD = QLCDNumber(self)
        self.velocity_LCD = QLCDNumber(self)
        self.acceleration_LCD = QLCDNumber(self)
        self.positionX_LCD = QLCDNumber(self)
        self.positionY_LCD = QLCDNumber(self)

        self.altitude_LCD.setDigitCount(6)
        self.temperature_LCD.setDigitCount(6)
        self.velocity_LCD.setDigitCount(6)
        self.acceleration_LCD.setDigitCount(6)
        self.positionX_LCD.setDigitCount(8)
        self.positionY_LCD.setDigitCount(8)

        altitude_label = QLabel("Current Altitude")
        temperature_label = QLabel("Current Temperature")
        velocity_label = QLabel("Current Velocity")
        acceleration_label = QLabel("Current Acceleration")
        position_label = QLabel("Current Position")


        MRT_Logo = QPixmap('MRT-logo.png')
        smaller_MRT_Logo = MRT_Logo.scaledToHeight(100)
        logo_Lbl = QLabel(self)
        logo_Lbl.setPixmap(smaller_MRT_Logo)

        """Layout Management"""
        hbox_Logo.addWidget(logo_Lbl)
        hbox_Logo.addWidget(self.fps_label)

        vbox_inner_Graphs.addWidget(self.altitude_graph)
        vbox_inner_Graphs.addWidget(self.temperature_graph)
        vbox_inner_Graphs.addWidget(self.velocity_graph)
        vbox_inner_Graphs.addWidget(self.acceleration_graph)
        hbox_Graphs.addLayout(vbox_inner_Graphs)
        hbox_Graphs.addWidget(self.position_graph)

        vbox_Indicators.addWidget(altitude_label)
        vbox_Indicators.addWidget(self.altitude_LCD)
        vbox_Indicators.addWidget(temperature_label)
        vbox_Indicators.addWidget(self.temperature_LCD)
        vbox_Indicators.addWidget(velocity_label)
        vbox_Indicators.addWidget(self.velocity_LCD)
        vbox_Indicators.addWidget(acceleration_label)
        vbox_Indicators.addWidget(self.acceleration_LCD)
        vbox_Indicators.addWidget(position_label)
        hbox_position.addWidget(self.positionX_LCD)
        hbox_position.addWidget(self.positionY_LCD)
        vbox_Indicators.addLayout(hbox_position)



        vbox_LogoAndGraphs.addLayout(hbox_Logo)
        vbox_LogoAndGraphs.addLayout(hbox_Graphs)
        hbox_Window.addLayout(vbox_LogoAndGraphs)
        hbox_Window.addLayout(vbox_Indicators)



        """ Telemetry values """
        self.time_list = []
        self.temperature_list = []
        self.altitude_list = []
        self.velocity_list = []
        self.acceleration_list = []

        """ GPS values """
        self.latitude_list = []
        self.longitude_list = []

        """ Redundancy GPS values """
        self.redundancy_latitude_list = []
        self.redundancy_longitude_list = []

        """Build main window"""
        self.setLayout(hbox_Window)
        self.setGeometry(100,100,1720,968)
        self.setWindowTitle('MRT Ground Station')
        self.show()


    @pyqtSlot(list)
    def append_data(self, telemetry_data):
        """
        Append telemetry data to lists

        telemetry long data format: Slat,long,time,alt,vel,sat,acc,temp,gyro_x,RSSI,E\n
        backup GPS data: Slat,long,time,gps_alt,gps_speed,sat,RSSI,E\n
        """
        self.time_list.append(float(telemetry_data[3]))
        self.altitude_list.append(float(telemetry_data[2]))
        self.temperature_list.append(float(telemetry_data[4]))
        self.velocity_list.append(float(telemetry_data[5]))
        self.acceleration_list.append(float(telemetry_data[6]))

        """ Append GPS data to lists """
        try:
            utm_coordinates = utm.from_latlon(float(telemetry_data[0]), float(telemetry_data[1]))  # Convert to UTM coordinates

            self.latitude_list.append(utm_coordinates[0])
            self.longitude_list.append(utm_coordinates[1])
        except:
            print("latlong broken")

    @pyqtSlot()
    def plot_data(self):

        now = pg.ptime.time()
        fps = 1.0 / (now - self.lastUpdate)
        self.lastUpdate = now
        self.avgFps = self.avgFps * 0.8 + fps * 0.2
        self.fps_label.setText("Generating %0.2f fps" % self.avgFps)

        self.altitude_graph.clear()
        self.temperature_graph.clear()
        self.velocity_graph.clear()
        self.acceleration_graph.clear()
        self.position_graph.clear()

        self.altitude_graph.plot(self.time_list, self.altitude_list, pen='r')
        self.temperature_graph.plot(self.time_list, self.temperature_list, pen='r')
        self.velocity_graph.plot(self.time_list, self.velocity_list, pen='r')
        self.acceleration_graph.plot(self.time_list, self.acceleration_list, pen='r')
        self.position_graph.plot(self.latitude_list, self.longitude_list)

        self.altitude_LCD.display(self.altitude_list[-1])
        self.temperature_LCD.display(self.temperature_list[-1])
        self.velocity_LCD.display(self.velocity_list[-1])
        self.acceleration_LCD.display(self.acceleration_list[-1])
        self.positionX_LCD.display(self.latitude_list[-1])
        self.positionY_LCD.display(self.longitude_list[-1])
        self.timer.start(0)

        print(len(self.altitude_list))

    def update_plots(self):
        pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = view()
    sys.exit(app.exec_())
