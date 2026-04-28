"""사이드바 입력 위젯."""

import streamlit as st

from tax_logic.constants import (
    RECOGNITION_AIRBNB_YEAR,
    RECOGNITION_CHECKIN,
    RECOGNITION_PAYOUT,
    RECOGNITION_TRANSACTION,
)


RECOGNITION_LABELS = {
    RECOGNITION_AIRBNB_YEAR: "수입 발생 연도 (에어비앤비 권장)",
    RECOGNITION_CHECKIN: "체크인일 기준 (시작일)",
    RECOGNITION_TRANSACTION: "거래일 기준 (날짜)",
    RECOGNITION_PAYOUT: "입금 예정일 기준 (현금주의)",
}


def render_csv_uploader():
    st.sidebar.markdown("### 1️⃣ CSV 업로드")
    return st.sidebar.file_uploader(
        "에어비앤비 대금수령 보고서",
        type=["csv"],
        help="에어비앤비 > 호스팅 수입 > 보고서 다운로드 메뉴에서 받은 CSV 파일",
    )


def render_business_status():
    st.sidebar.markdown("### 2️⃣ 사업자 정보")
    return st.sidebar.radio(
        "사업자 등록 여부",
        options=[False, True],
        format_func=lambda x: "등록함" if x else "미등록",
        index=0,
        horizontal=True,
    )


def render_year_selector():
    st.sidebar.markdown("### 3️⃣ 신고 연도")
    current_year = 2026
    options = list(range(current_year, current_year - 4, -1))
    return st.sidebar.selectbox("귀속 연도", options=options, index=1)


def render_recognition_method():
    st.sidebar.markdown("### 4️⃣ 매출 인식 시점")
    return st.sidebar.radio(
        "기준일",
        options=list(RECOGNITION_LABELS.keys()),
        format_func=lambda x: RECOGNITION_LABELS[x],
        index=0,
        help=(
            "에어비앤비가 권장하는 '수입 발생 연도' 기준이 가장 안전합니다. "
            "체크인일·거래일·입금일 기준은 연도 경계 예약에서 다른 결과를 보일 수 있습니다."
        ),
    )


def render_optional_inputs():
    st.sidebar.markdown("### 5️⃣ 추가 입력 (선택)")
    with st.sidebar.expander("매입세액·실제 경비 입력"):
        input_vat = st.number_input(
            "매입세액 (원)", min_value=0, value=0, step=10000,
            help="일반과세자만 해당. 영수증·세금계산서 합계.",
        )
        actual_expense = st.number_input(
            "실제 필요경비 (원)", min_value=0, value=0, step=100000,
            help="장부신고 시나리오용. 임대료·청소비·소모품·플랫폼 수수료 등.",
        )
    return {
        "input_vat": float(input_vat),
        "actual_expense": float(actual_expense),
    }


def render_sidebar() -> dict:
    st.sidebar.title("입력")
    uploaded_file = render_csv_uploader()
    is_registered = render_business_status()
    year = render_year_selector()
    method = render_recognition_method()
    optional = render_optional_inputs()
    return {
        "uploaded_file": uploaded_file,
        "is_registered": is_registered,
        "year": year,
        "recognition_method": method,
        **optional,
    }
