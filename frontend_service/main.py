from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app, jsonify, send_file
import requests
import os
import pandas as pd
from io import StringIO, BytesIO
from config.config import Config

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}
PARSING_SERVICE_URL = f"http://localhost:{Config.PARSING_SERVICE_PORT}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _get_processed_data():
    return session.get('processed_data')

def _get_dataframe():
    df_json = session.get('dataframe_json')
    if df_json:
        return pd.read_json(StringIO(df_json), orient='split')
    return None

@main.route('/')
def index():
    client_ip = request.remote_addr
    requested_path = request.path
    current_app.logger.info(f"Client IP: {client_ip}, Requested Path: {requested_path}")
    if request.args.get('clear_session'):
        session.clear()
    return render_template('index.html')

@main.route('/handle_grade_selection', methods=['POST'])
def handle_grade_selection():
    curr_grade = request.form.get('curr_grade')
    if curr_grade is None:
        flash('현재 상태를 입력해주세요.')
        return redirect(url_for('main.index'))
    session['curr_grade'] = int(curr_grade)
    return redirect(url_for('main.upload'))

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    client_ip = request.remote_addr
    requested_path = request.path
    current_app.logger.info(f"Client IP: {client_ip}, Requested Path: {requested_path}")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            try:
                curr_grade = session.get('curr_grade')
                if curr_grade is None:
                    flash('Current grade not set.')
                    return redirect(url_for('main.index'))

                files = {'file': (file.filename, file.stream, file.mimetype)}
                data = {'curr_grade': curr_grade}
                
                response = requests.post(f"{PARSING_SERVICE_URL}/parse", files=files, data=data)
                response.raise_for_status()  # Raise an exception for bad status codes

                response_data = response.json()
                session['processed_data'] = response_data # Store all processed data
                session['dataframe_json'] = response_data.get('dataframe_json') # Store DataFrame JSON separately
                
                return redirect(url_for('main.results'))

            except requests.exceptions.RequestException as e:
                current_app.logger.error(f"Error calling parsing service: {e}")
                flash('Error processing file. The parsing service may be down.')
                return render_template('error.html')
            except Exception as e:
                current_app.logger.error(f"An unexpected error occurred: {e}")
                return render_template('error.html')
        else:
            flash('Only PDF files are allowed')
            return redirect(request.url)
    return render_template('upload.html')

@main.route('/results')
def results():
    client_ip = request.remote_addr
    requested_path = request.path
    current_app.logger.info(f"Client IP: {client_ip}, Requested Path: {requested_path}")
    if not _get_processed_data():
        return redirect(url_for('main.index'))
    return render_template('download.html')

@main.route('/download_csv')
def download_csv():
    df = _get_dataframe()
    if df is None:
        flash('No data to download.')
        return redirect(url_for('main.index'))
    
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_buffer.seek(0)

    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='student_grades.csv'
    )

@main.route('/graph-general')
def graph_general():
    processed_data = _get_processed_data()
    if not processed_data:
        return render_template('error.html')
    
    averages = processed_data.get('general_averages', {})
    labels = ["국어", "수학", "영어", "사탐", "과탐"]
    data = [averages.get(l) for l in labels]

    return render_template('graph_general.html', labels=labels, data=data)

@main.route('/graph-science')
def graph_science():
    processed_data = _get_processed_data()
    if not processed_data:
        return render_template('error.html')

    averages = processed_data.get('science_averages', {})
    labels = ["통합과학", "물리학Ⅰ", "화학Ⅰ", "생명과학Ⅰ", "지구과학Ⅰ"]
    real_labels = [l for l in labels if l in averages]
    data = [averages[l] for l in real_labels]

    return render_template('graph_science.html', labels=real_labels, data=data)

@main.route('/graph-liberal')
def graph_liberal():
    processed_data = _get_processed_data()
    if not processed_data:
        return render_template('error.html')
        
    averages = processed_data.get('liberal_averages', {})
    labels = ["통합사회", "한국사", "한국지리", "세계지리", "세계사", "동아시아사", "경제", "정치와 법", "생활과 윤리", "윤리와 사상", "사회·문화"]
    real_labels = [l for l in labels if l in averages]
    data = [averages[l] for l in real_labels]

    return render_template('graph_liberal.html', labels=real_labels, data=data)

@main.route('/chart-liberal')
def chart_liberal():
    processed_data = _get_processed_data()
    if not processed_data:
        return render_template('error.html')

    labels = processed_data.get('trend_labels', [])
    overall_grades = processed_data.get('overall_trend', [])
    major_grades = processed_data.get('liberal_trend_major', [])
    
    return render_template('chart_liberal.html', labels=labels, overall_grades=overall_grades, major_grades=major_grades)

@main.route('/chart-science')
def chart_science():
    processed_data = _get_processed_data()
    if not processed_data:
        return render_template('error.html')

    labels = processed_data.get('trend_labels', [])
    overall_grades = processed_data.get('overall_trend', [])
    major_grades = processed_data.get('science_trend_major', [])

    return render_template('chart_science.html', labels=labels, overall_grades=overall_grades, major_grades=major_grades)
