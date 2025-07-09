from flask import Flask, render_template, request, send_file
import os
from parser import extract_grades

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
        
        output_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.csv')
        extract_grades(filepath, output_csv_path)
        
        return send_file(output_csv_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
