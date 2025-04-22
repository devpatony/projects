from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from celery import Celery
from celery.result import AsyncResult
import socketio
import uuid
import os
from werkzeug.utils import secure_filename
import pandas as pd
from services.validation_service import ValidationService
import logging

# Import the Celery task correctly
from celery_worker import process_excel_task  # Add this import

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask
app = Flask(__name__, static_folder='../frontend/static')
CORS(app, resources={
    r"/upload": {"origins": "http://localhost:3000"},
    r"/task/*": {"origins": "http://localhost:3000"},
    r"/socket.io/*": {"origins": "*"}
})

# Configuration
app.config.update(
    UPLOAD_FOLDER='uploads',
    ALLOWED_EXTENSIONS={'xlsx', 'xls'},
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Initialize Socket.IO
mgr = socketio.KombuManager(app.config['CELERY_BROKER_URL'])
sio = socketio.Server(async_mode='threading', cors_allowed_origins="*", client_manager=mgr)
socketio_app = socketio.WSGIApp(sio, app)

# Initialize Socket.IO
mgr = socketio.KombuManager(app.config['CELERY_BROKER_URL'])
sio = socketio.Server(async_mode='threading', cors_allowed_origins="*", client_manager=mgr)
socketio_app = socketio.WSGIApp(sio, app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type. Only .xlsx and .xls files are allowed."
        }), 415

    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Validate the Excel file for mandatory columns
        try:
            df = pd.read_excel(filepath)
            validation_result = ValidationService.validate_mandatory_columns(df)
            if not validation_result.is_valid:
                os.remove(filepath)  # Cleanup the file
                return jsonify({
                    "error": validation_result.message,
                    "missing_columns": validation_result.missing_columns
                }), 400
        except Exception as e:
            os.remove(filepath)  # Cleanup the file
            return jsonify({"error": f"Invalid Excel file: {str(e)}"}), 400

        # If validation passes, start the Celery task
        task_id = str(uuid.uuid4())
        process_excel_task.delay(filepath, task_id)
        
        return jsonify({
            "task_id": task_id,
            "message": "File uploaded successfully and processing started"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = AsyncResult(task_id, app=celery)
    
    response = {
        "task_id": task_id,
        "status": task.state,
    }
    
    if task.state == 'PROGRESS':
        response["progress"] = task.info.get('progress', 0)
        response["message"] = task.info.get('message', 'Processing')
    elif task.state == 'SUCCESS':
        response["result"] = task.result
        response["message"] = "Processing complete"
    elif task.state == 'FAILURE':
        response["message"] = str(task.info)
    
    return jsonify(response)

@sio.event
def connect(sid, environ):
    logging.info(f'Client connected: {sid}')
    sio.emit('connection_update', {'status': 'connected'}, room=sid)

@sio.event
def disconnect(sid):
    logging.info(f'Client disconnected: {sid}')

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, socketio_app)