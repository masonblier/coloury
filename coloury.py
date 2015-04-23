# -*- coding: utf-8 -*-
"""
    coloury
    ~~~~~~
    A simple experiment of flask and celery functionality.
"""

import os
from flask import Flask, jsonify, request, render_template
from werkzeug import secure_filename
from tasks import ProcessImageColors

# app
app = Flask(__name__)

# configuration vars
app.config.update(dict(
    DEBUG=True,
    UPLOAD_FOLDER="tmp/",
    ALLOWED_EXTENSIONS=["jpg","jpeg","png"]
))

@app.route('/')
def show_home():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def handle_upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(filepath)

        task = ProcessImageColors.delay(os.path.abspath(filepath))
        return jsonify(taskId=task.task_id)
    else:
        return jsonify(error="invalid file"), 400

@app.route('/result/<task_id>')
def check_result(task_id):
    result = ProcessImageColors.AsyncResult(task_id)
    if result:
        value = None
        if result.ready():
            value = result.get()
        return jsonify(state=result.state, value=value)
    else:
        return jsonify(error="task not found"), 400

# start app
if __name__ == '__main__':
    app.run()
