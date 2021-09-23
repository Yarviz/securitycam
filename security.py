from flask import Flask
from flask_login import LoginManager
from database import DataBase, UserHelper, get_log_handler
import logging
import argparse
import signal
from camera import Camera

app = Flask("security cam")
#app.config['LOGIN_DISABLED'] = True
app.secret_key = 'security app'

login_manager = LoginManager()
login_manager.init_app(app)

loghandler = get_log_handler(logging.DEBUG)
log = logging.getLogger('securitycam')
log.addHandler(loghandler)

db = DataBase(log)
users = UserHelper(db)
camera = None

import routes

def sig_handler(sig, frame):
    if camera:
        camera.stop_reader()
    log.info('got SIGINT, exiting')
    exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cert', action='store_true', help='set this if using HTTPS')
    parser.add_argument('--port', type=str, help='enter arduino serial port')

    args = parser.parse_args()

    log.setLevel(logging.INFO)

    if db.open_db() == False:
        log.error('Failed to open database')
        exit(1)

    if args.port:
        camera = Camera(args.port, log)
        if camera.start_reader() == False:
            log.warning("Can't open serial port")
        else:
            log.info("Camera state reader started")
            db.set_mutex()
    else:
        log.warning("Arduino serial port not defined, can't take security pictures.")

    cert = None
    if args.cert:
        cert = 'adhoc'

    signal.signal(signal.SIGINT, sig_handler)

    log.info(db.read(table='users'))
    app.run(debug=False, ssl_context=cert)