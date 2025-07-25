from flask import Blueprint, render_template, request, send_file, session, flash, redirect, url_for, current_app
import pandas as pd
import os
from .parser import extract_subjects_from_pdf
from .calculators import compute_main_subject_averages, compute_science_subject_averages, compute_liberal_subject_averages, compute_overall_trend, compute_major_trend
import uuid
from io import StringIO

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and             filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            try:
                df = extract_subjects_from_pdf(filepath)
                session['dataframe'] = df.to_json()
                csv_filename = f"output_{uuid.uuid4().hex}.csv"
                output_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_filename)
                df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
                session['csv_path'] = output_csv_path
                return redirect(url_for('main.results'))
            except Exception as e:
                return render_template('error.html')
        else:
            flash('Only PDF files are allowed')
            return redirect(request.url)
    return render_template('upload.html')

@main.route('/results')
def results():
    csv_path = session.get('csv_path')
    if not csv_path or not os.path.exists(csv_path):
        return redirect(url_for('main.index'))
    filename = os.path.basename(csv_path)
    return render_template('download.html', filename=filename)

@main.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    return send_file(path, as_attachment=True)

@main.route('/graph-general')
def graph_general():
    df_json = session.get('dataframe')
    curr_grade = session.get('curr_grade')
    if not df_json:
        return "파일이 없습니다. 파일을 먼저 업로드해주세요."
    if curr_grade is None:
        return "학년 선택을 먼저 해주세요."
    df = pd.read_json(StringIO(df_json))
    averages = compute_main_subject_averages(df, curr_grade)
    if not averages:
        return render_template('error.html')
    # For Logging
    print(averages, curr_grade)
    labels = ["국어", "수학", "영어", "사탐", "과탐"]
    data = []
    for l in labels:
        data.append(averages.get(l))

    return render_template('graph_general.html', labels=labels, data=data)

@main.route('/graph-science')
def graph_science():
    df_json = session.get('dataframe')
    curr_grade = session.get('curr_grade')
    if not df_json:
        return "파일이 없습니다. 파일을 먼저 업로드해주세요."
    if curr_grade is None:
        return "학년 선택을 먼저 해주세요."
    df = pd.read_json(StringIO(df_json))
    averages = compute_science_subject_averages(df, curr_grade)
    if not averages:
        return render_template('error.html')
    # For Logging
    print(averages, curr_grade)
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
    curr_grade = session.get('curr_grade')
    if not df_json:
        return "파일이 없습니다. 파일을 먼저 업로드해주세요."
    if curr_grade is None:
        return "학년 선택을 먼저 해주세요."
    df = pd.read_json(StringIO(df_json))
    averages = compute_liberal_subject_averages(df, curr_grade)
    if not averages:
        return render_template('error.html')
    # For Logging
    print(averages, curr_grade)
    labels = ["통합사회", "한국사", "한국지리", "세계지리", "세계사", "동아시아사", "경제", "정치와 법", "생활과 윤리", "윤리와 사상", "사회·문화"]
    real_labels = []
    data = []
    for l in labels:
        if l in averages.keys():
            real_labels.append(l)
            data.append(averages[l])

    return render_template('graph_liberal.html', labels=real_labels, data=data)

@main.route('/chart-liberal')
def chart_liberal():
    df_json = session.get('dataframe')
    curr_grade = session.get('curr_grade')
    if not df_json:
        return "파일이 없습니다. 파일을 먼저 업로드해주세요."
    if curr_grade is None:
        return "학년 선택을 먼저 해주세요."
    df = pd.read_json(StringIO(df_json))
    all_labels = ['1학년 1학기', '1학년 2학기', '2학년 1학기', '2학년 2학기', '3학년 1학기', '3학년 2학기']
    if curr_grade == 0:  # 2학년 재학
        labels = all_labels[:4]
    elif curr_grade == 1:  # 3학년 재학
        labels = all_labels[:5]
    else:  # 졸업
        labels = all_labels
    overall_grades = compute_overall_trend(df, curr_grade)
    major_grades = compute_major_trend(df, curr_grade, ["국어", "수학", "영어", "사회"])
    return render_template('chart_liberal.html', labels=labels, overall_grades=overall_grades, major_grades=major_grades)

@main.route('/chart-science')
def chart_science():
    df_json = session.get('dataframe')
    curr_grade = session.get('curr_grade')
    if not df_json:
        return "파일이 없습니다. 파일을 먼저 업로드해주세요."
    if curr_grade is None:
        return "학년 선택을 먼저 해주세요."
    df = pd.read_json(StringIO(df_json))
    all_labels = ['1학년 1학기', '1학년 2학기', '2학년 1학기', '2학년 2학기', '3학년 1학기', '3학년 2학기']
    if curr_grade == 0:  # 2학년 재학
        labels = all_labels[:4]
    elif curr_grade == 1:  # 3학년 재학
        labels = all_labels[:5]
    else:  # 졸업
        labels = all_labels
    overall_grades = compute_overall_trend(df, curr_grade)
    major_grades = compute_major_trend(df, curr_grade, ["국어", "수학", "영어", "과학"])
    return render_template('chart_science.html', labels=labels, overall_grades=overall_grades, major_grades=major_grades)
