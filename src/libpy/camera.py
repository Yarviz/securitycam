from serial import Serial
from threading import Thread
import subprocess
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from serial.serialutil import SerialException

VALUE_TRESHOLD = 5.0
TIME_TRESHOLD  = 5.0
PHOTO_DIR      = 'database/photos'
PHOTO_FILE     = 'photo'
MAIL_SERVER    = 'smtp.mailtrap.io'
PORT           = 2525
LOGIN          = '***REMOVED***'
PASSWORD       = '***REMOVED***'
SECURITY_URL   = 'http://127.0.0.1:5000'

class Mail(object):
    def __init__(self, server, port, login, pswrd, log):
        self.server = server
        self.port = port
        self.login = login
        self.password = pswrd
        self.log = log

    def send_mail(self, msg, receivers):
        recv = ','.join(receivers)
        message = MIMEMultipart('security')
        message["Subject"] = "Security issue"
        message["From"] = 'security@mailtrap.io'
        message["To"] = recv

        html = f"""\
            <html>
            <body>
                <p>{msg}<br><br>
                <a href={SECURITY_URL}>Security Camera</a>
                </p>
            </body>
            </html>
        """
        part1 = MIMEText(msg, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                server.login(self.login, self.password)
                server.sendmail('security@mailtrap.io', recv, message.as_string())
                self.log.info('sent emails')
        except:
            self.log.info('email sent failed')

class Camera(object):
    def __init__(self, port, logger, mail=None, app=None):
        self.port = port
        self.log = logger
        self.reader = None
        self.read_thread = None
        self.mail = mail
        self.app = app

    def open_port(self, baudrate=9600, timeout=2):
        return Serial(self.port, baudrate=baudrate, timeout=timeout)

    def find_img_index(self):
        path = os.listdir(os.getcwd() + '/' + PHOTO_DIR)
        photo_indexes = []
        for file in path:
            if file.startswith(PHOTO_FILE) and file.endswith(".jpg"):
                try:
                    photo_indexes.append(int(list(filter(str.isdigit, file))[0]))
                except ValueError:
                    pass
        if not photo_indexes:
            return 0
        return max(photo_indexes) + 1


    def start_reader(self, db):
        try:
            self.reader = self.open_port()
        except SerialException:
            return False
        self.read_thread = ReadThread(self.reader, self.log, db, self.find_img_index())
        self.read_thread.start()
        return True

    def stop_reader(self):
        if self.read_thread:
            self.read_thread.stop()
            self.read_thread.join()
            self.reader.close()

class ReadThread(Thread):
    def __init__(self, reader, log, db, index):
        Thread.__init__(self)
        self.reader = reader
        self.log = log
        self.db = db
        self.running = False
        self.last_num = None
        self.pic_time = 0.0
        self.img_index = index
        self.mail = Mail(MAIL_SERVER, PORT, LOGIN, PASSWORD, log)

    def run(self):
        self.reader.flush()
        self.running = True
        while self.running == True:
            if self.reader.inWaiting() > 0:
                line = self.reader.readline().decode('utf-8').rstrip()
                #self.log.info(line)
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
        file_name = f'{PHOTO_FILE}_{self.img_index}.jpg'
        proc_out = subprocess.getoutput([f'fswebcam --no-banner {PHOTO_DIR}/{file_name}'])
        if proc_out.find('Captured frame') > 0:
            self.log.info(f'New frame {file_name} captured')
            self.db.insert(table='photos', rows=['file'], values=[file_name])
            self.img_index += 1
            if self.mail:
                self.post_email()
        else:
            self.log.warn('Failed to capture frame')

    def post_email(self):
        ret = self.db.read(table='users',rows=['id', 'email'],where='WHERE notifications = 1 AND notificated = 0')
        ids = [e[0] for e in ret]
        emails = [e[1] for e in ret]
        if ids:
            self.mail.send_mail('New security photo taked', receivers=emails)
            self.db.update_notificated(ids)

    def stop(self):
        self.running = False