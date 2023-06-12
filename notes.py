# Part of the main code told to focus on first
def __add_document():
    global current_bot
    # Used to access a file that has been uploaded through a form. Retieves the file object assocaited with the
    # file input name 'file' in the form.
    document = request.files['file']
    # Sanitize and secure the filename of an uploaded file
    document_name = secure_filename(document.filename)
    # Creating/joining the path for the uploaded document
    document_path = os.path.join("..", "storage", current_id, "documents", document_name)
    # Saving the uploaded file to the path - using open with save can sometimes cause issues
    # wb used with open to tell the model to open the file for writing in binary mode. w-write b-binary
    # Commonly used when not working with text files
    document.save(open(document_path, "wb"))
    # Calling document helped from the SourceHelper file
    doc = DocumentHelper()
    doc.load_file(BytesIO(open(document_path, "rb").read()), os.path.split(document_path)[-1])
    current_bot.add_document(doc)
    __save_project()





<!DOCTYPE html>
<html>
  <head>
    <style>
      .card {
        width: 100px;
        height: 200px;
        border: 1px solid #ccc;
        border-radius: 5px;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
      }
    </style>
  </head>
  <body>
  <div class="card" style="height: 80%; text-align: center; background-color: #ececec" onclick="uploadFile()">
      <p><i class="fa-solid fa-plus fa-2x" style="color: white"></i></p>

      <h6>Add File</h6>
      <p><small>(or drag&drop)</small></p>

      <form method="POST" action="/upload" enctype="multipart/form-data">
          <input type="file" class="hidden" onchange="submitForm()">
      <input type="submit" class="hidden">
    </form>

  </div>
          <script>
      function uploadFile() {
        document.getElementById('file-input').click();
      }

      function submitForm() {
        document.getElementById('upload-form').submit();
      }
    </script>
  </body>
</html>


# Basic working function
from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder = 'template')
app.config['UPLOAD_FOLDER'] = 'uploads'  # Define the folder to store uploaded files


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return 'File successfully uploaded and saved in the app!'
        else:
            return 'No file selected!'
    return render_template('upload.html')


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)

###### WTF form - works for posting a list ####


uploaded_documents = ['HI', 'TESTING']


class TodoForm(FlaskForm):
    uploaded_document = StringField("Upload a Document")
    submit = SubmitField("Add Folder")


# Use Post to post submit things and GET to take in things so post text and then get the text to show it
# on the app
@app.route('/', methods=["GET", "POST"])
def index():
    if 'uploaded_document' in request.form:
        uploaded_documents.append(request.form['uploaded_document'])
    return render_template('upload.html', uploaded_documents=uploaded_documents, template_form=TodoForm())


if __name__ == '__main__':
    app.run(debug=True)

<!DOCTYPE html>
<html>
  <head>
    <style>
      .card {
        width: 100px;
        height: 200px;
        border-radius: 12px;
        border-color: #ececec;
        border-width: thin;
        background-color: white;
        padding: 10px;
        margin-bottom: 2vh;
        cursor: pointer;
      }
    </style>
        </head>
  <body>
  <div class="card" style="height: 80%; text-align: center; background-color: #ececec" onclick="uploadFile()">
      <p><i class="fa-solid fa-plus fa-2x" style="color: white"></i></p>
      <div class = "card-content">

      <h6>Add File</h6>
      <p><small>(or drag&drop)</small></p>
      <input type="file" id="fileInput" style="display: none;" >
             </div>
      </div>

  <h1> Uploaded documents </h1>
  <!-- Creating a for loop that goes through all the labels in the uploaded documents list -->
  {% for uploaded_document in uploaded_documents %}
  <li> {{ uploaded_document }}</li>
  {% endfor %}

  <!-- Creating the submit and label tags to then  post to the page. We then use the Get to view this on the
  page -->
  <form method="POST">
      {{  template_form.hidden_tag()  }}
      <p>
          {{  template_form.uploaded_document.label  }}
          {{  template_form.uploaded_document()  }}
      </p>
      <p>
          {{  template_form.submit()  }}
      </p>
  </form>

  <script>
      function uploadFile() {
        document.getElementById('fileInput').click();
        }
  </script>
  </body>
</html>