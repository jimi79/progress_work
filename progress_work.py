#!/usr/bin/python3

import shutil
import datetime
import time
import signal
import sys

#def get_center(display_settings):
#    a = shutil.get_terminal_size()
#    c = a.columns
#    l = a.lines


class Zone:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
 
def effective_time(zones, current_time):
    past = datetime.timedelta(0)
    total = datetime.timedelta(0)
    for zone in zones:
        total = total + (zone.end - zone.begin)
        if current_time > zone.begin:
            if current_time >= zone.end:
                past = past + (zone.end - zone.begin)
            else:
                past = past + (current_time - zone.begin)
    return past.total_seconds() / total.total_seconds()

def newtime(hours, minutes = 0):
    return datetime.datetime(2000, 1, 1, hours, minutes)

def self_tests():
    # not correct anymore
    zones = []
    zones.append(Zone(newtime(8,0), newtime(9, 0)))
    assert(effective_time(zones, newtime(8, 0)) == 0)
    assert(effective_time(zones, newtime(9, 0)) == 60 * 60)
    assert(effective_time(zones, newtime(8, 30)) == 30 * 60)
    assert(effective_time(zones, newtime(8, 30)) == 30 * 60)
    zones.append(Zone(newtime(10, 0), newtime(11, 30)))
    assert(effective_time(zones, newtime(9, 0)) == 60 * 60)
    assert(effective_time(zones, newtime(10, 0)) == 60 * 60)
    assert(effective_time(zones, newtime(11, 0)) == 2 * 60 * 60)
    assert(effective_time(zones, newtime(11, 30)) == 2 * 60 * 60 + 30)

def tests():
    zones = [Zone(newtime(8, 40), newtime(12)), Zone(newtime(13, 30), newtime(17, 10))]
    for hour in range(8, 19):
        print("time is %dh, duration is %d minutes" % (hour, effective_time(zones, newtime(hour)) / 60))

def end(): 
    print("\033[?25h", end = "")
    print() # add a carriage return
    sys.exit(0)

def signal_handler(signal, frame):
    end()

def get_width():
    term = shutil.get_terminal_size()
    return term.columns

def get_line(value):
    width = get_width()
    width = width - 2
    filled = int(width * value)
    line = "["
    for i in range(0, filled):
        line = line + "#"
    for i in range(filled, width):
        line = line + "."
    line = line + "]"
    return line
    

def print_line(value):
    # clear the line, print the bar, then put the cursor on the beginning of the line, for the next bar to be printed 
    print("\033[0k", end = "")
    print("\033[1G", end = "")
    print(get_line(value), end = "")
    print("\033[1G", end = "")

def run():
    zones = [Zone(newtime(8, 40), newtime(12)), Zone(newtime(13, 30), newtime(17, 10))]
    print("\033[?25l", end = '') # remove cursor
    signal.signal(signal.SIGINT, signal_handler) 
    while True:
        now = datetime.datetime.now() 
        print_line(effective_time(zones, newtime(now.hour, now.minute)))
        time.sleep(1)
        sys.stdout.flush()
    end()

#self_tests()
run()
