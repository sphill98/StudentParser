from flask import Flask, render_template, request, send_file, session
import pandas as pd
import os
from parser import extract_subjects_from_pdf
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = extract_subjects_from_pdf(filepath)
            
            # Generate a unique filename for the CSV
            csv_filename = f"output_{uuid.uuid4().hex}.csv"
            output_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_filename)
            
            df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
            
            # Store the csv path in the session
            session['csv_path'] = output_csv_path
            
            return render_template('download.html', filename=csv_filename)
        except Exception as e:
            return f"An error occurred: {e}"

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)

@app.route('/graph')
def graph():
    return render_template('graph.html')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
