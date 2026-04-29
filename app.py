"""에어비앤비 호스트 세무 계산기 - Streamlit 진입점."""

import streamlit as st

from tax_logic.csv_parser import parse_airbnb_csv
from tax_logic.revenue import filter_by_year
from ui.components import render_disclaimer, render_empty_state, render_header, inject_css
from ui.revenue_view import render_revenue_view
from ui.sidebar import render_sidebar
from ui.tax_view import render_tax_view


def main():
    st.set_page_config(
        page_title="에어비앤비 호스트 세무 계산기",
        page_icon="🏠",
        layout="wide",
    )

    inject_css()
    render_header()
    inputs = render_sidebar()
    render_disclaimer(location="sidebar")

    uploaded_file = inputs["uploaded_file"]
    if uploaded_file is None:
        render_empty_state()
        render_disclaimer(location="main")
        return

    try:
        df_all = parse_airbnb_csv(uploaded_file.read())
    except ValueError as e:
        st.error(f"❌ CSV 파싱 실패: {e}")
        return
    except Exception as e:
        st.error(f"❌ 예기치 못한 오류: {e}")
        st.exception(e)
        return

    if df_all.empty:
        st.warning("⚠️ CSV에서 예약 행을 찾을 수 없습니다. 파일을 확인해주세요.")
        return

    df_year = filter_by_year(df_all, year=inputs["year"], method=inputs["recognition_method"])

    render_revenue_view(df=df_year, year=inputs["year"], method=inputs["recognition_method"])

    if not df_year.empty:
        st.markdown("---")
        render_tax_view(
            df=df_year,
            is_registered=inputs["is_registered"],
            input_vat=inputs["input_vat"],
            actual_expense=inputs["actual_expense"],
        )

    st.markdown("---")
    render_disclaimer(location="main")


if __name__ == "__main__":
    main()
