from flask import Flask, request, jsonify
import os
import pandas as pd
from .parser import extract_subjects_from_pdf
from .calculators import (
    compute_main_subject_averages,
    compute_science_subject_averages,
    compute_liberal_subject_averages,
    compute_overall_trend,
    compute_major_trend,
    _get_valid_semesters
)
import uuid
from config.config import Config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/parse', methods=['POST'])
def parse_and_calculate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    curr_grade = request.form.get('curr_grade')
    if not curr_grade:
        return jsonify({"error": "Current grade is required"}), 400
    curr_grade = int(curr_grade)

    if file:
        filename = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            df = extract_subjects_from_pdf(filepath)
            valid_semesters = _get_valid_semesters(curr_grade)
            df = df[df["학년/학기"].isin(valid_semesters)].copy()

            general_averages = compute_main_subject_averages(df, curr_grade)
            science_averages = compute_science_subject_averages(df, curr_grade)
            liberal_averages = compute_liberal_subject_averages(df, curr_grade)
            
            overall_trend = compute_overall_trend(df, curr_grade)
            liberal_trend_major = compute_major_trend(df, curr_grade, ["국어", "수학", "영어", "사회"])
            science_trend_major = compute_major_trend(df, curr_grade, ["국어", "수학", "영어", "과학"])

            os.remove(filepath) # Clean up the uploaded file

            return jsonify({
                "dataframe_json": df.to_json(orient='split'), # Add DataFrame as JSON
                "general_averages": general_averages,
                "science_averages": science_averages,
                "liberal_averages": liberal_averages,
                "trend_labels": valid_semesters,
                "overall_trend": overall_trend,
                "liberal_trend_major": liberal_trend_major,
                "science_trend_major": science_trend_major
            })
        except Exception as e:
            # In a real app, you'd want to log this error.
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PARSING_SERVICE_PORT, debug=True)
