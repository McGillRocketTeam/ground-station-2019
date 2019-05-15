import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QGridLayout)
from PyQt5.QtGui import QPixmap
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
import qdarkstyle
import utm
import numpy as np

class view(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        """Declare layouts"""
        hbox_Window = QHBoxLayout(self)
        vbox_LogoAndGraphs = QVBoxLayout()

        hbox_Logo = QHBoxLayout()
        hbox_Graphs = QHBoxLayout()
        vbox_inner_Graphs = QVBoxLayout() # vbox for non-position graphs
        vbox_Indicators = QVBoxLayout()

        """Declare widgets"""

        self.altitude_graph = pg.PlotWidget(title='Altitude', left='Height', bottom='Time', right='')
        self.temperature_graph = pg.PlotWidget(title='Temperature', left='Temperature', bottom='Time')
        self.velocity_graph = pg.PlotWidget(title='Velocity', left='Velocity', bottom='Time')
        self.acceleration_graph = pg.PlotWidget(title='Acceleration', left='Acceleration', bottom='Time')
        self.position_graph = pg.PlotWidget(title='Position', left='X Coordinate', bottom='Y Coordinate')

        altitude_label = QPushButton('Altitude')
        temperature_label = QLabel('Temperature')
        velocity_label = QLabel('Velocity')
        acceleration_label = QLabel('Acceleration')
        position_label = QLabel('Position')

        MRT_Logo = QPixmap('MRT-logo.png')
        smaller_MRT_Logo = MRT_Logo.scaledToHeight(100)
        logo_Lbl = QLabel(self)
        logo_Lbl.setPixmap(smaller_MRT_Logo)

        """Layout Management"""
        hbox_Logo.addWidget(logo_Lbl)

        vbox_inner_Graphs.addWidget(self.altitude_graph)
        vbox_inner_Graphs.addWidget(self.temperature_graph)
        vbox_inner_Graphs.addWidget(self.velocity_graph)
        vbox_inner_Graphs.addWidget(self.acceleration_graph)
        hbox_Graphs.addLayout(vbox_inner_Graphs)
        hbox_Graphs.addWidget(self.position_graph)

        vbox_Indicators.addWidget(altitude_label)
        vbox_Indicators.addWidget(temperature_label)
        vbox_Indicators.addWidget(velocity_label)
        vbox_Indicators.addWidget(acceleration_label)
        vbox_Indicators.addWidget(position_label)


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
        self.setGeometry(300,300,1250,750)
        self.setWindowTitle('MRT Ground Station')
        self.show()

        """ This is a test to show how to plot using signals and slots """
        def update():
            test1 = np.random.normal(size=1000)
            test2 = np.random.normal(size=1000)
            self.altitude_graph.plot(test1, test2, pen='r')

        altitude_label.clicked.connect(update)



    def plot_telemetry_data(self, telemetry_data):
        """ Append telemetry data to lists """
        # self.time_list.append(float(telemetry_data[3]))
        # self.temperature_list.append(float(telemetry_data[4]))
        # self.altitude_list.append(float(telemetry_data[2]))
        # self.velocity_list.append(float(telemetry_data[5]))
        # self.acceleration_list.append(float(telemetry_data[6]))

        test1 = np.random.normal(size=1000)
        test2 = np.random.normal(size=1000)

        self.altitude_graph.plot(test1, test2, pen='r')


    def plot_gps_data(self, telemetry_data):
        """ Append GPS data to lists """
        utm_coordinates = utm.from_latlon(float(telemetry_data[0]), float(telemetry_data[1]))  # Convert to UTM coordinates
        self.latitude_list.append(utm_coordinates[0])
        self.longitude_list.append(utm_coordinates[1])
    def update_views(self):
        fun = 0
    #
    # timer = QTimer()
    # timer.timeout.connect(plot_telemetry_data)
    # timer.start(50)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = view()
    sys.exit(app.exec_())
