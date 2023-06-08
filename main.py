from flask import Flask, render_template, send_file, request, redirect
from werkzeug.utils import secure_filename
from SourceHelper import DocumentHelper
from ChatModel import ChatModel
from datetime import datetime
from io import BytesIO
import pickle
import time
import glob
import json
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home.html", projects=__projects(), files=__current())


@app.route('/chat')
def chat():
    return render_template("chat.html", projects=__projects(), files=__current(),
                           prompt="I'm your assistant, ask me anything about the document")


@app.route('/change/<project_id>')
def change(project_id):
    global current_id
    current_id = project_id
    __load_project(current_id)
    return redirect("/")


@app.route('/file/<filename>')
def file(filename: str):
    print(f"Trying to load {filename}")
    global current_id
    if filename.lower().endswith("url"):
        return \
        "".join(open(os.path.join("..", "storage", current_id, "documents", filename), "r").readlines()).split("URL=")[
            1]

    correct_filename = ''.join(filename.split('.')[:-1]) + '.' + filename.split('.')[-1].lower()

    return send_file(open(os.path.join("..", "storage", current_id, "documents", correct_filename), "rb"),
                     download_name=correct_filename)


@app.route('/conversation')
def conversation():
    return render_template("conversation.html", conversation=__conversations())


@app.route('/load_chat', methods=["GET", "POST"])
def load_chat():
    global current_bot
    text = request.form['prompt']
    conversations = __conversations()
    conversations.append(__clean_dict({"side": "user", "sentence": text, "meta": {
        "source": "",
        "timestamp": time.time()
    }}))
    conversations.append(__clean_dict({"side": "loading", "sentence": "", "meta": {
        "source": "",
        "timestamp": time.time()
    }}))
    return render_template("conversation.html", conversation=conversations)


@app.route('/reset_chat')
def reset_chat():
    global current_bot
    current_bot.conversation = []
    conversations = __conversations()
    return render_template("conversation.html", conversation=conversations)


@app.route('/conversate', methods=["GET", "POST"])
def conversate():
    global current_bot
    text = request.form['prompt']
    current_bot.chat(text)
    conversations = __conversations()
    return render_template("conversation.html", conversation=conversations)


def __projects():
    global projects
    project_list = list()
    for i, v in projects.items():
        project_list.append((i, f"{v['customer']} - {v['name']}"))
    return project_list


def __load_project(project_id: str):
    global current_id, current_bot
    current_id = project_id
    current_bot = pickle.load(open(os.path.join("..", "storage", current_id, "chat_model.pkl"), "rb"))
    current_bot.reset_state()


def __save_project():
    global current_id, current_bot
    pickle.dump(current_bot, open(os.path.join("..", "storage", current_id, "chat_model.pkl"), "wb"))


def __conversations():
    global current_bot
    return [__clean_dict(c) for c in current_bot.conversation]


def __clean_dict(d):
    d["sentence"] = d["sentence"].replace('\n', '<br>')
    date_time = datetime.fromtimestamp(d["meta"]["timestamp"])
    d["timestamp"] = date_time.strftime("%d-%m-%Y, %H:%M:%S")
    return d


def __add_document():
    global current_bot
    document = request.files['file']
    document_name = secure_filename(document.filename)
    document_path = os.path.join("..", "storage", current_id, "documents", document_name)
    document.save(open(document_path, "wb"))
    doc = DocumentHelper()
    doc.load_file(BytesIO(open(document_path, "rb").read()), os.path.split(document_path)[-1])
    current_bot.add_document(doc)
    __save_project()


def __current():
    def human_size(size, units=None):
        if units is None:
            units = [' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        return str(size) + units[0] if size < 1024 else human_size(size >> 10, units[1:])

    global current_id
    dir_name = os.path.join("..", "storage", current_id, "documents")
    list_of_files = filter(os.path.isfile, glob.glob(os.path.join(dir_name, '*')))
    files_with_size = [(file_path, os.stat(file_path).st_size) for file_path in list_of_files]

    file_list = list()
    total_weight = 0
    for file_path, file_size in files_with_size:
        total_weight += file_size
        file_list.append((
                         os.path.splitext(os.path.split(file_path)[-1])[0], os.path.splitext(file_path)[-1][1:].upper(),
                         human_size(file_size)))

    return {
        "current": f"{projects[current_id]['customer']} - {projects[current_id]['name']}",
        "current_customer": projects[current_id]['customer'],
        "current_name": projects[current_id]['name'],
        "id": current_id,
        "files": file_list,
        "file_count": len(file_list),
        "file_weight": human_size(total_weight)
    }


projects = {i: v for i, v in json.load(open(os.path.join("..", "storage", "metadata.json"), "r"))}
current_id = "MJ6AP276WPV8BEZN"
current_bot = ChatModel([])
__load_project(current_id)
if __name__ == '__main__':
    try:
        app.config['SECRET_KEY'] = os.urandom(12)
        app.run(host="0.0.0.0", port=8081, debug=True, threaded=True)
    except KeyboardInterrupt:
        print("Server interrupted by user")