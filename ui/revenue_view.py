"""매출 요약 화면."""
import pandas as pd
import plotly.express as px
import streamlit as st
from tax_logic.constants import RECOGNITION_AIRBNB_YEAR
from tax_logic.revenue import aggregate_by_listing, aggregate_monthly, aggregate_yearly


def _fmt(amount: float) -> str:
    return f"{int(round(amount)):,}원"


def render_revenue_view(df: pd.DataFrame, year: int, method: str):
    if df.empty:
        st.warning(f"⚠️ {year}년에 해당하는 예약 내역이 없습니다.")
        return

    summary = aggregate_yearly(df)

    st.markdown(
        f"<div style='background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;"
        f"padding:14px 18px;display:flex;align-items:center;gap:12px;margin-bottom:20px'>"
        f"<div style='width:32px;height:32px;border-radius:50%;background:#14B8A6;"
        f"display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#fff;font-size:14px;font-weight:700'>✓</div>"
        f"<div><div style='font-size:13px;font-weight:700;color:#0F766E'>CSV 정리가 완료됐어요</div>"
        f"<div style='font-size:11px;color:#5C6868;margin-top:2px'>"
        f"Payout·기타 크레딧은 자동으로 제외됐습니다 · {year}년 예약 {summary['reservation_count']}건</div></div></div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("신고용 총매출", _fmt(summary["gross_revenue"]), help="호스팅 총수입 합계. 국세청 신고 기준.")
    with col2: st.metric("순수령액", _fmt(summary["net_received"]), help="서비스 수수료 차감 후 실수령액.")
    with col3: st.metric("서비스 수수료", _fmt(summary["service_fee"]), help="종소세 신고 시 필요경비로 공제 가능.")
    with col4: st.metric("예약 건수", f"{summary['reservation_count']}건")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    chart_method = method
    if method == RECOGNITION_AIRBNB_YEAR:
        chart_method = "transaction"
        st.caption("ℹ️ 월별 차트는 거래일 기준으로 표시됩니다.")

    monthly = aggregate_monthly(df, chart_method)
    if not monthly.empty:
        fig = px.bar(monthly, x="month", y="gross_revenue",
                     labels={"month": "월", "gross_revenue": "매출 (원)"},
                     height=300, color_discrete_sequence=["#14B8A6"])
        fig.update_layout(margin=dict(l=0,r=0,t=8,b=0), plot_bgcolor="white",
                          paper_bgcolor="white", font_family="Pretendard")
        fig.update_xaxes(type="category", showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#EEF0F0")
        st.markdown("**월별 매출 추이**")
        st.plotly_chart(fig, use_container_width=True)

    listing_agg = aggregate_by_listing(df)
    if not listing_agg.empty and len(listing_agg) > 1:
        with st.expander("숙소별 매출 보기"):
            d = listing_agg.copy()
            d["gross_revenue"] = d["gross_revenue"].apply(_fmt)
            d.columns = ["숙소", "매출", "예약 건수"]
            st.dataframe(d, use_container_width=True, hide_index=True)

    with st.expander("예약 상세 내역 보기"):
        d = df.copy()
        for col in ["시작일", "종료일", "날짜"]:
            if col in d.columns:
                d[col] = d[col].dt.strftime("%Y-%m-%d")
        cols = [c for c in ["예약 코드","시작일","종료일","숙박일 수","호스팅 총수입","서비스 수수료","청소비"] if c in d.columns]
        st.dataframe(d[cols], use_container_width=True, hide_index=True)
