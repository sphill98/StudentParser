from flask import Flask, render_template, request, send_file
import pandas as pd
import os
from parser import extract_subjects_from_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

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
            output_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.csv')
            df = extract_subjects_from_pdf(filepath)
            df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
            return send_file(output_csv_path, as_attachment=True)
        except Exception as e:
            return f"An error occurred: {e}"

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
