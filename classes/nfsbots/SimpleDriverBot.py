import classes.keyboardEmu as kbe
import threading


class SimpleDriverBot(object):
    """Бот-водитель для NFS: Shift, простейшая версия, работающая только по величине угла отклонения от нормали"""

    def __init__(self, get_data=lambda x: None):
        self.get_data = get_data
        self.do_run = True

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def can_drive(self, outer=None):
        if outer is not None:
            self.can_drive = outer
        return lambda: False

    def run(self):
        while self.do_run:
            if self.can_drive():
                angle = self.get_data()
                if angle is None:
                    continue
                elif angle > 45:
                    kbe.keyPress(kbe.SC_LEFT)
                    kbe.keyPress(kbe.SC_DOWN, 0.2)
                elif angle > 25:
                    kbe.keyPress(kbe.SC_LEFT)
                    kbe.keyPress(kbe.SC_DOWN, 0.1)
                elif angle > 15:
                    kbe.keyPress(kbe.SC_LEFT)
                elif angle > 5:
                    kbe.keyPress(kbe.SC_LEFT)
                    kbe.keyPress(kbe.SC_UP, 0.1)
                elif angle < -45:
                    kbe.keyPress(kbe.SC_RIGHT)
                    kbe.keyPress(kbe.SC_DOWN, 0.2)
                elif angle < -25:
                    kbe.keyPress(kbe.SC_RIGHT)
                    kbe.keyPress(kbe.SC_DOWN, 0.1)
                elif angle < -15:
                    kbe.keyPress(kbe.SC_RIGHT)
                elif angle < -5:
                    kbe.keyPress(kbe.SC_RIGHT)
                    kbe.keyPress(kbe.SC_UP, 0.1)
                else:
                    kbe.keyPress(kbe.SC_UP, 0.1)

                kbe.keyPress(kbe.SC_UP, 0.1)
