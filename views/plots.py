import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style, animation
import tkinter as tk
import matplotlib.pyplot as plt

import utm

LARGE_FONT = ("VERDANA", 12)
style.use("ggplot")

f = plt.figure()    # Add all plots to main window
a = plt.subplot2grid((4, 2), (0, 0))
a.set_facecolor('black')
b = plt.subplot2grid((4, 2), (1, 0))
b.set_facecolor('black')
c = plt.subplot2grid((4, 2), (2, 0))
c.set_facecolor('black')
d = plt.subplot2grid((4, 2), (3, 0))
d.set_facecolor('black')
e = plt.subplot2grid((4, 2), (0, 1), colspan=2, rowspan=4)
e.set_facecolor('black')

matplotlib.rcParams['lines.linewidth'] = 3


class Plots(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "MRT GUI")

        # TODO Make sure 'zoomed' state works on all laptops
        self.state('zoomed')  # Make fullscreen by default

        container = tk.Frame(self, bg='blue')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        frame = GraphPage(container)
        self.page = GraphPage
        frame.configure(background='black')
        self.frame = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame()  # Display frame on window

    def show_frame(self):
        frame = self.frame
        frame.tkraise()

    def refresh(self):
        self.page.canvas.draw()

    def plot_telemetry_data(self):
        # TODO Add exception handling for opening the file
        file = open("../storage/dataTelemetry.csv", "r")  # Open data file for plotting
        pull_data = file.read()
        data_list = pull_data.split('\n')
        time_list = []
        temperature_list = []
        altitude_list = []
        velocity_list = []
        acceleration_list = []

        first_line = True
        for eachLine in data_list:
            if first_line:
                first_line = False  # Don't read data if first line, since it is the header
            elif len(eachLine) > 1:
                currTime, time, temperature, altitude, velocity, acceleration = eachLine.split(',')  # Split each line by comma
                time_list.append(float(time))  # Add each value to proper list
                temperature_list.append(float(temperature))
                altitude_list.append(float(altitude))
                velocity_list.append(float(velocity))
                acceleration_list.append(float(acceleration))
        file.close()

        a.clear()
        a.plot(time_list, temperature_list)  # Graph temperature
        a.set_ylabel('Temperature(Celcius)')

        b.clear()
        b.plot(time_list, altitude_list)  # Graph altitude
        b.set_ylabel('Altitude(m)')

        c.clear()
        c.plot(time_list, velocity_list)  # Graph velocity
        c.set_ylabel('Velocity(m/s)')

        d.clear()
        d.plot(time_list, acceleration_list)  # Graph acceleration
        d.set_xlabel('Time(s)')
        d.set_ylabel('Acceleration(m/s^2)')

    def plot_gps_data(self):
        file = open("../storage/dataGps.csv", "r")  # Open data file for plotting
        pull_data = file.read()
        data_list = pull_data.split('\n')
        latitude_list = []
        longitude_list = []

        first_line = True
        for eachLine in data_list:
            if first_line:
                first_line = False  # Don't read data if first line, since it is the header
            elif len(eachLine) > 1:
                time, latitude, longitude, num_satelites = eachLine.split(',')  # Split each line by comma
                utm_coordinates = utm.from_latlon(float(latitude), float(longitude))
                latitude_list.append(utm_coordinates[0])  # Add each value to proper list
                longitude_list.append(utm_coordinates[1])
        file.close()

        # e.clear()
        #e.plot(longitude_list, latitude_list)
        e.scatter(longitude_list, latitude_list)
        e.set_xlabel('Longitude')
        e.set_ylabel('Latitude')


class GraphPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, bg='red', text="McGill Rocket Team Ground Station", font=LARGE_FONT, width=400)

        label.pack(pady=10, padx=10)

        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


"""
The following could be useful if we decided to use multiple pages in the application
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Visit Page 1",
                            command=lambda: controller.show_frame(PageOne))
        button.pack()

        button2 = ttk.Button(self, text="Visit Page 2",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()

        button3 = ttk.Button(self, text="Graph Page",
                             command=lambda: controller.show_frame(PageThree))
        button3.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page Two",
                             command=lambda: controller.show_frame(PageTwo))
        button2.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two!!!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = ttk.Button(self, text="Back to Home",
                             command=lambda: controller.show_frame(StartPage))
        button1.pack()

        button2 = ttk.Button(self, text="Page One",
                             command=lambda: controller.show_frame(PageOne))
        button2.pack()
"""
"""
        canvas = Canvas(window, width=screen_width, height=screen_height, bg="black")

        # axis lines
        global yaxis_xloc
        yaxis_xloc = int(screen_width/12)                       # x location of both y axis
        global x_0
        x_0 = int(screen_height/12*7)                   # y location of x axis of upper graph
        xlower_yloc = int(screen_height - screen_height/8)      # y location of x axis of lower graph
        endx = int((screen_width - yaxis_xloc) / 2)                   # x location of end of the graph
        maxY_upper = int(screen_height/12)                      # y location of max height for upper
        maxY_lower = int(screen_height/12*8)                    # y location of max height for lower
        global x_1
        global x_2
        global x_3
        x_1 = (maxY_upper - x_0) / 4
        x_2 = 2*x_1 + x_0
        x_3 = 3*x_1+ x_0
        x_1 = x_1 + x_0

        canvas.create_line(yaxis_xloc, x_0, endx, x_0, fill="white")   # upper graph x axis 1
        canvas.create_line(yaxis_xloc, x_1, endx, x_1, fill="white")   # upper graph x axis 2
        canvas.create_line(yaxis_xloc, x_2, endx, x_2, fill="white")   # upper graph x axis 3
        canvas.create_line(yaxis_xloc, x_3, endx, x_3, fill="white")   # upper graph x axis 4

        # axis ticks are every 2s

        length = endx - yaxis_xloc
        time = 40
        canvas.create_text(screen_width/4, x_0 + 30, fill="white", text="time (s)")

        for x in range(1, length):
            if x % 40 == 0:
                canvas.create_line(x+yaxis_xloc, x_0+4, x+yaxis_xloc, x_0-4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + x_1 + 4, x + yaxis_xloc, x_0 + x_1 - 4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 2*x_1 + 4, x + yaxis_xloc, x_0 + 2*x_1 - 4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 3*x_1 + 4, x + yaxis_xloc, x_0 + 3*x_1 - 4, fill="white")
                # time axis text
                timeString = self.time_string(time)
                canvas.create_text(x + yaxis_xloc, x_0 + 15, fill="white", text=timeString, tags="times")
                time = time + 40

            if x % 4 == 0:
                canvas.create_line(x+yaxis_xloc, x_0, x+yaxis_xloc, x_0-3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + x_1, x + yaxis_xloc, x_0 + x_1 - 3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 2*x_1, x + yaxis_xloc, x_0 + 2*x_1 - 3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 3*x_1, x + yaxis_xloc, x_0+ 3*x_1 - 3, fill="white")

        canvas.create_line(yaxis_xloc, maxY_upper, yaxis_xloc, x_0, fill="white")   # y axis upper graph

        # Temperature, Altitude, Velocity, Acceleration vs time plot
        height_each = (x_0 - maxY_upper)/24
        y = x_0
        text = x_0 - height_each/2
        while y > maxY_upper:
            y = y - height_each
            canvas.create_line(yaxis_xloc, y, yaxis_xloc + 4, y, fill="white")

            text = text - height_each
        #plot labels
        canvas.create_text(yaxis_xloc/2, x_0 - 6*height_each/2, fill="red", text="Temperature")
        canvas.create_text(yaxis_xloc/2, x_0 - 6*height_each/2 + 15, fill="red", text="(C)")
        canvas.create_text(yaxis_xloc/2, x_0 - 18*height_each/2, fill="yellow", text="Altitude (km)")
        canvas.create_text(yaxis_xloc / 2, x_0 - 30*height_each/2, fill="green", text="Velocity (m/s)")
        canvas.create_text(yaxis_xloc / 2, x_0 - 42*height_each/2, fill="blue", text="Acceleration")
        canvas.create_text(yaxis_xloc / 2, x_0 - 42 * height_each / 2 + 15, fill="blue", text="(m/s^2)")

        # Latitude vs Longitude plot
        # Bottom plot
        # NEED RANGE ESTIMATES

        startX = endx + 100  # Start of gps graph is ~ end of telemetry graph

        canvas.create_line(startX, xlower_yloc, screen_width - 75, xlower_yloc, fill="white")        # lower graph x axis
        canvas.create_line(startX, maxY_lower, startX, screen_height, fill="white")   # y axis lower graph


        # y axis
        for y in range(0, xlower_yloc - maxY_lower):
            if y % 4 == 0:
                canvas.create_line(yaxis_xloc, xlower_yloc - y, yaxis_xloc + 3, xlower_yloc - y, fill="white")

            if y % 40 == 0:
                canvas.create_line(yaxis_xloc, xlower_yloc - y, yaxis_xloc + 5, xlower_yloc - y, fill="white")

        # x axis
        for x in range(0, endx - yaxis_xloc):
            if x % 4 == 0:
                canvas.create_line(yaxis_xloc + x, xlower_yloc, yaxis_xloc + x, xlower_yloc - 3, fill="white")

            if x % 40 == 0:
                canvas.create_line(yaxis_xloc + x, xlower_yloc + 4, yaxis_xloc + x, xlower_yloc - 4, fill="white")


        canvas.pack()
        window.update()

    # time string return the time in a x:xx format
    def time_string(self, time):
        second = time % 60
        time_string = str(int((time - second)/60))
        time_string = time_string + ':'
        time_string = time_string + str(second)
        return time_string

    def plotLatLong(self, data):
        # draw points
        # need scale

        canvas.pack()
        window.update()

    def plotTelemetryData(self, data):
        # ASSUMES DATA IS AN ARRAY [TIME, TEMP,ALTITUDE, VELOCITY, ACCELERATION]
        # these need to be scaled based on the ranges of the y axis
        # auto range could be done but all points would have to be redrawn every time the range
        # changes which might be time consuming
        print(data)
        time = int(yaxis_xloc + float(data[0]))
        temp = int(x_0 - float(data[1]))
        alt = int(x_1 - float(data[2]))
        vel = int(x_2 - float(data[3]))
        acc = int(x_3 - float(data[4]))

        # save values to array so that the points can be coloured over and moved
        # need to be able to keep track of the corresponding time value (unless its a value for every second
        # or some other constant number)


        # plot if time is less than original time scale
        if float(data[0]) < 600:
            # each point is 1x1, might want to increase the distance
            # between axis ticks if the points are not to be touching
            # temp, alt, vel, acc  need to be scaled based on the range for each
            canvas.create_oval(time, temp, time + 1, temp + 1, fill="red", tags="data")
            canvas.create_oval(time, alt, time + 1, alt + 1, fill="yellow", tags="data")
            canvas.create_oval(time, vel, time + 1, vel + 1, fill="green", tags="data")
            canvas.create_oval(time, acc, time + 1, acc + 1, fill="blue", tags="data")

        # plot if time is greater
        else:
            pass
            # canvas.delete("times")
            # canvas.delete("data")
            # ^ will delete the times and dots so they can be reprinted
            # could you canvas.move("times", dx, dy) to move them across screen
            # could also draw over the dots with black dots

        canvas.pack()
        window.update()

        # time2 = self.time_string(time)
        # ^ call to make the time a string x:xx format
        """
