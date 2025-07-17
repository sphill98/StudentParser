from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for
import pandas as pd
import os
from .parser import extract_subjects_from_pdf
from .calculators import compute_main_subject_averages, compute_science_subject_averages, compute_liberal_subject_averages
import uuid

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    session.clear()
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = file.filename
            # Use app's upload folder config
            filepath = os.path.join(main.app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                df = extract_subjects_from_pdf(filepath)
                
                session['dataframe'] = df.to_json()

                csv_filename = f"output_{uuid.uuid4().hex}.csv"
                output_csv_path = os.path.join(main.app.config['UPLOAD_FOLDER'], csv_filename)
                
                df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
                
                session['csv_path'] = output_csv_path
                
                return render_template('download.html', filename=csv_filename)
            except Exception as e:
                flash(f"An error occurred: {e}")
                return redirect(url_for('main.index'))
        else:
            flash('Only PDF files are allowed')
            return redirect(request.url)
    else: # GET request
        csv_path = session.get('csv_path')
        if csv_path and os.path.exists(csv_path):
            filename = os.path.basename(csv_path)
            return render_template('download.html', filename=filename)
        else:
            return redirect(url_for('main.index'))

@main.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(main.app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)

@main.route('/graph-general')
def graph_general():
    df_json = session.get('dataframe')
    if not df_json:
        return "Dataframe not found in session. Please upload a file first."

    df = pd.read_json(df_json)
    averages = compute_main_subject_averages(df)
    labels = ["국어", "수학", "영어", "사탐", "과탐"]
    data = []
    for l in labels:
        data.append(averages[l])

    return render_template('graph_general.html', labels=labels, data=data)

@main.route('/graph-science')
def graph_science():
    df_json = session.get('dataframe')
    if not df_json:
        return "Dataframe not found in session. Please upload a file first."

    df = pd.read_json(df_json)
    averages = compute_science_subject_averages(df)
    labels = ["통합과학", "물리학Ⅰ", "화학Ⅰ", "생명과학Ⅰ", "지구과학Ⅰ"]
    real_labels = []
    data = []
    for l in labels:
        if l in averages.keys():
            real_labels.append(l)
            data.append(averages[l])

    return render_template('graph_science.html', labels=real_labels, data=data)

@main.route('/graph-liberal')
def graph_liberal():
    df_json = session.get('dataframe')
    if not df_json:
        return "Dataframe not found in session. Please upload a file first."

    df = pd.read_json(df_json)
    averages = compute_liberal_subject_averages(df)
    labels = ["통합사회", "한국사", "한국지리", "세계지리", "세계사", "동아시아사", "경제", "정치와 법", "생활과 윤리", "윤리와 사상", "사회·문화"]
    real_labels = []
    data = []
    for l in labels:
        if l in averages.keys():
            real_labels.append(l)
            data.append(averages[l])

    return render_template('graph_liberal.html', labels=real_labels, data=data)