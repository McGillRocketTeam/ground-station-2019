from tkinter import *
from array import *


class Plots:
    def __init__(self):
        global window
        window = Tk()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        global canvas
        canvas = Canvas(window, width=screen_width, height=screen_height, bg="black")

        # axis lines
        global yaxis_xloc
        yaxis_xloc = int(screen_width/12)                       # x location of both y axis
        global x_0
        x_0 = int(screen_height/12*7)                   # y location of x axis of upper graph
        xlower_yloc = int(screen_height - screen_height/8)      # y location of x axis of lower graph
        endx = int(screen_width - yaxis_xloc)                   # x location of end of the graph
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

        length = endx - yaxis_xloc;
        time = 20;
        canvas.create_text(screen_width/2, x_0 + 30, fill="white", text="time (s)")

        for x in range(1, length):
            if x % 40 == 0:
                canvas.create_line(x+yaxis_xloc, x_0+4, x+yaxis_xloc, x_0-4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + x_1 + 4, x + yaxis_xloc, x_0 + x_1 - 4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 2*x_1 + 4, x + yaxis_xloc, x_0 + 2*x_1 - 4, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 3*x_1 + 4, x + yaxis_xloc, x_0 + 3*x_1 - 4, fill="white")
                # time axis text
                timeString = self.time_string(time)
                canvas.create_text(x + yaxis_xloc, x_0 + 15, fill="white", text=timeString, tags="times")
                time = time + 20

            if x % 4 == 0:
                canvas.create_line(x+yaxis_xloc, x_0, x+yaxis_xloc, x_0-3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + x_1, x + yaxis_xloc, x_0 + x_1 - 3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 2*x_1, x + yaxis_xloc, x_0 + 2*x_1 - 3, fill="white")
                canvas.create_line(x + yaxis_xloc, x_0 + 3*x_1, x + yaxis_xloc, x_0+ 3*x_1 - 3, fill="white")

        canvas.create_line(yaxis_xloc, xlower_yloc, endx, xlower_yloc, fill="white")        # lower graph x axis
        canvas.create_line(yaxis_xloc, maxY_upper, yaxis_xloc, x_0, fill="white")   # y axis upper graph
        canvas.create_line(yaxis_xloc, maxY_lower, yaxis_xloc, xlower_yloc, fill="white")   # y axis lower graph

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

        time = int(yaxis_xloc - data[0])
        temp = int(x_0 - data[1])
        alt = int(x_1 - data[2])
        vel = int(x_2 - data[3])
        acc = int(x_3 - data[4])

        # save values to array so that the points can be coloured over and moved
        # need to be able to keep track of the corresponding time value (unless its a value for every second
        # or some other constant number)


        # plot if time is less than original time scale
        if data[0] < 533:
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

