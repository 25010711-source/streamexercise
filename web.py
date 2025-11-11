import streamlit as st

st.title("간단한 사용자 입력 앱")

name = st.text_input("이름을 입력하세요:")
age = st.number_input("나이를 입력하세요:", min_value=0, max_value=120)

if st.button("확인"):
    st.success(f"안녕하세요 {name}님! 당신의 나이는 {age}살 입니다.")
