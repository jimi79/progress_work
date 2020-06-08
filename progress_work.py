#!/usr/bin/python3

import shutil
import datetime
import time
import signal
import sys
import math

#def get_center(display_settings):
#    a = shutil.get_terminal_size()
#    c = a.columns
#    l = a.lines
ALIGN_LEFT = 0
ALIGN_RIGHT = 1
ALIGN_CENTER = 2

def newtime(hours, minutes = 0):
    return datetime.datetime(2000, 1, 1, hours, minutes)

class Zone:
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
 
class Clock: 
    def __init__(self, zones):
        self.zones = zones

    def effective_time(self, current_time):
        past = datetime.timedelta(0)
        total = datetime.timedelta(0)
        for zone in self.zones:
            total = total + (zone.end - zone.begin)
            if current_time > zone.begin:
                if current_time >= zone.end:
                    past = past + (zone.end - zone.begin)
                else:
                    past = past + (current_time - zone.begin)
        return past.total_seconds() / total.total_seconds()

    def self_tests(self):
        zones = []
        zones.append(Zone(self.newtime(8,0), self.newtime(9, 0)))
        assert(effective_time(zones, self.newtime(8, 0)) == 0)
        assert(effective_time(zones, self.newtime(9, 0)) == 60 * 60)
        assert(effective_time(zones, self.newtime(8, 30)) == 30 * 60)
        assert(effective_time(zones, self.newtime(8, 30)) == 30 * 60)
        zones.append(Zone(self.newtime(10, 0), self.newtime(11, 30)))
        assert(effective_time(zones, self.newtime(9, 0)) == 60 * 60)
        assert(effective_time(zones, self.newtime(10, 0)) == 60 * 60)
        assert(effective_time(zones, self.newtime(11, 0)) == 2 * 60 * 60)
        assert(effective_time(zones, self.newtime(11, 30)) == 2 * 60 * 60 + 30)

    def tests(self):
        zones = [Zone(self.newtime(8, 40), self.newtime(12)), Zone(self.newtime(13, 30), self.newtime(17, 10))]
        for hour in range(8, 19):
            print("time is %dh, duration is %d minutes" % (hour, effective_time(zones, self.newtime(hour)) / 60))

    def get_line(self, value):
        width = self.width
        width = width - 2 # from 1 to col count
        filled = int(width * value)
        line = "["
        for i in range(0, filled):
            line = line + "#"
        for i in range(filled, width):
            line = line + "."
        line = line + "]"
        return line

    def get_width(self):
         term = shutil.get_terminal_size()
         return term.columns 

    def clear_screen(self):
        print("\033[2J", end = "") 
        print("\033[1;1H", end = "") 

    def get_position(self, text, x, align):
        position = math.ceil(x * (self.width - 3)) # from 0 to col count - 1
        if align == ALIGN_CENTER:
            position = position - len(text) / 2 + 1
        if align == ALIGN_RIGHT:
            position = position - len(text) + 1
        position = position + 2 # because of the [ at the beginning, and because it starts at 1
        return position

    def format(self, time):
        return "%02d:%02d" % (time.hour, time.minute)

    def print_zone(self, zone): 
        value_begin = self.effective_time(zone.begin)
        value_end = self.effective_time(zone.end)
        text = "|%s" % self.format(zone.begin)
        position = self.get_position(text, value_begin, ALIGN_LEFT)
        print("\033[%dG" % position, end = "") 
        print(text, end = "")
        text = "%s|" % self.format(zone.end)
        position = self.get_position(text, value_end, ALIGN_RIGHT)
        print("\033[%dG" % position, end = "") 
        print(text)
 
    def print_zones(self):
        for zone in self.zones:
            self.print_zone(zone) 
    
    def init_screen(self):
        self.clear_screen()
        self.print_zones()
        
    def print_line(self, value):
        # clear the line, print the bar, then put the cursor on the beginning of the line, for the next bar to be printed 
        print("\033[0K", end = "")
        print("\033[1G", end = "")
        print(self.get_line(value), end = "")
        print("\033[1G", end = "")

    def run(self):
        print("\033[?25l", end = '') # remove cursor
        #self.print_zones()
        signal.signal(signal.SIGINT, signal_handler) 
        self.width = self.get_width()
        self.width = self.width
        self.init_screen()
        while True:
            new_width = self.get_width()
            if self.width != new_width:
                self.width = new_width
                self.init_screen()

            now = datetime.datetime.now() 
            self.print_line(self.effective_time(newtime(now.hour, now.minute))) 
            sys.stdout.flush()
            time.sleep(1)
        end()

def end(): 
    print("\033[?25h", end = "")
    print() # add a carriage return
    sys.exit(0)

def signal_handler(signal, frame):
    end()

#self_tests()
zones = [Zone(newtime(8, 40), newtime(12)), Zone(newtime(13, 30), newtime(17, 10))]
#zones = []
#zones.append(Zone(newtime(8, 40), newtime(10)))
#zones.append(Zone(newtime(10, 10), newtime(12, 00)))
#zones.append(Zone(newtime(13, 30), newtime(16, 00)))
#zones.append(Zone(newtime(16, 10), newtime(17, 10)))


Clock(zones).run()
