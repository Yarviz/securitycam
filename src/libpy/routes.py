from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from __main__ import app, login_manager, users, log, db

from flask import send_from_directory

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

@login_manager.user_loader
def load_user(user_id):
    return users.get_user(user_id)

@app.route('/uploads/<path:filename>')
def download_file(filename):
    #log.info(app.config['UPLOAD_FOLDER'])
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)

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
        #log.info('get photos')
        return jsonify(db.get_photo_infos(get_all))
    elif req_type == 'get':
        id = data.get('id')
        img = db.get_photo_img(id)
        if img:
            return ok(url_for('download_file', filename=img))
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
        log.debug(user.to_json())
        login_user(user)
        db.update(table='users', rows=['notificated'], values=[0], where='WHERE id={}'.format(user.get_id()))
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