from serial import Serial
from threading import Thread
import subprocess
import time

VALUE_TRESHOLD = 5.0
TIME_TRESHOLD = 5.0
class Camera(object):
    def __init__(self, port, logger):
        self.port = port
        self.log = logger
        self.reader = None
        self.read_thread = None

    def open_port(self, baudrate=9600, timeout=2):
        return Serial(self.port, baudrate=baudrate, timeout=timeout)

    def start_reader(self):
        self.reader = self.open_port()
        if self.reader.is_open == False:
            return False
        self.read_thread = ReadThread(self.reader, self.log)
        self.read_thread.start()
        return True

    def stop_reader(self):
        self.read_thread.stop()
        self.read_thread.join()
        self.reader.close()

class ReadThread(Thread):
    def __init__(self, reader, log):
        Thread.__init__(self)
        self.reader = reader
        self.log = log
        self.running = False
        self.last_num = None
        self.pic_time = 0.0

    def run(self):
        self.reader.flush()
        self.running = True
        while self.running == True:
            if self.reader.inWaiting() > 0:
                line = self.reader.readline().decode('utf-8').rstrip()
                self.log.info(line)
                try:
                    self.process(float(line))
                except ValueError:
                    pass
            time.sleep(0.01)

    def process(self, num):
        if self.last_num:
            now = time.time()
            if abs(self.last_num - num) > VALUE_TRESHOLD and now - self.pic_time > TIME_TRESHOLD:
                self.take_picture()
                self.pic_time = now
        self.last_num = num

    def take_picture(self):
        proc_out = subprocess.getoutput(['fswebcam', 'pic_1.jpg'])
        if proc_out.find('Captured frame') > 0:
            self.log.info('New frame captured')
        else:
            self.log.warn('Failed to capture frame')

    def stop(self):
        self.running = False