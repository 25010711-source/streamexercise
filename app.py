import streamlit as st
import pandas as pd
import numpy as np

st.title("데이터 시각화 예제")

# 랜덤 데이터 생성
data = pd.DataFrame(
    np.random.randn(50, 3),
    columns=["A", "B", "C"]
)

st.subheader("데이터프레임")
st.dataframe(data)

st.subheader("라인 차트")
st.line_chart(data)

