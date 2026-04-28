"""매출 요약 화면."""

import pandas as pd
import plotly.express as px
import streamlit as st

from tax_logic.constants import RECOGNITION_AIRBNB_YEAR
from tax_logic.revenue import aggregate_by_listing, aggregate_monthly, aggregate_yearly


def _format_krw(amount: float) -> str:
    return f"{int(round(amount)):,}원"


def render_yearly_metrics(df: pd.DataFrame, year: int):
    summary = aggregate_yearly(df)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{year}년 신고용 총매출", _format_krw(summary["gross_revenue"]),
                  help="호스팅 총수입 합계. 국세청 신고 기준.")
    with col2:
        st.metric("순수령액", _format_krw(summary["net_received"]),
                  help="호스트 계좌 입금 기준 (서비스 수수료 차감 후).")
    with col3:
        st.metric("서비스 수수료", _format_krw(summary["service_fee"]),
                  help="종소세 신고 시 필요경비로 인정.")
    with col4:
        st.metric("예약 건수", f"{summary['reservation_count']}건")


def render_monthly_chart(df: pd.DataFrame, method: str):
    """월별 매출 차트.

    매출 인식 시점이 'airbnb_year'면 월별 분포가 무의미하므로
    거래일 기준으로 자동 전환하여 그린다 (사용자 안내 포함).
    """
    chart_method = method
    if method == RECOGNITION_AIRBNB_YEAR:
        chart_method = "transaction"
        st.caption(
            "ℹ️ 월별 차트는 '거래일' 기준으로 표시됩니다 "
            "('수입 발생 연도'는 연도만 있어 월별 분포 표현 불가)."
        )

    monthly = aggregate_monthly(df, chart_method)
    if monthly.empty:
        st.info("월별 집계할 데이터가 없습니다.")
        return

    st.markdown("#### 월별 매출 추이")
    fig = px.bar(
        monthly,
        x="month",
        y="gross_revenue",
        labels={"month": "월", "gross_revenue": "매출 (원)"},
        height=350,
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(type="category")
    st.plotly_chart(fig, use_container_width=True)


def render_listing_breakdown(df: pd.DataFrame):
    listing_agg = aggregate_by_listing(df)
    if listing_agg.empty or len(listing_agg) <= 1:
        return
    st.markdown("#### 숙소별 매출")
    listing_display = listing_agg.copy()
    listing_display["gross_revenue"] = listing_display["gross_revenue"].apply(_format_krw)
    listing_display.columns = ["숙소", "매출", "예약 건수"]
    st.dataframe(listing_display, use_container_width=True, hide_index=True)


def render_detail_table(df: pd.DataFrame):
    """예약 상세 — 날짜 포맷 정리, 표시 컬럼 최소화."""
    with st.expander("📋 예약 상세 내역 보기"):
        display = df.copy()
        # 날짜 컬럼을 YYYY-MM-DD 문자열로 (00:00:00 잘림 방지)
        for col in ["시작일", "종료일", "날짜"]:
            if col in display.columns:
                display[col] = display[col].dt.strftime("%Y-%m-%d")
        display_cols = [
            c for c in [
                "예약 코드", "시작일", "종료일", "숙박일 수",
                "호스팅 총수입", "서비스 수수료", "청소비",
            ] if c in display.columns
        ]
        st.dataframe(display[display_cols], use_container_width=True, hide_index=True)


def render_revenue_view(df: pd.DataFrame, year: int, method: str):
    if df.empty:
        st.warning(f"⚠️ {year}년에 해당하는 예약 내역이 없습니다.")
        return
    st.header(f"📊 {year}년 매출 요약")
    render_yearly_metrics(df, year)
    st.markdown("---")
    render_monthly_chart(df, method)
    render_listing_breakdown(df)
    render_detail_table(df)
