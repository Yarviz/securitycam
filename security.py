from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask.logging import default_handler
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from database import DataBase, User, UserHelper, get_log_handler
import logging
import argparse
import json
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

def error(msg):
    return jsonify({
        'result' : 401,
        'message': msg
    })

def ok(data):
    return jsonify({
        'result' : 200,
        'data': data
    })

def sig_handler(sig, frame):
    log.info('got SIGINT, exiting')
    if camera:
        camera.stop_reader()
    exit(0)

@login_manager.user_loader
def load_user(user_id):
    return users.get_user(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photos', methods=['POST'])
@login_required
def get_photos():
    data = request.json
    req_type = data.get('request')
    if req_type == 'list':
        get_all = False if data.get('all') == False else True
        log.info('get photos')
        return jsonify(db.get_photo_infos(get_all))
    elif req_type == 'get':
        id = data.get('id')
        img = db.get_photo_img(id)
        if img:
            img_path = 'photos/' + img
            return ok(url_for('static', filename=img_path))
        return error('image not found')
    elif req_type == 'delete':
        id = data.get('id')
        deleted = db.delete_photo(id)
        if deleted > 0:
            return ok('image entry deleted')
        return error('image entry not found')

    return error('invalid request type')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == None or password == None:
        return error('enter username and password')

    user = users.validate_user(username, password)
    if user:
        log.info(user.to_json())
        login_user(user)
        return ok(user.to_json())
    else:
        return error('invalid username or password')

@app.route('/browse_data')
@login_required
def broqse_data():
    if current_user.is_authenticated() == False:
        return login_manager.unauthorized()
    user = current_user.to_json()
    return render_template('data.html', user=user['name'], email=user['email'])

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
    app.run(debug=True, ssl_context=cert)