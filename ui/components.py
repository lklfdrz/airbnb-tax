"""공통 Streamlit 컴포넌트."""

import streamlit as st

from tax_logic.constants import DISCLAIMER


def render_header():
    st.title("🏠 에어비앤비 호스트 세무 계산기")
    st.caption("CSV 업로드만으로 예상 부가세·종합소득세를 산출합니다.")
    st.markdown("---")


def render_disclaimer(location: str = "main"):
    if location == "sidebar":
        st.sidebar.caption(f"⚠️ {DISCLAIMER}")
    else:
        st.info(f"⚠️ {DISCLAIMER}")


def render_empty_state(message: str = "왼쪽에서 CSV 파일을 업로드해주세요."):
    st.info(f"📤 {message}")


def render_step_header(step_num: int, title: str):
    st.subheader(f"{step_num}. {title}")
