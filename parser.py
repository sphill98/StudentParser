import fitz  # PyMuPDF
import re
import pandas as pd
import platform

# 일반선택 과목 리스트
general_subjects = set([
    '국어', '화법과 작문', '독서', '언어와 매체', '문학', '수학', '수학Ⅰ', '수학Ⅱ',
    '미적분', '확률과 통계', '영어', '영어Ⅰ', '영어Ⅱ', '영어 회화', '영어 독해와 작문',
    '통합사회', '한국지리', '세계지리', '세계사', '동아시아사', '경제', '정치와 법',
    '사회·문화', '생활과 윤리', '윤리와 사상', '통합과학', '과학탐구실험', '물리학Ⅰ',
    '화학Ⅰ', '생명과학Ⅰ', '지구과학Ⅰ', '기술·가정', '정보', '독일어Ⅰ', '프랑스어Ⅰ',
    '스페인어Ⅰ', '중국어Ⅰ', '일본어Ⅰ', '러시아어Ⅰ', '아랍어Ⅰ', '베트남어Ⅰ', '한문Ⅰ',
    '국제 정치', '국제 경제', '국제법', '지역 이해', '한국 사회의 이해', '비교 문화',
    '세계 문제와 미래 사회', '국제 관계와 국제기구', '현대 세계의 변화', '철학', '논리학',
    '심리학', '교육학', '종교학', '진로와 직업', '보건', '환경', '실용 경제', '논술'
])

def extract_section_text(lines, start_idx, end_idx):
    return lines[start_idx:end_idx]

def parse_grade_section(lines, grade):
    records = []
    semester = "1학기"
    term = f"{grade}{semester}"
    i = 0
    while i + 5 < len(lines):
        try:
            l0, l1, l2, l3, l4, l5 = lines[i:i+6]
            subject_area = l0.strip()
            subject = l1.strip()
            unit = l2.strip()
            score_str = l3.strip()
            grade_str = l4.strip()
            rank = l5.strip()

            # 학기 변경 감지
            if "2학기" in subject_area:
                semester = "2학기"
                term = f"{grade}{semester}"
                i += 1
                continue

            if not re.match(r"\d+\.?\d*/\d+\.?\d*\(\d+\.?\d*\)", score_str):
                i += 1
                continue

            group1 = "일반선택" if subject in general_subjects else "진로선택"

            if "영어" in subject:
                group2 = "영어"
            elif "수학" in subject:
                group2 = "수학"
            elif "국어" in subject:
                group2 = "국어"
            elif "중국어" in subject or "프랑스어" in subject:
                group2 = "제2외국어"
            elif "과학" in subject:
                group2 = "과학"
            elif "법" in subject or "정치" in subject or "사회" in subject:
                group2 = "사회"
            else:
                group2 = "기타"

            sm = re.match(r"(\d+\.?\d*)/(\d+\.?\d*)\((\d+\.?\d*)\)", score_str)
            score, avg, std = sm.groups() if sm else ("", "", "")

            gm = re.match(r"([ABC])\((\d+)\)", grade_str)
            achievement, total = gm.groups() if gm else ("", "")

            A = B = C = ""
            if achievement == "A":
                A = total
            elif achievement == "B":
                B = total
            elif achievement == "C":
                C = total

            records.append([
                term, group1, group2, subject, unit,
                score, avg, std, achievement, total,
                A, B, C, rank
            ])
            i += 6
        except Exception:
            i += 1
            continue
    return records

def extract_grades_from_pdf(pdf_path, output_csv_path):
    doc = fitz.open(pdf_path)
    full_text = "\n".join([page.get_text() for page in doc])
    lines = full_text.split('\n')

    section_indices = {}
    for idx, line in enumerate(lines):
        if line.strip() == "[1학년]":
            section_indices["1학년"] = idx
        elif line.strip() == "[2학년]":
            section_indices["2학년"] = idx
        elif line.strip() == "[3학년]":
            section_indices["3학년"] = idx

    all_records = []
    grade_keys = sorted(section_indices.keys())
    for idx, grade in enumerate(grade_keys):
        start = section_indices[grade]
        end = section_indices[grade_keys[idx+1]] if idx+1 < len(grade_keys) else len(lines)
        section_lines = extract_section_text(lines, start, end)
        all_records.extend(parse_grade_section(section_lines, grade))

    df = pd.DataFrame(all_records, columns=[
        "학년/학기", "교과 구분1", "교과 구분2", "과목명", "단위",
        "원점수", "평균", "편차", "성취도", "수강자수",
        "A", "B", "C", "석차등급"
    ])

    # OS에 맞춰 인코딩 선택
    system = platform.system()
    encoding = "cp949" if system == "Windows" else "utf-8-sig"

    df.to_csv(output_csv_path, index=False, encoding=encoding)
    print(f"CSV 저장 완료: {output_csv_path}")

if __name__ == "__main__":
    input_pdf = "경북외고 생활기록부.pdf"
    output_csv = "성적_추출_결과.csv"
    extract_grades_from_pdf(input_pdf, output_csv)