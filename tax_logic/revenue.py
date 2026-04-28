"""매출 인식 시점 선택 및 연도/월별 집계."""

import pandas as pd

from .constants import (
    RECOGNITION_AIRBNB_YEAR,
    RECOGNITION_CHECKIN,
    RECOGNITION_PAYOUT,
    RECOGNITION_TRANSACTION,
)


def get_recognition_date(df: pd.DataFrame, method: str) -> pd.Series:
    """선택된 매출 인식 방법에 따라 날짜 시리즈 반환."""
    if method == RECOGNITION_CHECKIN:
        return df["시작일"]
    if method == RECOGNITION_TRANSACTION:
        return df["날짜"]
    if method == RECOGNITION_PAYOUT:
        return df["입금 예정일"]
    if method == RECOGNITION_AIRBNB_YEAR:
        return pd.to_datetime(
            df["수입 발생 연도"].astype("Int64").astype(str) + "-01-01",
            errors="coerce",
        )
    raise ValueError(f"알 수 없는 인식 방법: {method}")


def filter_by_year(df: pd.DataFrame, year: int, method: str) -> pd.DataFrame:
    """특정 연도 매출만 필터링."""
    df = df.copy()
    recognition_date = get_recognition_date(df, method)
    mask = recognition_date.dt.year == year
    return df[mask].reset_index(drop=True)


def aggregate_yearly(df: pd.DataFrame) -> dict:
    """연 매출 요약."""
    if df.empty:
        return {
            "gross_revenue": 0.0,
            "net_received": 0.0,
            "service_fee": 0.0,
            "cleaning_fee": 0.0,
            "reservation_count": 0,
        }
    return {
        "gross_revenue": float(df["호스팅 총수입"].fillna(0).sum()),
        "net_received": float(df["금액"].fillna(0).sum()) if "금액" in df.columns else 0.0,
        "service_fee": float(df["서비스 수수료"].fillna(0).sum()),
        "cleaning_fee": float(df["청소비"].fillna(0).sum()) if "청소비" in df.columns else 0.0,
        "reservation_count": int(len(df)),
    }


def aggregate_monthly(df: pd.DataFrame, method: str) -> pd.DataFrame:
    """월별 매출 집계."""
    if df.empty:
        return pd.DataFrame(columns=["month", "gross_revenue", "reservation_count"])

    df = df.copy()
    recognition_date = get_recognition_date(df, method)
    df["_month"] = recognition_date.dt.to_period("M").astype(str)

    grouped = (
        df.groupby("_month")
        .agg(
            gross_revenue=("호스팅 총수입", lambda s: s.fillna(0).sum()),
            reservation_count=("호스팅 총수입", "count"),
        )
        .reset_index()
        .rename(columns={"_month": "month"})
    )
    grouped["gross_revenue"] = grouped["gross_revenue"].astype(float)
    return grouped.sort_values("month").reset_index(drop=True)


def aggregate_by_listing(df: pd.DataFrame) -> pd.DataFrame:
    """리스팅별 매출 집계."""
    if df.empty or "리스팅" not in df.columns:
        return pd.DataFrame(columns=["listing", "gross_revenue", "reservation_count"])

    grouped = (
        df.groupby("리스팅", dropna=False)
        .agg(
            gross_revenue=("호스팅 총수입", lambda s: s.fillna(0).sum()),
            reservation_count=("호스팅 총수입", "count"),
        )
        .reset_index()
        .rename(columns={"리스팅": "listing"})
    )
    grouped["gross_revenue"] = grouped["gross_revenue"].astype(float)
    return grouped.sort_values("gross_revenue", ascending=False).reset_index(drop=True)
