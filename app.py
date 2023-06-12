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

#####################################################
@app.route('/upload_document', methods=["POST"])
def upload_document():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    document_path = os.path.join("..", "storage", "MJ6AP276WPV8BEZN", "documents", filename)
    uploaded_file.save(open(document_path, "wb"))
    return render_template("home.html")

< div


class ="card" style="height: 80%; text-align: center; background-color: #ececec" onclick="uploadFile()" >

< p > < i


class ="fa-solid fa-plus fa-2x" style="color: white" > < / i > < / p >

< h6 > Add
File < / h6 >
< input
type = "file"
id = "fileInput"
style = "display: none;" >
< p > < small > (or drag & drop) < / small > < / p >

function uploadFile() {
            document.getElementById('fileInput').click();
        }

        document.getElementById('fileInput').addEventListener('change', function() {
            let file = this.files[0];
            let formData = new FormData();
            formData.append('file', file);

            fetch('/upload_document', {
                method: 'POST',
                body: formData
            })
                .then(response => response.text())
                .then(data => {
                    console.log(data);
                    alert('File uploaded successfully');
                    window.location.reload();
                })
                .catch(error => {
                    console.error(error);
                    alert('Error uploading file');
                })
        })


cursor: pointer;
#####################################################