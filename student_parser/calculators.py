import pandas as pd

def _get_valid_semesters(curr_grade: int) -> list[str]:
    """현재 학년에 따라 유효한 학기 목록을 반환합니다."""
    all_semesters = ["1학년 1학기", "1학년 2학기", "2학년 1학기", "2학년 2학기", "3학년 1학기", "3학년 2학기"]
    if curr_grade == 0:  # 2학년 재학
        return all_semesters[:4]
    elif curr_grade == 1:  # 3학년 재학
        return all_semesters[:5]
    else:  # 졸업
        return all_semesters

def _prepare_data(df: pd.DataFrame, curr_grade: int) -> pd.DataFrame:
    """데이터프레임의 공통 전처리 작업을 수행합니다."""
    if df.empty:
        return pd.DataFrame()

    valid_semesters = _get_valid_semesters(curr_grade)
    df = df.loc[df["학년/학기"].isin(valid_semesters)].copy()
    if df.empty:
        return pd.DataFrame()

    df["석차등급"] = pd.to_numeric(df["석차등급"], errors="coerce")
    df["단위"] = pd.to_numeric(df["단위"], errors="coerce")

    valid = df.dropna(subset=["석차등급", "단위"])
    valid = valid[valid["교과 구분1"] == "일반선택"]
    return valid

def compute_main_subject_averages(df: pd.DataFrame, curr_grade: int) -> dict:
    """주요 교과(국어, 수학, 영어, 사회, 과학)의 평균 등급을 계산합니다."""
    valid_df = _prepare_data(df, curr_grade)
    if valid_df.empty:
        return {}

    subject_map = {
        "국어": "국어", "수학": "수학", "영어": "영어",
        "사회": "사탐", "과학": "과탐"
    }
    
    valid_df = valid_df[valid_df["교과 구분2"].isin(subject_map.keys())].copy()
    if valid_df.empty:
        return {}
        
    valid_df["통합교과"] = valid_df["교과 구분2"].map(subject_map)
    
    result = valid_df.groupby("통합교과").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    
    return result.to_dict()

def compute_science_subject_averages(df: pd.DataFrame, curr_grade: int) -> dict:
    """과학탐구 과목들의 평균 등급을 계산합니다."""
    valid_df = _prepare_data(df, curr_grade)
    if valid_df.empty:
        return {}

    science_subjects = ["통합과학", "물리학Ⅰ", "화학Ⅰ", "생명과학Ⅰ", "지구과학Ⅰ"]
    valid_df = valid_df[valid_df["과목명"].isin(science_subjects)].copy()
    if valid_df.empty:
        return {}

    result = valid_df.groupby("과목명").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    
    return result.to_dict()

def compute_liberal_subject_averages(df: pd.DataFrame, curr_grade: int) -> dict:
    """사회탐구 과목들의 평균 등급을 계산합니다."""
    valid_df = _prepare_data(df, curr_grade)
    if valid_df.empty:
        return {}

    liberal_subjects = [
        "통합사회", "한국사", "한국지리", "세계지리", "세계사", "동아시아사",
        "경제", "정치와 법", "생활과 윤리", "윤리와 사상", "사회·문화"
    ]
    valid_df = valid_df[valid_df["과목명"].isin(liberal_subjects)].copy()
    if valid_df.empty:
        return {}

    result = valid_df.groupby("과목명").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    
    return result.to_dict()

def compute_overall_trend(df: pd.DataFrame, curr_grade: int) -> list:
    """전체 과목의 학기별 평균 등급 추이를 계산합니다.
    :rtype: list
    """
    valid_df = _prepare_data(df, curr_grade)
    if valid_df.empty:
        return []

    trend = valid_df.groupby("학년/학기").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    
    valid_semesters = _get_valid_semesters(curr_grade)
    return [trend.get(s) for s in valid_semesters]

def compute_major_trend(df: pd.DataFrame, curr_grade: int, major_subjects: list[str]) -> list:
    """주요 과목의 학기별 평균 등급 추이를 계산합니다."""
    valid_df = _prepare_data(df, curr_grade)
    if valid_df.empty:
        return []

    valid_df = valid_df[valid_df["교과 구분2"].isin(major_subjects)].copy()
    if valid_df.empty:
        return []

    trend = valid_df.groupby("학년/학기").apply(
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum(),
        include_groups=False
    ).round(2)
    
    valid_semesters = _get_valid_semesters(curr_grade)
    return [trend.get(s) for s in valid_semesters]