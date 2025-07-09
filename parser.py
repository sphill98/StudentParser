import pdfplumber
import pandas as pd
import re

def extract_grades(pdf_path, output_csv_path='output.csv'):
    # PDF 열기
    with pdfplumber.open(pdf_path) as pdf:
        text_all = ""
        for page in pdf.pages:
            text_all += page.extract_text() + "\n"

    # 성적 부분만 찾기
    pattern = r'교과\s+과목\s+단위수[\s\S]+?(?=과목 세 부 능 력)'
    match = re.search(pattern, text_all)

    if not match:
        print("성적 부분을 찾지 못했습니다.")
        return

    grades_text = match.group()

    # 줄 단위로 분리
    lines = grades_text.strip().split("\n")

    # 헤더
    data = []
    for line in lines:
        # 성적 데이터는 한 줄에 과목명, 단위수, 점수 등이 포함됨
        cols = re.split(r'\s+', line.strip())

        # 과목명 필터링 (ex: 국어, 수학, 물리학Ⅰ 등)
        if len(cols) >= 5 and any(sub in cols[0] for sub in ["국어", "수학", "영어", "물리", "화학", "생명", "정보", "기하", "미적분", "고급", "과학", "문학", "중국어"]):
            data.append(cols)

    # DataFrame 생성
    df = pd.DataFrame(data, columns=['과목', '단위수', '원점수/평균(표준편차)', '성취도(수강자수)', '석차등급', '비고'])

    # CSV 저장
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"성적 데이터가 {output_csv_path} 파일로 저장되었습니다.")


