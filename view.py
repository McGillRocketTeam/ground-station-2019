import sys
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLabel, QGridLayout, QLCDNumber, QLineEdit, QPushButton)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer
import pyqtgraph as pg
import qdarkstyle
import utm
import numpy as np
from controller import parser
from model import datastorage

show_graphs = True  # Show graph toggle option

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
        self.cutoff = 0

        """Optimization settings"""
        self.end_dots = True
        self.graph_update_count = 0
        self.graph_update_interval = 3  # Increase this value to speed up graphing
        self.optimize_fps = True
        self.goal_fps = 30  # Max 60
        self.bounds = 10

        """Latest Telemetry Info"""
        self.lat = 0
        self.long = 0
        self.time = 0
        self.alt = 0
        self.vel = 0
        self.sat = 0
        self.accel = 0
        self.temp = 0
        self.gyro_x = 0

        self.antenna_angle = [0, 0]
        self.antenna_precision = 7
        self.antenna_font_size = 32

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
        self.antenna_angle_label = QLabel()
        # TODO: increase font size
        self.antenna_angle_label.setFont(QFont("Times", self.antenna_font_size, QFont.Bold))
        # self.antenna_angle_label.setFont(QFont=QFont(15))

        self.altitude_graph = pg.PlotWidget(title='Altitude', left='Height', bottom='Time')
        # self.temperature_graph = pg.PlotWidget(title='Temperature', left='Temperature', bottom='Time')
        self.rssi_graph = pg.PlotWidget(title='RSSI', left='RSSI', bottom='Time')
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

        self.text_box = QLineEdit(self)
        self.text_box.setFixedWidth(200)
        self.button = QPushButton('Update Cutoff', self)
        self.button.clicked.connect(self.on_click)
        self.button.setFixedWidth(150)
        self.button_reset = QPushButton('RESET DATA', self)
        self.button_reset.clicked.connect(self.on_click_reset)
        self.button_reset.setFixedWidth(150)

        self.altitude_LCD = QLCDNumber(self)
        # self.temperature_LCD = QLCDNumber(self)
        self.rssi_LCD = QLCDNumber(self)
        self.velocity_LCD = QLCDNumber(self)
        self.acceleration_LCD = QLCDNumber(self)
        self.positionX_LCD = QLCDNumber(self)
        self.positionY_LCD = QLCDNumber(self)

        self.altitude_LCD.setDigitCount(9)
        # self.temperature_LCD.setDigitCount(9)
        self.rssi_LCD.setDigitCount(4)
        self.velocity_LCD.setDigitCount(9)
        self.acceleration_LCD.setDigitCount(9)
        self.positionX_LCD.setDigitCount(10)
        self.positionY_LCD.setDigitCount(10)

        altitude_label = QLabel("Current Altitude")
        # temperature_label = QLabel("Current Temperature")
        rssi_label = QLabel("RSSI")
        velocity_label = QLabel("Current Velocity")
        acceleration_label = QLabel("Current Acceleration")
        position_label = QLabel("Current Position")

        MRT_Logo = QPixmap('MRT-logo.png')
        smaller_MRT_Logo = MRT_Logo.scaledToHeight(100)
        logo_Lbl = QLabel(self)
        logo_Lbl.setPixmap(smaller_MRT_Logo)

        """Layout Management"""
        hbox_Logo.addWidget(logo_Lbl)
        hbox_Logo.addWidget(self.antenna_angle_label)
        hbox_Logo.addWidget(self.button_reset)
        hbox_Logo.addWidget(self.fps_label)
        hbox_Logo.addWidget(self.text_box)
        hbox_Logo.addWidget(self.button)

        vbox_inner_Graphs.addWidget(self.altitude_graph)
        # vbox_inner_Graphs.addWidget(self.temperature_graph)
        vbox_inner_Graphs.addWidget(self.rssi_graph)
        vbox_inner_Graphs.addWidget(self.velocity_graph)
        vbox_inner_Graphs.addWidget(self.acceleration_graph)
        hbox_Graphs.addLayout(vbox_inner_Graphs)
        hbox_Graphs.addWidget(self.position_graph)

        vbox_Indicators.addWidget(altitude_label)
        vbox_Indicators.addWidget(self.altitude_LCD)
        # vbox_Indicators.addWidget(temperature_label)
        # vbox_Indicators.addWidget(self.temperature_LCD)
        vbox_Indicators.addWidget(rssi_label)
        vbox_Indicators.addWidget(self.rssi_LCD)
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

        self.rssi_list = []

        """Build main window"""
        self.setLayout(hbox_Window)
        self.setGeometry(100, 100, 1720, 968)
        self.setWindowTitle('MRT Ground Station')
        if show_graphs is True:
            self.show()

    @pyqtSlot(list)
    def append_data(self, telemetry_data):
        """
        Append telemetry data to lists

        telemetry long data format: Slat,long,time,alt,vel,sat,acc,temp,gyro_x,RSSI,E\n
        backup GPS data: Slat,long,time,gps_alt,gps_speed,sat,RSSI,E\n
        """
        if len(telemetry_data) == 2:
            self.antenna_angle = telemetry_data
        else:
            try:
                self.lat = float(telemetry_data[0])
                self.long = float(telemetry_data[1])
                self.time = float(telemetry_data[2])
                self.alt = float(telemetry_data[3])
                self.vel = float(telemetry_data[4])
                self.sat = float(telemetry_data[5])
                self.accel = 0
                self.temp = 0
                self.gyro_x = 0
                self.rssi = 0
                if len(telemetry_data) >= 9:
                    self.accel = float(telemetry_data[6])
                    self.temp = float(telemetry_data[7])
                    self.gyro_x = float(telemetry_data[8])
                    if len(telemetry_data) == 10:
                        self.rssi = float(telemetry_data[9])
                        self.rssi_list.append(float(self.rssi))
                elif len(telemetry_data) == 7:
                    self.rssi = float(telemetry_data[6])
                    self.rssi_list.append(float(self.rssi))

                self.time_list.append(float(self.time))
                self.altitude_list.append(float(self.alt))
                self.temperature_list.append(float(self.temp))
                self.velocity_list.append(float(self.vel))
                self.acceleration_list.append(float(self.accel))
            except:
                print('INVALID DATA SENT TO VIEW')



        """ Append GPS data to lists """
        try:
            utm_coordinates = utm.from_latlon(float(self.lat), float(self.long))  # Convert to UTM coordinates

            # self.latitude_list.append(utm_coordinates[0])
            # self.longitude_list.append(utm_coordinates[1])
            self.latitude_list.append(float(self.lat))
            self.longitude_list.append(float(self.long))
        except:
            print("latlong broken")

    @pyqtSlot()
    def plot_data(self):

        try:

            now = pg.ptime.time()
            fps = 1.0 / (now - self.lastUpdate)
            self.lastUpdate = now
            self.avgFps = self.avgFps * 0.8 + fps * 0.2
            self.fps_label.setText("Generating {0:3.2f} fps\nUpdate interval: {1}".format(self.avgFps, self.graph_update_interval))
            # self.fps_label.setText("Generating {0:3.2f} fps".format(self.avgFps))z
            self.antenna_angle_label.setText('XY:{}\nZ:{}'.format(str(self.antenna_angle[0])[0:self.antenna_precision], str(self.antenna_angle[1])[0:self.antenna_precision]))
            if self.graph_update_count > self.graph_update_interval:
                self.graph_update_count = 0
                if self.optimize_fps:
                    if self.avgFps < (self.goal_fps-self.bounds):
                        self.graph_update_interval += 1
                    elif self.avgFps > (self.goal_fps+self.bounds):
                        self.graph_update_interval -= 1


                self.altitude_graph.clear()
                # self.temperature_graph.clear()
                self.rssi_graph.clear()
                self.velocity_graph.clear()
                self.acceleration_graph.clear()
                self.position_graph.clear()

                if len(self.altitude_list) > self.cutoff+1:
                    self.altitude_graph.plot(self.time_list[-self.cutoff:-1], self.altitude_list[-self.cutoff:-1], pen='r')
                    # self.temperature_graph.plot(self.time_list[-self.cutoff:-1], self.temperature_list[-self.cutoff:-1], pen='r')
                    self.velocity_graph.plot(self.time_list[-self.cutoff:-1], self.velocity_list[-self.cutoff:-1], pen='r')
                    self.acceleration_graph.plot(self.time_list[-self.cutoff:-1], self.acceleration_list[-self.cutoff:-1], pen='r')

                    self.position_graph.plot(self.latitude_list[-self.cutoff:-1], self.longitude_list[-self.cutoff:-1])
                    if self.end_dots:
                        self.velocity_graph.plot([self.time], [self.vel], pen=None, symbol='o', symbolBrush=(0, 0, 255), symbolSize=6.5)
                        self.acceleration_graph.plot([self.time], [self.accel], pen=None, symbol='o', symbolBrush=(0, 0, 255), symbolSize=6.5)
                        self.altitude_graph.plot([self.time], [self.alt], pen=None, symbol='o', symbolBrush=(0, 0, 255), symbolSize=6.5)
                    if len(self.time_list) == len(self.rssi_list):
                        self.rssi_graph.plot(self.time_list[-self.cutoff:-1], self.rssi_list[-self.cutoff:-1], pen='r')
                        if self.end_dots:
                            self.rssi_graph.plot([self.time], [self.rssi], pen=None, symbol='o', symbolBrush=(0, 0, 255), symbolSize=6.5)
                    # This line adds an X marking the last gps location
                    self.position_graph.plot([self.lat], [self.long], pen=None, symbol='o', symbolBrush=(255, 0, 0), symbolSize=6.5)
            else:
                self.graph_update_count = self.graph_update_count + 1

            self.altitude_LCD.display(self.alt)
            # self.temperature_LCD.display(self.temp)
            self.rssi_LCD.display(self.rssi)
            self.velocity_LCD.display(self.vel)
            self.acceleration_LCD.display(self.accel)
            self.positionX_LCD.display(self.lat)
            self.positionY_LCD.display(self.long)

            self.timer.start(0)

            # print(len(self.altitude_list))

        except: print("Problem with graphing")

    @pyqtSlot()
    def on_click(self):
        text_value = self.text_box.text()
        try:
            num_value = int(text_value)
            num_value = abs(num_value)
            if num_value < len(self.longitude_list):
                self.cutoff = num_value
            else:
                self.cutoff = 0
        except:
            print('Data limit {} is invalid \nInput a number between 0 and {}'.format(text_value, len(self.longitude_list)))
            self.cutoff = 0

    @pyqtSlot()
    def on_click_reset(self):
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

        self.rssi_list = []


    def update_plots(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = view()
    sys.exit(app.exec_())
