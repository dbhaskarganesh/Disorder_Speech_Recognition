import os
from flask import Flask, request, render_template, redirect, url_for, send_file
import your_speech_to_text_module

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            result = your_speech_to_text_module.recognize_speech(filename)
            return render_template('result.html', result=result)  

    return render_template('index.html')

@app.route('/image/<image_filename>')
def get_image(image_filename):
    return send_file(image_filename, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
