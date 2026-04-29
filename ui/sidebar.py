"""사이드바 — 결정 포인트 최소화."""
import streamlit as st
from tax_logic.constants import (
    RECOGNITION_AIRBNB_YEAR, RECOGNITION_CHECKIN,
    RECOGNITION_PAYOUT, RECOGNITION_TRANSACTION,
)

RECOGNITION_LABELS = {
    RECOGNITION_AIRBNB_YEAR: "수입 발생 연도 (권장)",
    RECOGNITION_CHECKIN:     "체크인일 기준",
    RECOGNITION_TRANSACTION: "거래일 기준",
    RECOGNITION_PAYOUT:      "입금 예정일 기준",
}


def render_sidebar() -> dict:
    st.sidebar.markdown(
        "<div style='display:flex;align-items:center;gap:8px;padding-bottom:16px;"
        "border-bottom:1px solid #DCE0E0;margin-bottom:20px'>"
        "<span style='font-size:22px'>🏡</span>"
        "<span style='font-size:14px;font-weight:700;color:#0F1717'>비앤비 택스가드</span></div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("<p style='font-size:12px;font-weight:600;color:#5C6868;margin-bottom:4px'>CSV 파일</p>", unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader(
        "에어비앤비 대금수령 보고서", type=["csv"],
        label_visibility="collapsed",
        help="에어비앤비 앱 → 호스팅 수입 → 보고서 → 내보내기",
    )
    if not uploaded_file:
        st.sidebar.caption("에어비앤비 앱 → 호스팅 수입 → 보고서 → 내보내기")

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:12px;font-weight:600;color:#5C6868;margin-bottom:4px'>신고 연도</p>", unsafe_allow_html=True)
    year = st.sidebar.selectbox(
        "귀속 연도",
        options=list(range(2026, 2022, -1)),
        index=1,
        label_visibility="collapsed",
    )

    # 기본값 초기화
    is_registered      = False
    recognition_method = RECOGNITION_AIRBNB_YEAR
    input_vat          = 0.0
    actual_expense     = 0.0

    with st.sidebar.expander("고급 설정 (대부분 기본값으로 충분합니다)", expanded=False):
        is_registered = st.radio(
            "사업자 등록 여부", options=[False, True],
            format_func=lambda x: "등록함" if x else "미등록",
            index=0, horizontal=True,
        )
        recognition_method = st.radio(
            "매출 인식 시점",
            options=list(RECOGNITION_LABELS.keys()),
            format_func=lambda x: RECOGNITION_LABELS[x],
            index=0,
            help="'수입 발생 연도' 기준이 가장 안전합니다.",
        )
        input_vat = float(st.number_input("매입세액 (원)", min_value=0, value=0, step=10000, help="일반과세자만. 영수증·세금계산서 합계."))
        actual_expense = float(st.number_input("실제 필요경비 (원)", min_value=0, value=0, step=100000, help="장부신고 시나리오용."))

    return {
        "uploaded_file":      uploaded_file,
        "is_registered":      is_registered,
        "year":               year,
        "recognition_method": recognition_method,
        "input_vat":          input_vat,
        "actual_expense":     actual_expense,
    }
