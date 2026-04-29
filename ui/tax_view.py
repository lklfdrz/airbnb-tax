"""세액 결과 화면."""
import pandas as pd
import streamlit as st
from tax_logic.constants import SEPARATE_TAX_THRESHOLD, SIMPLE_EXPENSE_THRESHOLD
from tax_logic.revenue import aggregate_yearly
from tax_logic.tax_calculator import calculate_all_scenarios, calculate_penalties, calculate_vat

VAT_STATUS_LABELS = {
    "unregistered":"사업자 미등록","simple_exempt":"간이과세 (면제)",
    "simple_taxable":"간이과세 (납부)","general":"일반과세",
}
SCENARIO_LABELS = {
    "simple_expense":"단순경비율 (82.9%)",
    "standard_expense":"기준경비율 (20.4%)",
    "actual_expense":"장부신고 (실제 경비)",
}


def _fmt(amount: float) -> str:
    return f"{int(round(amount)):,}원"


def render_tax_view(df: pd.DataFrame, is_registered: bool, input_vat: float, actual_expense: float):
    if df.empty:
        return

    summary        = aggregate_yearly(df)
    annual_revenue = summary["gross_revenue"]
    scenarios      = calculate_all_scenarios(annual_revenue, actual_expense)
    applicable     = [s for s in scenarios if s["applicable"]]
    best           = applicable[0] if applicable else scenarios[1]

    # Hero 세액 카드
    st.markdown(
        f"<div style='background:linear-gradient(160deg,#F0FDFA,#fff);border:1px solid #CCFBF1;"
        f"border-radius:16px;padding:28px 24px;text-align:center;margin-bottom:20px;"
        f"box-shadow:0 4px 16px rgba(20,184,166,.10)'>"
        f"<div style='font-size:11px;font-weight:600;color:#5C6868;letter-spacing:0.06em;margin-bottom:6px'>"
        f"{SCENARIO_LABELS.get(best['scenario'],'')} 기준 예상 종합소득세</div>"
        f"<div style='font-size:52px;font-weight:800;color:#14B8A6;letter-spacing:-0.025em;"
        f"font-variant-numeric:tabular-nums;line-height:1;white-space:nowrap'>{_fmt(best['total_tax'])}</div>"
        f"<div style='font-size:11px;color:#8A9494;margin-top:8px'>지방소득세 포함 · 가장 유리한 시나리오</div>"
        f"<div style='margin-top:12px;display:inline-flex;align-items:center;gap:6px;"
        f"background:#ECFDF5;border:1px solid #10B981;border-radius:999px;padding:4px 12px;"
        f"font-size:11px;font-weight:600;color:#047857'>✓ {len(applicable)}가지 시나리오 중 가장 낮은 금액</div></div>",
        unsafe_allow_html=True,
    )

    # 시나리오 비교
    st.markdown("**시나리오 비교**")
    for s in scenarios:
        is_best = s["scenario"] == best["scenario"] and s["applicable"]
        bg     = "#ECFDF5" if is_best else "#FFFFFF"
        border = "#6EE7B7" if is_best else "#DCE0E0"
        tc     = "#047857" if is_best else "#0F1717"
        badge  = " ← 이걸로 신고하세요" if is_best else ""
        na     = "" if s["applicable"] else "  (적용 불가)"
        st.markdown(
            f"<div style='background:{bg};border:1px solid {border};border-radius:11px;"
            f"padding:12px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center'>"
            f"<div><div style='font-size:13px;font-weight:600;color:#0F1717'>{SCENARIO_LABELS[s['scenario']]}{na}</div>"
            f"<div style='font-size:11px;color:#5C6868;margin-top:2px'>경비 {_fmt(s['expense'])} · 과세표준 {_fmt(s['taxable_income'])}</div></div>"
            f"<div style='font-size:16px;font-weight:700;color:{tc};font-variant-numeric:tabular-nums'>"
            f"{_fmt(s['total_tax'])}<span style='font-size:10px;color:#047857'>{badge}</span></div></div>",
            unsafe_allow_html=True,
        )

    # 부가세
    vat_result = calculate_vat(annual_revenue, input_vat, is_registered)
    with st.expander(f"부가가치세 — {VAT_STATUS_LABELS[vat_result['status']]}"):
        if vat_result["status"] in ("unregistered", "simple_exempt"):
            st.success("✅ 부가세 납부 의무 없음")
            if vat_result["status"] == "unregistered":
                st.caption("단, 미등록 가산세(매출 1%)가 발생할 수 있습니다.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("매출세액", _fmt(vat_result["output_vat"]))
            with c2: st.metric("매입세액", _fmt(vat_result["input_vat"]))
            with c3: st.metric("납부세액", _fmt(vat_result["payable_vat"]))

    if annual_revenue <= SEPARATE_TAX_THRESHOLD:
        st.info(f"💡 연 수입이 {SEPARATE_TAX_THRESHOLD:,}원 이하인 경우 기타소득 분리과세 선택 가능 (별도 검토 필요).")

    # 가산세 시뮬레이터
    with st.expander("지금 신고 안 하시면 얼마 더 내실까요? (가산세 시뮬레이터)"):
        days_late = st.slider("신고 지연 일수", 0, 365, 30, 30)
        result = calculate_penalties(payable_tax=best["total_tax"], annual_revenue=annual_revenue,
                                     is_unregistered=not is_registered, days_late=days_late)
        st.markdown(
            f"<div style='background:#FFFBEB;border:1px solid #FDE68A;border-radius:14px;"
            f"padding:20px;text-align:center;margin:12px 0'>"
            f"<div style='font-size:11px;font-weight:600;color:#B45309;margin-bottom:4px'>{days_late}일 지연 시 추가 납부액</div>"
            f"<div style='font-size:40px;font-weight:800;color:#B45309;font-variant-numeric:tabular-nums;white-space:nowrap'>"
            f"+{_fmt(result['total_penalty'])}</div></div>",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("무신고 가산세", _fmt(result["no_filing"]))
        with c2: st.metric("미등록 가산세", _fmt(result["no_registration"]))
        with c3: st.metric(f"납부지연({days_late}일)", _fmt(result["late_payment"]))
        st.markdown(
            "<div style='background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;"
            "padding:14px 16px;margin-top:14px'>"
            "<div style='font-size:13px;font-weight:700;color:#0F766E;margin-bottom:4px'>"
            "지금 신고하시면 이 금액은 안 내셔도 됩니다.</div>"
            "<div style='font-size:12px;color:#5C6868;line-height:1.55'>"
            "국세청 홈택스(hometax.go.kr) 또는 세무사를 통해 신고하실 수 있어요.<br>"
            "막막하시면 아래 엑셀 파일을 세무사에게 전달하시면 됩니다.</div></div>",
            unsafe_allow_html=True,
        )

    # 엑셀 다운로드
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_btn, col_info = st.columns([2, 3])
    with col_btn:
        st.button("세무사 제출용 엑셀 받기 (3,000원)", disabled=True, help="5월 5일 정식 출시 시 활성화 예정")
    with col_info:
        st.caption("거래내역 + 매출 인식일 + 합계 시트 포함 · 국세청 신고 기준 포맷")
