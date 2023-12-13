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

# _________________ Token User ________________________________________________
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

@app.context_processor
def inject_user_info():
    user_info = get_user_info()
    return dict(user_info=user_info)

# _________________ End Token User ________________________________________________

# _________________ Token Admin ________________________________________________

def get_admin_info():
    token_receive = request.cookies.get("mytoken")
    admininfo = None
    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            admininfo = db.admin.find_one({"admin": payload["id"]})
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            pass
    return admininfo

@app.context_processor
def inject_admin_info():
    admininfo = get_admin_info()
    return dict(admininfo=admininfo)

# _________________ End Token Admin ________________________________________________


# _________________ Login Page Display ________________________________________________
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')

# _________________ Login Process ________________________________________________
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

# _________________ Encrypted Pages ________________________________________________
@app.route('/pendaftaranonline', methods=['GET'])
def show_pendaftaranonline():
    user_info = get_user_info()
    if not user_info:
        return redirect(url_for("login"))

    user_data = db.users.find_one({'nama': user_info['nama']})  

    if user_data:
        nama_pengguna = user_data.get('nama')
        nik_pengguna = user_data.get('nik')

        return render_template('pendaftaranonline.html', nama=nama_pengguna, nik=nik_pengguna, user_info=user_info)
    else:
        return jsonify({'error': 'Data pengguna tidak ditemukan'})

# _________________ Queue Registration ________________________________________________
@app.route('/pendaftaranonline', methods=['POST'])
def pendaftaranonline():
    if request.method == 'POST':
        tanggal = request.form['tanggal']
        sesi = request.form['sesi']
        mcu = request.form['mcu']


        if db.antrian.count_documents({"tanggal": tanggal,
        "sesi": sesi,
        "mcu": mcu}) == 0:
            nomor_antrian_baru = 1
        else:
            last_item = db.antrian.find_one(sort=[('_id', -1)])
            
            if (last_item['tanggal'] != tanggal and
                         last_item['sesi'] != sesi and
                         last_item['mcu'] != mcu):
                
                nomor_antrian_baru = 1
            else:
                nomor_antrian_baru = last_item['nomor_antrian'] + 1

        data_pendaftaran = {
            'tanggal': tanggal,
            'sesi': sesi,
            'mcu': mcu,
            'nomor_antrian': nomor_antrian_baru
        }
        db.antrian.insert_one(data_pendaftaran)

        return jsonify({'result': 'success','nomor_antrian': nomor_antrian_baru})

# _________________ Register Page Display ________________________________________________
@app.route('/register', methods=['GET'])
def show_register():
    return render_template('register.html')

# _________________ Registration Process ________________________________________________
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        jenis_kelamin = request.form['gender']
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
            return jsonify({'result': 'error', 'message': 'NIK sudah terdaftar'})

        db.users.insert_one(user)

        return jsonify({'result': 'success', 'message': 'Registrasi berhasil', 'redirect_url': '/login'})

# _________________ Home Pages Display ________________________________________________
@app.route('/')
def home():
    user_info = get_user_info()
    return render_template('index.html', user_info=user_info)

# _________________ Queue Pages Display ________________________________________________
@app.route('/antrian')
def antrian():
   token = request.cookies.get('token')
   return render_template('antrian.html',token=token)

# _________________ Instruction Pages Display ________________________________________________
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

# _________________ Article Pages Display ________________________________________________
@app.route('/artikelkolesterol')
def artikelkolesterol():
   return render_template('artikelkolesterol.html')

@app.route('/artikelguladarah')
def artikelguladarah():
   return render_template('artikelguladarah.html')

@app.route('/artikelurine')
def artikelurine():
   return render_template('artikelurine.html')

# _________________ Account Pages Display ________________________________________________
@app.route('/akun')
def akun():
   return render_template('akun.html')


# _________________ Admin Pages Encrypted ________________________________________________
@app.route('/admin',methods=['GET'])
def homeAdmin():
    admininfo = get_admin_info()
    if not admininfo:
        return redirect(url_for("show_loginAdmin"))

    admin_data = db.admin.find_one({'admin': admininfo['admin']})  

    if admin_data:
        admin = admin_data.get('admin')
        password= admin_data.get('password')

        return render_template('dashboard.html', admin=admin, password=password, admininfo=admininfo)
    else:
        return jsonify({'error': 'Data pengguna tidak ditemukan'})

# _________________ Admin Login Process ________________________________________________
@app.route('/admin/login', methods=['POST'])
def loginAdmin():
    if request.method == 'POST':
        nama_received = request.form["nama"]
        pass_received = request.form["pass"]


        user = db.admin.find_one({'admin': nama_received, 'password': pass_received})

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

# _________________ Login Admin Pages Display ________________________________________________         
@app.route("/admin/login",methods=['GET'])
def show_loginAdmin():
    return render_template("login-admin.html")


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)