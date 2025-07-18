import pandas as pd


def compute_main_subject_averages(df: pd.DataFrame) -> dict:
    # 1, 2학년 성적만 필터링
    valid_grades = ["1학년 1학기", "1학년 2학기", "2학년 1학기", "2학년 2학기"]
    df = df.loc[df["학년/학기"].isin(valid_grades)].copy()

    # 숫자형으로 변환
    df["석차등급"] = pd.to_numeric(df["석차등급"], errors="coerce")
    df["단위"] = pd.to_numeric(df["단위"], errors="coerce")

    # NaN 제거 + 일반선택 필터링
    valid = df.dropna(subset=["석차등급", "단위"])
    valid = valid[valid["교과 구분1"] == "일반선택"]

    # 교과구분2 → 통합 교과 이름 매핑
    subject_map = {
        "국어": "국어",
        "수학": "수학",
        "영어": "영어",
        "사회": "사탐",
        "과학": "과탐"
    }

    valid = valid[valid["교과 구분2"].isin(subject_map.keys())].copy()
    valid["통합교과"] = valid["교과 구분2"].map(subject_map)
    # 가중 평균 계산
    result = valid.groupby("통합교과").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)

    # 딕셔너리로 반환
    return result.to_dict()


def compute_science_subject_averages(df: pd.DataFrame) -> dict:
    # 1, 2학년 성적만 필터링
    valid_grades = ["1학년 1학기", "1학년 2학기", "2학년 1학기", "2학년 2학기"]
    df = df.loc[df["학년/학기"].isin(valid_grades)].copy()

    # 숫자형으로 변환
    df["석차등급"] = pd.to_numeric(df["석차등급"], errors="coerce")
    df["단위"] = pd.to_numeric(df["단위"], errors="coerce")

    # NaN 제거 + 일반선택 필터링
    valid = df.dropna(subset=["석차등급", "단위"])
    valid = valid[valid["교과 구분1"] == "일반선택"]

    # 과학 교과만 필터링
    science_subjects = ["통합과학", "물리학Ⅰ", "화학Ⅰ", "생명과학Ⅰ", "지구과학Ⅰ"]
    valid = valid[valid["과목명"].isin(science_subjects)].copy()
    # 가중 평균 계산
    result = valid.groupby("과목명").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    # 딕셔너리로 반환
    return result.to_dict()


def compute_liberal_subject_averages(df: pd.DataFrame) -> dict:
    # 1, 2학년 성적만 필터링
    valid_grades = ["1학년 1학기", "1학년 2학기", "2학년 1학기", "2학년 2학기"]
    df = df.loc[df["학년/학기"].isin(valid_grades)].copy()

    # 숫자형으로 변환
    df["석차등급"] = pd.to_numeric(df["석차등급"], errors="coerce")
    df["단위"] = pd.to_numeric(df["단위"], errors="coerce")

    # NaN 제거 + 일반선택 필터링
    valid = df.dropna(subset=["석차등급", "단위"])
    valid = valid[valid["교과 구분1"] == "일반선택"]

    # 사회 교과만 필터링
    science_subjects = ["통합사회", "한국사", "한국지리", "세계지리", "세계사", "동아시아사", "경제", "정치와 법", "생활과 윤리", "윤리와 사상", "사회·문화"]
    valid = valid[valid["과목명"].isin(science_subjects)].copy()
    # 가중 평균 계산
    result = valid.groupby("과목명").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    # 딕셔너리로 반환
    return result.to_dict()