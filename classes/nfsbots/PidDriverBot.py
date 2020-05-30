import classes.keyboardEmu as kbe
import threading
import time
import numpy as np


class PidDriverBot(object):
    """Бот-водитель для NFS: Shift, версия, работающая по принципу PID-регулятора"""

    def __init__(self):
        self.do_run = True
        self.radius_prev = 0
        self.integral = 0
        self.angle_prev = 0

        self.threads = {}

        self.threads['wheel'] = threading.Thread(target=self.run_wheel)
        self.threads['wheel'].start()

        self.threads['speed'] = threading.Thread(target=self.run_speed)
        self.threads['speed'].start()

    def __del__(self):
        self.do_run = False
        time.sleep(0.1)
        self.threads['wheel'].join()
        self.threads['speed'].join()
        print("The object is destroyed")

    def get_data(self, get_data=None) -> {'x': float, 'y': float}:
        if get_data is not None:
            self.get_data = get_data
        return {'x': None, 'y': None}


    def can_drive(self, can_drive=None):
        if can_drive is not None:
            self.can_drive = can_drive
        return False

    def get_multiplexors(self, get_multiplexors=None) -> dict:
        if get_multiplexors is not None:
            self.get_multiplexors = get_multiplexors
        return {'linear': 0.0, 'integral': 0.0, 'diff': 0.0}


    def run_speed(self):
        while self.do_run:
            if self.can_drive():
                radius = self.get_data()['y']
                if radius is None:
                    continue

                gas = 0.15
                sleep = gas
                if np.absolute(radius-self.radius_prev) > np.absolute(self.radius_prev)*0.10:
                    kbe.keyPress(kbe.SC_DOWN, sleep)
                elif np.absolute(radius-self.radius_prev) > np.absolute(self.radius_prev)*0.05:
                    kbe.keyPress(kbe.SC_UP, gas*1.5)
                else:
                    kbe.keyPress(kbe.SC_UP, gas)

                time.sleep(sleep)
                self.radius_prev = radius

    def run_wheel(self):
        while self.do_run:
            if self.can_drive():
                angle = self.get_data()['x']
                if angle is None:
                    continue

                base = 0.000005
                multiplexors = self.get_multiplexors()
                koeff = {
                    'linear': base * multiplexors['linear'],
                    'integral': base * multiplexors['integral'],
                    'diff': base * multiplexors['diff']
                }

                self.integral = koeff['integral'] * angle + self.integral
                differential = koeff['diff'] * (angle - self.angle_prev)
                self.angle_prev = angle
                interval = koeff['linear'] * angle + self.integral + differential

                # if -10 < angle < -10:
                #    continue
                # print(interval)

                if interval > 0:
                    kbe.keyPress(kbe.SC_LEFT, interval)
                elif interval < 0:
                    kbe.keyPress(kbe.SC_RIGHT, -interval)
