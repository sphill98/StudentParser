import fitz  # PyMuPDF
import re
import pandas as pd
import json

# JSON에서 과목 매핑 정보 불러오기
with open("./static/subject_mapping.json", "r", encoding="utf-8") as f:
    subject_mapping_json = json.load(f)
subject_mapping = {k: tuple(v) for k, v in subject_mapping_json.items()}

# 점수 파싱
def parse_score(score_str):
    match = re.match(r"(\d+)\/([\d.]+)\(([\d.]+)\)", score_str)
    return match.groups() if match else ("", "", "")

# 성취도 파싱
def parse_grade(grade_str):
    match = re.match(r"([ABC])\((\d+)\)", grade_str)
    return (match.group(1), int(match.group(2))) if match else ("", "")

# 과목명으로 교과 구분 추정
def map_subject(name):
    name = name.replace("\n", "").strip()
    return subject_mapping.get(name, ("기타", ""))

# 성적 추출 핵심 함수
def extract_subjects_from_pdf(pdf_path: str) -> pd.DataFrame:
    doc = fitz.open(pdf_path)
    subjects = []
    current_grade = "1학년"
    current_semester = "1학기"

    for page_num in range(len(doc)):
        text = doc.load_page(page_num).get_text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        i = 0

        while i < len(lines):
            if "[1학년]" in lines[i]:
                current_grade = "1학년"
            elif "[2학년]" in lines[i]:
                current_grade = "2학년"
            elif "[3학년]" in lines[i]:
                current_grade = "3학년"

            if lines[i] in ["1", "2"]:
                current_semester = lines[i] + "학기"
                i += 1
                continue

            # 일반 성적 항목
            if i + 4 < len(lines) and re.match(r"\d+\/[\d.]+\([\d.]+\)", lines[i+3]):
                과목명 = lines[i + 1]
                단위 = lines[i + 2]
                원점수, 평균, 편차 = parse_score(lines[i + 3])
                성취도, 수강자수 = parse_grade(lines[i + 4])
                석차등급 = lines[i + 5] if i + 5 < len(lines) and lines[i + 5].isdigit() else ""
                step = 6 if 석차등급 else 5

                교과구분2, 교과구분1 = map_subject(과목명)

                A = B = C = ""
                if 성취도 == "A": A = 수강자수
                elif 성취도 == "B": B = 수강자수
                elif 성취도 == "C": C = 수강자수

                subjects.append({
                    "학년/학기": f"{current_grade} {current_semester}",
                    "교과 구분1": 교과구분1,
                    "교과 구분2": 교과구분2,
                    "과목명": 과목명,
                    "단위": 단위,
                    "원점수": 원점수,
                    "평균": 평균,
                    "편차": 편차,
                    "성취도": 성취도,
                    "수강자수": 수강자수,
                    "A": A, "B": B, "C": C,
                    "석차등급": 석차등급
                })
                i += step

            # P만 있는 과목 (예: 체육/예술/진로선택)
            elif i + 2 < len(lines) and lines[i + 2] == "P":
                과목후보 = lines[i:i+3]
                과목명 = 과목후보[0] if not re.match(r"\d+", 과목후보[0]) else ""
                for j in range(len(과목후보)):
                    if re.match(r"^\d+$", 과목후보[j]):
                        과목명 = ''.join(과목후보[:j])
                        단위 = 과목후보[j]
                        break
                성취도 = "P"
                교과구분2, 교과구분1 = map_subject(과목명)
                subjects.append({
                    "학년/학기": f"{current_grade} {current_semester}",
                    "교과 구분1": 교과구분1,
                    "교과 구분2": 교과구분2,
                    "과목명": 과목명,
                    "단위": 단위,
                    "원점수": "", "평균": "", "편차": "",
                    "성취도": 성취도,
                    "수강자수": "", "A": "", "B": "", "C": "",
                    "석차등급": ""
                })
                i += 3
            else:
                i += 1

    doc.close()
    return pd.DataFrame(subjects)