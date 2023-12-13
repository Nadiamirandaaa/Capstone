from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for

from werkzeug.utils import secure_filename

import os
from os.path import join, dirname
from dotenv import load_dotenv
from functools import wraps

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")

def get_user_info():
    token_receive = request.cookies.get("mytoken")
    user_info = None
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"nama": payload["id"]})
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            pass
    return user_info

# Context processor to inject user_info into templates
@app.context_processor
def inject_user_info():
    user_info = get_user_info()
    return dict(user_info=user_info)

# Route to display login page
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')

# Route to perform login
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        nama_received = request.form["nama"]
        nik_received = request.form["nik"]

        hashed_nik = hashlib.sha256(nik_received.encode("utf-8")).hexdigest()

        user = db.users.find_one({'nama': nama_received, 'nik': hashed_nik})

        if user:
            token = jwt.encode({'id': nama_received, "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)}, SECRET_KEY, algorithm='HS256')
            response = jsonify({
                "result": "success",
                "token": token
            })
            response.set_cookie('mytoken', token)
            return response
        else:
            return jsonify({'error': 'Invalid credentials'})

# Route to display pendaftaran online page
@app.route('/pendaftaranonline', methods=['GET'])
def show_pendaftaranonline():
    user_info = get_user_info()
    if not user_info:
        return redirect(url_for("login"))
    return render_template('pendaftaranonline.html', user_info=user_info)

# Route to display registration page
@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html')

# Route to perform registration
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']

        hashed_nik = hashlib.sha256(nik.encode()).hexdigest()

        user = {
            'nama': nama,
            'nik': hashed_nik,
            'jenis_kelamin': jenis_kelamin,
            'alamat': alamat
        }

        existing_user = db.users.find_one({'nik': hashed_nik})
        if existing_user:
            return jsonify({'status': 'error', 'message': 'NIK sudah terdaftar'}), 400

        db.users.insert_one(user)

        return jsonify({'status': 'success', 'message': 'Registrasi berhasil', 'redirect_url': '/login'})

@app.route('/')
def home():
    user_info = get_user_info()
    return render_template('index.html', user_info=user_info)

@app.route('/antrian')
def antrian():
   token = request.cookies.get('token')
   return render_template('antrian.html',token=token)

@app.route('/petunjuk')
def petunjuk():
   user_info = get_user_info()
   return render_template('petunjuk.html',user_info=user_info)

@app.route('/petunjukpendaftaran')
def petunjukpendaftaran():
   return render_template('petunjukpendaftaran.html')

@app.route('/petunjukhasilpemeriksaan')
def petunjukhasilpemeriksaan():
   return render_template('petunjukhasilpemeriksaan.html')

@app.route('/artikelkolesterol')
def artikelkolesterol():
   return render_template('artikelkolesterol.html')

@app.route('/artikelguladarah')
def artikelguladarah():
   return render_template('artikelguladarah.html')

@app.route('/artikelurine')
def artikelurine():
   return render_template('artikelurine.html')

@app.route('/akun')
def akun():
   return render_template('akun.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)