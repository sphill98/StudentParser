import pandas as pd

def compute_main_subject_averages(df: pd.DataFrame) -> dict:
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
        lambda g: (g["석차등급"] * g["단위"]).sum() / g["단위"].sum()
    ).round(2)

    # 딕셔너리로 반환
    return result.to_dict()