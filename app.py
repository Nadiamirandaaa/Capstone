from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for,flash,session

from werkzeug.utils import secure_filename

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY")

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/pendaftaranonline')
def show_pendaftaranonline():
    token = request.cookies.get('token')
    if not token:
        return redirect(url_for('login'))

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if payload['id']:
            return render_template('pendaftaranonline.html')
    except jwt.ExpiredSignatureError:
        return 'Session expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
@app.route('/antrian')
def antrian():
   return render_template('antrian.html')

@app.route('/petunjuk')
def petunjuk():
   return render_template('petunjuk.html')

@app.route('/petunjukpendaftaran')
def petunjukpendaftaran():
   return render_template('petunjukpendaftaran.html')

@app.route('/petunjukhasilpemeriksaan')
def petunjukhasilpemeriksaan():
   return render_template('petunjukhasilpemeriksaan.html')

@app.route('/login', methods=['POST'])
def login():
    nama = request.form.get('nama')
    nik = request.form.get('nik')

    # Menggunakan SHA256 untuk mengenkripsi NIK
    hashed_nik = hashlib.sha256(nik.encode()).hexdigest()

    # Cek ke database jika data sesuai
    user = db.users.find_one({'nama': nama, 'nik': hashed_nik})

    if user:
        # Buat token JWT jika user valid
        token = jwt.encode({'id': nama, "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24)}, SECRET_KEY, algorithm='HS256')
        response = redirect(url_for('show_pendaftaranonline'))
        response.set_cookie('token', token, httponly=True)  # Set cookie with HttpOnly flag
        return response
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
    
@app.route('/login')
def show_login():
    return render_template('login.html')
    
@app.route('/register')
def show_register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']

        # Enkripsi NIK menggunakan SHA-256
        hashed_nik = hashlib.sha256(nik.encode()).hexdigest()

        # Simpan data ke MongoDB
        user = {
            'nama': nama,
            'nik': hashed_nik,  # Menggunakan NIK yang telah di-hash
            'jenis_kelamin': jenis_kelamin,
            'alamat': alamat
        }

        # Pastikan NIK terenkripsi unik sebelum menyimpan ke database
        existing_user = db.users.find_one({'nik': hashed_nik})
        if existing_user:
            return jsonify({'status': 'error', 'message': 'NIK sudah terdaftar'}), 400

        # Simpan data ke MongoDB
        db.users.insert_one(user)

        # Return a success message and redirect URL
        return jsonify({'status': 'success', 'message': 'Registrasi berhasil', 'redirect_url': '/login'})

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