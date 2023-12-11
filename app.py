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

MONGODB_CONNECTION_STRING = "mongodb+srv://capgemini:capstone@cluster0.il5vinp.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGODB_CONNECTION_STRING)

db = client.dbcapstone

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/pendaftaranonline')
def pendaftaranonline():
    if 'username' not in session:  # Periksa apakah pengguna sudah login
        flash('Anda harus login untuk mengakses halaman pendaftaran online', 'warning')
        return redirect(url_for('login'))  # Jika belum login, arahkan ke halaman login

    return render_template('pendaftaranonline.html')

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

@app.route('/login')
def login():
    error = None  # Inisialisasi variabel error
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']

        # Hash nik yang diinput untuk mencocokkan dengan yang tersimpan di database
        hashed_nik = hashlib.sha256(nik.encode()).hexdigest()

        # Cek apakah pengguna ada di basis data (di sini menggunakan contoh dummy_users)
        user = db.users.find_one({'nama': nama, 'nik': hashed_nik})
      
        
        if user:
            # Lakukan tindakan setelah berhasil login
            session['username'] = nama  # Simpan nama pengguna dalam sesi
            flash(f"Selamat datang, {nama}! Anda berhasil login.", 'success')
            return redirect(url_for('pendaftaranonline'))  # Alihkan ke halaman pendaftaran online setelah login berhasil

        else:
            flash("Kombinasi nama dan nik salah. Silakan coba lagi.", 'danger')

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        jenis_kelamin = request.form['jenis_kelamin']
        alamat = request.form['alamat']
        bpjs = request.form['bpjs']

        # Hashing password menggunakan SHA-256
        hashed_nik = hashlib.sha256(nik.encode()).hexdigest()
        hashed_bpjs = hashlib.sha256(bpjs.encode()).hexdigest()

        # Simpan data ke MongoDB
        user_data = {
            'nama': nama,
            'nik': hashed_nik,
            'jenis_kelamin':jenis_kelamin,
            'alamat':alamat,
            'bpjs':hashed_bpjs # Simpan password yang di-hash
        }

        db.users.insert_one(user_data)  # Menyimpan data ke koleksi MongoDB
        return "Registrasi berhasil! Data tersimpan di MongoDB."
    return render_template('register.html')

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