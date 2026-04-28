"""에어비앤비 대금수령 보고서 CSV 파싱."""

from io import BytesIO, StringIO
from typing import Union

import pandas as pd

from .constants import TYPE_RESERVATION


REQUIRED_COLUMNS = [
    "날짜", "종류", "통화 단위", "호스팅 총수입", "서비스 수수료", "수입 발생 연도",
]

OPTIONAL_COLUMNS = [
    "입금 예정일", "예약 코드", "시작일", "종료일", "숙박일 수",
    "리스팅", "청소비", "신속 수령 수수료", "금액",
]

DATE_COLUMNS = ["날짜", "입금 예정일", "예약일", "시작일", "종료일"]

NUMERIC_COLUMNS = [
    "금액", "서비스 수수료", "신속 수령 수수료", "청소비",
    "호스팅 총수입", "에어비앤비가 수금 및 납부한 세금",
    "수입 발생 연도", "숙박일 수",
]


def read_csv_safely(source: Union[bytes, str, BytesIO, StringIO]) -> pd.DataFrame:
    """인코딩 자동 감지하여 CSV 읽기."""
    if isinstance(source, str):
        for encoding in ("utf-8", "utf-8-sig", "cp949"):
            try:
                return pd.read_csv(source, encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise ValueError("CSV 인코딩을 자동 감지할 수 없습니다 (UTF-8/CP949).")

    if isinstance(source, bytes):
        raw = source
    else:
        raw = source.read() if hasattr(source, "read") else source

    for encoding in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return pd.read_csv(BytesIO(raw), encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("CSV 인코딩을 자동 감지할 수 없습니다 (UTF-8/CP949).")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """컬럼명 앞뒤 공백 제거."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def validate_columns(df: pd.DataFrame) -> None:
    """필수 컬럼 누락 검증."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """숫자 컬럼의 쉼표 제거 후 float 변환."""
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(str).str.replace(",", "", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    """날짜 컬럼 datetime 변환."""
    df = df.copy()
    for col in DATE_COLUMNS:
        if col not in df.columns:
            continue
        df[col] = pd.to_datetime(df[col], format="%m/%d/%Y", errors="coerce")
    return df


def filter_reservations(df: pd.DataFrame) -> pd.DataFrame:
    """`종류 = 예약` 행만 추출."""
    if "종류" not in df.columns:
        raise ValueError("종류 컬럼이 없습니다.")
    return df[df["종류"] == TYPE_RESERVATION].copy().reset_index(drop=True)


def parse_airbnb_csv(source: Union[bytes, str, BytesIO, StringIO]) -> pd.DataFrame:
    """end-to-end 파싱 진입점."""
    df = read_csv_safely(source)
    df = normalize_columns(df)
    validate_columns(df)
    df = coerce_numeric(df)
    df = coerce_dates(df)
    df = filter_reservations(df)
    return df
