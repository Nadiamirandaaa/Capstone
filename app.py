from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
import locale

import os
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

locale.setlocale(locale.LC_TIME, 'id_ID')

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
    return render_template('user/login.html')

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
                "token": token,
                'message': 'Selamat datang'
            })
            response.set_cookie('mytoken', token)
            return response
        else:
            return jsonify({'error': 'Invalid credentials','message': 'Data tidak valid'})

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

        return render_template('user/pendaftaranonline.html', nama=nama_pengguna, nik=nik_pengguna, user_info=user_info)
    else:
        return jsonify({'error': 'Data pengguna tidak ditemukan'})

# _________________ Queue Registration ________________________________________________
@app.route('/pendaftaranonline', methods=['POST'])
def pendaftaranonline():
    if request.method == 'POST':

        nama = request.form['nama']
        tanggal = request.form['tanggal']
        sesi = request.form['sesi']
        mcu = request.form['mcu']

        user_info = get_user_info()  if get_user_info() else {'_id': None}

        if not (tanggal and sesi and mcu and nama):
            return jsonify({'result': 'error', 'message': 'Data tidak lengkap'})
        
        tanggal_obj = datetime.strptime(tanggal, '%Y-%m-%d')
        tanggal_formatted = tanggal_obj.strftime('%d %b %Y')
        hari = tanggal_obj.strftime("%A")

        tanggal_sekarang = datetime.now()

        if tanggal_obj < tanggal_sekarang:
            return jsonify({'result': 'error', 'message': 'Pendaftaran tidak bisa dilakukan untuk tanggal yang sudah lewat'})


        if hari == "Sabtu" or hari == "Minggu":
            return jsonify({'result': 'error', 'message': 'Pelayanan Tidak Tersedia Pada Akhir Pekan (Sabtu atau Minggu)'})
        
        if sesi == "pagi":
            jam_awal = datetime.strptime('08:00', '%H:%M')
            jam_akhir = datetime.strptime('12:00', '%H:%M')
            durasi_per_antrian = timedelta(minutes=15)
        elif sesi == "siang":
            jam_awal = datetime.strptime('12:30', '%H:%M')
            jam_akhir = datetime.strptime('14:30', '%H:%M')
            durasi_per_antrian = timedelta(minutes=15)
        elif sesi == "sore":
            jam_awal = datetime.strptime('15:00', '%H:%M')
            jam_akhir = datetime.strptime('18:00', '%H:%M')
            durasi_per_antrian = timedelta(minutes=20)
        else:
            return jsonify({'result': 'error', 'message': 'Sesi tidak valid'})
        
        # waktu_sekarang = datetime.now().time()
        # if waktu_sekarang > jam_akhir.time():
        #     return jsonify({'result': 'error', 'message': 'Kuota pendaftaran untuk sesi ini telah habis'})

        
        # jam_akhir_hari = datetime.strptime('18:00', '%H:%M').time()
        # if waktu_sekarang > jam_akhir_hari:
        #     return jsonify({'result': 'error', 'message': 'Kuota pendaftaran untuk hari ini telah habis'})

        if db.antrian.find_one({"user_id": user_info["_id"], "tanggal": tanggal_formatted}):
            return jsonify({'result': 'error', 'message': f'Anda sudah mendaftar pada Hari {hari}, {tanggal_formatted} '})
        

        # _________________ Antrian _________________________
        if db.antrian.count_documents({"tanggal": tanggal_formatted,
        "sesi": sesi,
        "mcu": mcu}) == 0:
            nomor_antrian_baru = 1
            jam = jam_awal
        else:
            last_item = db.antrian.find_one(sort=[('_id', -1)])
            
            if (last_item['tanggal'] != tanggal_formatted and
                         last_item['sesi'] != sesi and
                         last_item['mcu'] != mcu):
                
                nomor_antrian_baru = 1
                jam = jam_awal
            else:
                nomor_antrian_baru = last_item['nomor_antrian'] + 1
                jam = last_item['jam'] + durasi_per_antrian 

        data_pendaftaran = {
            'user_id': user_info["_id"],
            'nama': nama,
            'nomor_antrian': nomor_antrian_baru,
            'hari': hari,
            'jam' : jam.strftime('%H:%M'),
            'tanggal': tanggal_formatted,
            'sesi': sesi,
            'mcu': mcu,
            'nomor_antrian': nomor_antrian_baru
        }
        db.antrian.insert_one(data_pendaftaran)

        return jsonify({'result': 'success','nama': nama,
            'nomor_antrian': nomor_antrian_baru,
            'hari': hari,
            'tanggal': tanggal_formatted,
            'sesi': sesi,
            'jam': jam.strftime('%H:%M'),
            'mcu': mcu,
            'nomor_antrian': nomor_antrian_baru})

# _________________ Register Page Display ________________________________________________
@app.route('/register', methods=['GET'])
def show_register():
    return render_template('user/register.html')

# _________________ Registration Process ________________________________________________
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        nik = request.form['nik']
        jenis_kelamin = request.form['gender']
        alamat = request.form['alamat']

        if not nik or len(nik) != 16:
            return jsonify({'result': 'error', 'message': 'NIK harus terdiri dari 16 karakter!'})
    
        if not (nama and nik and jenis_kelamin and alamat):
            return jsonify({'result': 'error', 'message': 'Harap Isi Semua Data'})
        
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
    return render_template('user/index.html', user_info=user_info)

# _________________ Queue Pages Display ________________________________________________
@app.route('/antrian')
def antrian():
   token = request.cookies.get('token')
   return render_template('user/antrian.html',token=token)

# _________________ Instruction Pages Display ________________________________________________
@app.route('/petunjuk')
def petunjuk():
   user_info = get_user_info()
   return render_template('user/petunjuk.html',user_info=user_info)

@app.route('/petunjukpendaftaran')
def petunjukpendaftaran():
   return render_template('user/petunjukpendaftaran.html')

@app.route('/petunjukhasilpemeriksaan')
def petunjukhasilpemeriksaan():
   return render_template('user/petunjukhasilpemeriksaan.html')

# _________________ Article Pages Display ________________________________________________
@app.route('/artikelkolesterol')
def artikelkolesterol():
   return render_template('user/artikelkolesterol.html')

@app.route('/artikelguladarah')
def artikelguladarah():
   return render_template('user/artikelguladarah.html')

@app.route('/artikelurine')
def artikelurine():
   return render_template('user/artikelurine.html')

# _________________ Account Pages Display ________________________________________________
@app.route('/akun')
def akun():
   return render_template('user/akun.html')


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

        return render_template('admin/dashboard.html', admin=admin, password=password, admininfo=admininfo)
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
    return render_template("admin/login-admin.html")

# _________________ Edit Detail Rumah Sakit ________________________________________________         
@app.route('/admin/editrs')
def editrs():
   return render_template('admin/editrs.html')

@app.route('/save_data', methods=['POST'])
def save_data():
    try:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        nama_mcu = request.form['nama_mcu']
        detailrs_mcu = request.form['detailrs_mcu']

        doc = {"nama_mcu": nama_mcu, "detailrs_mcu": detailrs_mcu, "user_id": payload["id"]}
        db.medical_checkup.insert_one(doc)

        return jsonify({'message': 'Data Berhasil Disimpan!', 'success': True})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'message': 'Token tidak valid!'})

@app.route('/delete_data', methods=['POST'])
def delete_data():
    try:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        nama_mcu = request.form['nama_mcu']
        detailrs_mcu = request.form['detailrs_mcu']

        db.medical_checkup.delete_one({"nama_mcu": nama_mcu, "detailrs_mcu": detailrs_mcu, "user_id": payload["id"]})
        
        return jsonify({'message': 'Data Dihapus!', 'success': True})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'message': 'Token tidak valid!'})

@app.route('/admin/detailrs/<nama_mcu>', methods=['GET'])
def detailrs(nama_mcu):
    try:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        mcu_data = db.medical_checkup.find_one({"nama_mcu": nama_mcu, "user_id": payload["id"]})
        return render_template('admin/detailrs.html', mcu_data=mcu_data)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'message': 'Token tidak valid!'})

@app.route('/get_all_data', methods=['GET'])
def get_all_data():
    try:
        token_receive = request.cookies.get("mytoken")
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        all_data = list(db.medical_checkup.find({"user_id": payload["id"]}))
        return jsonify({'all_data': all_data})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'message': 'Token tidak valid!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)