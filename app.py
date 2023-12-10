from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/pendaftaranonline')
def pendaftaranonline():
   return render_template('pendaftaranonline.html')

@app.route('/antrian')
def antrian():
   return render_template('antrian.html')

@app.route('/petunjuk')
def petunjuk():
   return render_template('petunjuk.html')

@app.route('/petunjukpasienlama')
def petunjukpasienlama():
   return render_template('petunjukpasienlama.html')

@app.route('/petunjukpasienbaru')
def petunjukpasienbaru():
   return render_template('petunjukpasienbaru.html')

@app.route('/petunjukhasilpemeriksaan')
def petunjukhasilpemeriksaan():
   return render_template('petunjukhasilpemeriksaan.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/register')
def register():
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

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)