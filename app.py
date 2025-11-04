import streamlit as st
import pandas as pd
import numpy as np

st.title('나의 첫 스트림릿 앱')

user_input = st.text_input("이름을 입력하세요:")

if st.button('인사하기')
    if user_input:
        st.write(f"안녕하세요, {user_input}님! ")
    else:
        st.write("이름을 입력하세요.")

x = st.slider('숫자를 선택하세요', 0, 100, 25)
st.write(f"선택한 숫자는 {x}입니다.")
