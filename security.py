from flask import Flask, render_template, request, jsonify, redirect
from flask.logging import default_handler
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from helpers import DataBase, User, UserHelper, get_log_handler
import logging
import argparse
import json

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

@login_manager.user_loader
def load_user(user_id):
    return users.get_user(user_id)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_photos', methods=['POST'])
@login_required
def get_photos():
    data = request.json
    req_type = data.get('request')
    if req_type == 'list':
        get_all = False if data.get('all') == False else True
        log.info('get photos')
        return jsonify(db.get_photo_infos(get_all))
    elif req_type == 'photo':
        id = data.get('id')
        img = db.get_photo_img(id)
        if img:
            img_path = 'photos/' + img
            return ok(img_path)
        return error('image not found')

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
    parser.add_argument('--create_db', action='store_true')
    parser.add_argument('--dummy_val', action='store_true')
    parser.add_argument('--cert', action='store_true')

    args = parser.parse_args()

    log.setLevel(logging.INFO)

    if db.open_db() == False:
        log.error('Failed to open database')
        exit(1)

    if args.create_db:
        files = []
        if args.dummy_val:
            files.extend(['file1', 'file2'])
        db.create_db(files)

    cert = None
    if args.cert:
        cert = 'adhoc'

    log.info(db.read(table='users'))
    app.run(debug=True, ssl_context=cert)