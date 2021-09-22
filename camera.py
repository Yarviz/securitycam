from serial import Serial
import logging
from threading import Thread
import time

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

    def run(self):
        self.reader.flush()
        self.running = True
        while self.running == True:
            if self.reader.in_waiting > 0:
                line = self.reader.readline().decode('utf-8').rstrip()
                self.log.info(line)

    def stop(self):
        self.running = False