import time
import serial
import os, pty
from random import randint
import random
import re
import datetime
import time
import math
import string
from controller.parser import Parser as parser
import model.datastorage as data_storage
import views.plots as plots
from serial.tools import list_ports


def port_finder():
    full_telemetery = True
    write_to_file = True
    try:
        if full_telemetery:
            os.remove('../storage/serial/full_telemetery.txt')
        else:
            os.remove('../storage/serial/gps_backup.txt')
    except:
        print('file not removed')
    usb_type = 'Full Telemetery' if full_telemetery else 'GPS'
    initial = list_ports.comports()
    i1 = input('Insert usb for {}:'.format(usb_type))
    first_insert = list_ports.comports()
    # i2 = input('Insert usb for {} RSSI'.format(usb_type))
    # second_insert = list_ports.comports()
    port_list = []
    init = []
    fi = []
    # si = []
    for i in range(0, len(first_insert)):
        if i < len(initial):
            init.append(initial[i].device)
        if i < len(first_insert):
            fi.append(first_insert[i].device)
    init.sort()
    fi.sort()
    # si.sort()
    ndi = 'NoDeviceInserted'
    final = ndi
    for j in fi:
        to_append = (j, init.count(j))
        if to_append[1] == 0:
            final = j
        port_list.append(to_append)
    main_port = final
    print(final)
    rssi_port = ''
    port_option = []
    if full_telemetery:
        f = open("../storage/serial/full_telemetery.txt", "w+")
    else:
        f = open("../storage/serial/gps_backup.txt", "w+")
    if write_to_file:
        f.write('{}'.format(main_port))
    f.close()
    # print(port_list)
    # print('{}'.format(main_port))


port_finder()