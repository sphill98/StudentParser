import pdfplumber
import pandas as pd
import re

def extract_grades(pdf_path, output_csv_path='output.csv'):
    # 파일 경로
    pdf_path = "이공계열 학생부 샘플.pdf"
    subject_path = "고등학교 교과목.xlsx"

    # 학기 정보 (과목 수에 따라 작성)
    학기_정보 = (
            ["1학년 1학기"] * 8 +
            ["1학년 2학기"] * 10 +
            ["2학년 1학기"] * 9 +
            ["2학년 2학기"] * 7
    )

    # ----------------------------------------
    # 1. 교과목 리스트 불러와서 교과구분 매핑 테이블 생성
    # ----------------------------------------
    subject_df = pd.read_excel(subject_path, sheet_name="선택과목", header=None)
    subject_mappings = []
    current_구분2 = None
    current_구분1 = None

    for _, row in subject_df.iterrows():
        row_values = row.dropna().tolist()
        if len(row_values) == 0:
            continue
        if len(row_values) == 1 and "과" in row_values[0]:
            current_구분2 = row_values[0].replace(" ", "").replace("(", "").replace(")", "")
        elif any(x in str(row_values[0]) for x in ["일반", "진로"]):
            current_구분1 = row_values[0].strip()
            if len(row_values) > 1:
                for 과목명 in ",".join(row_values[1:]).replace("\t", "").split(","):
                    과목명 = 과목명.strip()
                    if 과목명:
                        subject_mappings.append({
                            "교과구분1": current_구분1,
                            "교과구분2": current_구분2,
                            "과목명": 과목명
                        })

    subject_map_df = pd.DataFrame(subject_mappings)

    # 포함 문자열 기반 매칭 함수
    def fuzzy_map_subject_info(과목명):
        filtered = subject_map_df[subject_map_df["과목명"].str.contains(과목명, na=False)]
        if not filtered.empty:
            return filtered.iloc[0]["교과구분1"], filtered.iloc[0]["교과구분2"]
        else:
            return None, None

    # ----------------------------------------
    # 2. PDF에서 성적 정보 추출
    # ----------------------------------------
    with pdfplumber.open(pdf_path) as pdf:
        pages = [pdf.pages[i].extract_text().replace("\n", " ") for i in [11, 12, 17]]  # 12,13,18쪽

    text = " ".join(pages)

    # 성적 정보 정규식 추출
    pattern = r"([가-힣ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+)\s+(\d+)\s+(\d+)/([\d.]+)\(([\d.]+)\)\s+([ABC])\((\d+)\)\s*(\d*)"
    matches = re.findall(pattern, text)

    # 데이터 저장
    records = []
    for i, match in enumerate(matches):
        과목 = match[0]
        단위 = int(match[1])
        원점수 = int(match[2])
        평균 = float(match[3])
        편차 = float(match[4])
        성취도 = match[5]
        수강자수 = int(match[6])
        석차등급 = match[7] if match[7] else None

        교과구분1, 교과구분2 = fuzzy_map_subject_info(과목)

        records.append({
            "학년/학기": 학기_정보[i],
            "교과 구분1": 교과구분1,
            "교과 구분2": 교과구분2,
            "과목명": 과목,
            "단위": 단위,
            "원점수": 원점수,
            "평균": 평균,
            "편차": 편차,
            "성취도": 성취도,
            "수강자수": 수강자수,
            "A": 1 if 성취도 == 'A' else 0,
            "B": 1 if 성취도 == 'B' else 0,
            "C": 1 if 성취도 == 'C' else 0,
            "석차등급": 석차등급
        })

    # ----------------------------------------
    # 3. DataFrame 구성 및 출력/저장
    # ----------------------------------------
    columns_order = [
        "학년/학기", "교과 구분1", "교과 구분2", "과목명", "단위",
        "원점수", "평균", "편차", "성취도", "수강자수",
        "A", "B", "C", "석차등급"
    ]

    df = pd.DataFrame(records)[columns_order]

    # CSV 저장 (선택)
    df.to_csv("완성된_성적표.csv", index=False)

    # 결과 확인
    print(df)


