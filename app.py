from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/pendaftaran')
def pendaftaranonline():
   return render_template('pendaftaranonline.html')

@app.route('/antrian')
def antrian():
   return render_template('antrian.html')

@app.route('/petunjuk')
def petunjuk():
   return render_template('petunjuk.html')

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)