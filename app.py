from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, template_folder='template')


@app.route('/')
def index():
    return render_template('upload.html')


@app.route('/home', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return "No file selected."

    uploaded_file = request.files['file']

    if uploaded_file.filename == '':
        return "No file selected."

    # Secure the filename
    filename = secure_filename(uploaded_file.filename)

    # Save the uploaded file to the UPLOAD_FOLDER
    uploaded_file.save(os.path.join('storage/MJ6AP276WPV8BEZN/documents', filename))

    return render_template('upload')


if __name__ == '__main__':
    app.run(debug=True)
