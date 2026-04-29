"""공통 컴포넌트 + CSS 주입."""
import os
import streamlit as st
from tax_logic.constants import DISCLAIMER


def inject_css():
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_header():
    col_logo, col_text = st.columns([1, 11])
    with col_logo:
        st.markdown("<div style='font-size:36px;line-height:1;padding-top:6px'>🏡</div>", unsafe_allow_html=True)
    with col_text:
        st.markdown(
            "<div style='font-size:22px;font-weight:800;letter-spacing:-0.025em;color:#0F1717;padding-top:4px'>"
            "비앤비 택스가드"
            "<span style='font-size:13px;font-weight:500;color:#5C6868;margin-left:10px'>"
            "에어비앤비 호스트 세무 계산기</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:1px;background:#DCE0E0;margin:16px 0 20px'></div>", unsafe_allow_html=True)


def render_disclaimer(location: str = "main"):
    html = f"<div style='background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:12px 16px;font-size:12px;color:#B45309;line-height:1.5;margin:16px 0'>⚠️ {DISCLAIMER}</div>"
    if location == "sidebar":
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def render_empty_state(message: str = "왼쪽 사이드바에서 CSV 파일을 올려주세요."):
    st.markdown(
        "<div style='text-align:center;padding:60px 20px;color:#5C6868'>"
        "<div style='font-size:48px;margin-bottom:16px'>📤</div>"
        "<div style='font-size:20px;font-weight:700;color:#0F1717;margin-bottom:8px'>CSV 파일을 올려주세요</div>"
        "<div style='font-size:14px;color:#5C6868;line-height:1.6;max-width:400px;margin:0 auto'>"
        "에어비앤비 앱 → 호스팅 수입 → 보고서에서<br>대금수령 내역 CSV를 받아 올려주시면<br>예상 세액을 자동으로 계산해 드려요.</div></div>",
        unsafe_allow_html=True,
    )


def render_step_header(step_num: int, title: str):
    st.subheader(f"{step_num}. {title}")
