"""세액 계산 화면."""

import pandas as pd
import streamlit as st

from tax_logic.constants import SEPARATE_TAX_THRESHOLD, SIMPLE_EXPENSE_THRESHOLD
from tax_logic.revenue import aggregate_yearly
from tax_logic.tax_calculator import (
    calculate_all_scenarios, calculate_penalties, calculate_vat,
)


VAT_STATUS_LABELS = {
    "unregistered": "사업자 미등록",
    "simple_exempt": "간이과세 (면제)",
    "simple_taxable": "간이과세 (납부)",
    "general": "일반과세",
}

SCENARIO_LABELS = {
    "simple_expense": "단순경비율 (82.9%)",
    "standard_expense": "기준경비율 (20.4%)",
    "actual_expense": "장부신고 (실제 경비)",
}


def _format_krw(amount: float) -> str:
    return f"{int(round(amount)):,}원"


def render_revenue_warnings(annual_revenue: float):
    if annual_revenue <= SEPARATE_TAX_THRESHOLD:
        st.info(
            f"💡 연 수입이 {SEPARATE_TAX_THRESHOLD:,}원 이하인 경우, "
            "기타소득 분리과세를 선택할 수 있습니다 (별도 검토 필요)."
        )
    if annual_revenue >= SIMPLE_EXPENSE_THRESHOLD:
        st.warning(
            f"⚠️ 연 수입 {SIMPLE_EXPENSE_THRESHOLD:,}원 이상이므로 "
            "단순경비율 적용이 불가능하며, 기준경비율 또는 장부신고가 필요합니다."
        )


def render_vat_section(annual_revenue: float, input_vat: float, is_registered: bool):
    st.subheader("A. 부가가치세")
    vat_result = calculate_vat(annual_revenue, input_vat, is_registered)
    status_label = VAT_STATUS_LABELS[vat_result["status"]]
    st.caption(f"판정 결과: **{status_label}**")

    if vat_result["status"] in ("unregistered", "simple_exempt"):
        st.success("✅ 부가세 납부 의무 없음")
        if vat_result["status"] == "unregistered":
            st.caption("단, 미등록 가산세(매출 1%)가 발생할 수 있습니다. 아래 가산세 항목 참고.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("매출세액", _format_krw(vat_result["output_vat"]))
    with col2:
        st.metric("매입세액", _format_krw(vat_result["input_vat"]))
    with col3:
        st.metric("**납부세액**", _format_krw(vat_result["payable_vat"]))


def render_scenario_table(annual_revenue: float, actual_expense: float):
    st.subheader("B. 종합소득세 (시나리오 비교)")
    scenarios = calculate_all_scenarios(annual_revenue, actual_expense)
    rows = []
    for s in scenarios:
        applicable_mark = "✅" if s["applicable"] else "❌"
        rows.append({
            "시나리오": SCENARIO_LABELS[s["scenario"]],
            "적용 가능": applicable_mark,
            "필요경비": _format_krw(s["expense"]),
            "과세표준": _format_krw(s["taxable_income"]),
            "산출세액": _format_krw(s["income_tax"]),
            "지방소득세": _format_krw(s["local_tax"]),
            "총 세액": _format_krw(s["total_tax"]),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    applicable_scenarios = [s for s in scenarios if s["applicable"]]
    if applicable_scenarios:
        cheapest = min(applicable_scenarios, key=lambda s: s["total_tax"])
        st.success(
            f"💡 적용 가능한 시나리오 중 세액이 가장 낮은 것은 "
            f"**{SCENARIO_LABELS[cheapest['scenario']]}** ({_format_krw(cheapest['total_tax'])})."
        )


def render_penalty_section(payable_tax: float, annual_revenue: float, is_registered: bool):
    with st.expander("C. 가산세 시뮬레이션 (지금 신고 안 하면 얼마 더 내야 하는가)"):
        days_late = st.slider("납부 지연 일수", 0, 365, 30, 30)
        result = calculate_penalties(
            payable_tax=payable_tax,
            annual_revenue=annual_revenue,
            is_unregistered=not is_registered,
            days_late=days_late,
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("무신고 가산세", _format_krw(result["no_filing"]))
        with col2:
            st.metric("미등록 가산세", _format_krw(result["no_registration"]))
        with col3:
            st.metric(f"납부지연 ({days_late}일)", _format_krw(result["late_payment"]))
        with col4:
            st.metric("**가산세 합계**", _format_krw(result["total_penalty"]))


def render_export_section():
    with st.expander("D. 소명용 엑셀 다운로드 (유료)"):
        st.info(
            "🚧 5월 5일 정식 런칭 시 활성화 예정. "
            "거래내역 + 매출 인식일 + 합계가 포함된 세무서 제출용 엑셀 파일."
        )
        st.button("엑셀 다운로드 (준비 중)", disabled=True)


def render_tax_view(df: pd.DataFrame, is_registered: bool, input_vat: float, actual_expense: float):
    if df.empty:
        return
    summary = aggregate_yearly(df)
    annual_revenue = summary["gross_revenue"]

    st.header("💰 예상 세액")
    render_revenue_warnings(annual_revenue)
    render_vat_section(annual_revenue, input_vat, is_registered)
    st.markdown("---")
    render_scenario_table(annual_revenue, actual_expense)
    st.markdown("---")

    scenarios = calculate_all_scenarios(annual_revenue, actual_expense)
    applicable = [s for s in scenarios if s["applicable"]]
    base_tax = applicable[0]["total_tax"] if applicable else scenarios[1]["total_tax"]
    render_penalty_section(base_tax, annual_revenue, is_registered)
    render_export_section()
