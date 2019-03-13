import tkinter as tk
import matplotlib.pyplot as plt
import utm
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import style

""" Styles """
LARGE_FONT = ("VERDANA", 12)
style.use("ggplot")
matplotlib.use("TkAgg")
plots = plt.figure()


class Plots(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "MRT GUI")

        """ Set up plots """
        global plots

        self.temperature_graph = plt.subplot2grid((4, 2), (0, 0))
        self.temperature_graph.set_facecolor('black')

        self.altitude_graph = plt.subplot2grid((4, 2), (1, 0))
        self.altitude_graph.set_facecolor('black')

        self.velocity_graph = plt.subplot2grid((4, 2), (2, 0))
        self.velocity_graph.set_facecolor('black')

        self.acceleration_graph = plt.subplot2grid((4, 2), (3, 0))
        self.acceleration_graph.set_facecolor('black')

        self.gps_graph = plt.subplot2grid((4, 2), (0, 1), colspan=2, rowspan=4)
        self.gps_graph.set_facecolor('black')

        matplotlib.rcParams['lines.linewidth'] = 3

        """ Telemetry values """
        self.time_list = []
        self.temperature_list = []
        self.altitude_list = []
        self.velocity_list = []
        self.acceleration_list = []

        """ GPS values """
        self.latitude_list = []
        self.longitude_list = []

        """ Build main frame"""
        self.state('zoomed')  # Make fullscreen by default

        container = tk.Frame(self, bg='blue')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frame = GraphPage(container)
        self.page = GraphPage
        self.frame.configure(background='black')
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame()  # Display frame on window

        """ Antenna calculations angle label """
        self.antennaAngle = tk.Label(self, text='ANTENNA ANGLE: 0 (xy), 0 (z)')
        self.antennaAngle.config(font=("Courier", 25))
        self.antennaAngle.pack(pady=10, padx=10)

        """ Reset graph functions """
        def reset_telemetry_graphs():
            self.time_list.clear()
            self.temperature_list.clear()
            self.altitude_list.clear()
            self.velocity_list.clear()
            self.acceleration_list.clear()

        def reset_gps_graphs():
            self.gps_graph.clear()
            self.latitude_list.clear()
            self.longitude_list.clear()

        """ Reset graph buttons """
        reset_telemetry_button = tk.Button(self, text="RESET TEL", command=reset_telemetry_graphs)
        reset_telemetry_button.pack()
        reset_gps_button = tk.Button(self, text="RESET GPS", command=reset_gps_graphs)
        reset_gps_button.pack()

    def show_frame(self):
        frame = self.frame
        frame.tkraise()

    def plot_telemetry_data(self, telemetry_data):
        """ Append telemetry data to lists """
        self.time_list.append(float(telemetry_data[3]))
        self.temperature_list.append(float(telemetry_data[4]))
        self.altitude_list.append(float(telemetry_data[2]))
        self.velocity_list.append(float(telemetry_data[5]))
        self.acceleration_list.append(float(telemetry_data[6]))

        """ Plot data """
        self.temperature_graph.clear()
        self.temperature_graph.plot(self.time_list, self.temperature_list)  # Graph temperature
        self.temperature_graph.set_ylabel('Temperature(Celcius)')

        self.altitude_graph.clear()
        self.altitude_graph.plot(self.time_list, self.altitude_list)  # Graph altitude
        self.altitude_graph.set_ylabel('Altitude(m)')

        self.velocity_graph.clear()
        self.velocity_graph.plot(self.time_list, self.velocity_list)  # Graph velocity
        self.velocity_graph.set_ylabel('Velocity(m/s)')

        self.acceleration_graph.clear()
        self.acceleration_graph.plot(self.time_list, self.acceleration_list)  # Graph acceleration
        self.acceleration_graph.set_xlabel('Time(s)')
        self.acceleration_graph.set_ylabel('Acceleration(m/s^2)')

    def plot_gps_data(self, telemetry_data):
        """ Append GPS data to lists """
        utm_coordinates = utm.from_latlon(float(telemetry_data[0]), float(telemetry_data[1])) # Convert to UTM coordinates
        self.latitude_list.append(utm_coordinates[0])
        self.longitude_list.append(utm_coordinates[1])

        """ Plot data """
        self.gps_graph.scatter(self.longitude_list, self.latitude_list)
        self.gps_graph.set_xlabel('Longitude')
        self.gps_graph.set_ylabel('Latitude')

    def update_plots(self):
        global plots
        plots.canvas.draw()  # Update plots
        plots.canvas.flush_events()  # Flush the GUI events


class GraphPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        """ Set up Graph Page"""
        label = tk.Label(self, bg='red', text="McGill Rocket Team Ground Station", font=LARGE_FONT, width=400)
        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(plots, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
