import streamlit as st

st.set_page_config(
    page_title="에어비앤비 호스트 세무 계산기",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 에어비앤비 호스트 세무 계산기")
st.markdown("---")

st.success("배포 환경 정상 동작 확인")

st.info(
    "본 서비스가 산출하는 세액은 참고용 추정치이며, "
    "실제 세무 신고를 대체하지 않습니다."
)

st.markdown("### 출시 예정일: 2026년 5월 5일")
