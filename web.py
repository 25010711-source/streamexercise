import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="주기율표 탐험 퀘스트", page_icon="🧪", layout="wide")

st.title("🧪 주기율표 탐험 퀘스트")
st.markdown("**원소를 클릭해 정보를 확인하고 퀴즈에 도전하세요!**")

# --- 간단한 주기율표 데이터 ---
data = [
    {"symbol": "H",  "name": "Hydrogen", "atomic_number": 1, "group": 1, "period": 1, "type": "비금속"},
    {"symbol": "He", "name": "Helium",   "atomic_number": 2, "group": 18, "period": 1, "type": "비활성 기체"},
    {"symbol": "Li", "name": "Lithium",  "atomic_number": 3, "group": 1, "period": 2, "type": "금속"},
    {"symbol": "Be", "name": "Beryllium","atomic_number": 4, "group": 2, "period": 2, "type": "금속"},
    {"symbol": "B",  "name": "Boron",    "atomic_number": 5, "group": 13, "period": 2, "type": "준금속"},
    {"symbol": "C",  "name": "Carbon",   "atomic_number": 6, "group": 14, "period": 2, "type": "비금속"},
    {"symbol": "N",  "name": "Nitrogen", "atomic_number": 7, "group": 15, "period": 2, "type": "비금속"},
    {"symbol": "O",  "name": "Oxygen",   "atomic_number": 8, "group": 16, "period": 2, "type": "비금속"},
    {"symbol": "F",  "name": "Fluorine", "atomic_number": 9, "group": 17, "period": 2, "type": "비금속"},
    {"symbol": "Ne", "name": "Neon",     "atomic_number": 10, "group": 18, "period": 2, "type": "비활성 기체"},
]

df = pd.DataFrame(data)

# --- UI: 주기율표 버튼 만들기 ---
cols = st.columns(10)
for i, col in enumerate(cols):
    with col:
        if i < len(df):
            element = df.iloc[i]
            if st.button(element["symbol"]):
                st.session_state["selected"] = element["symbol"]

# --- 선택된 원소 정보 표시 ---
if "selected" in st.session_state:
    symbol = st.session_state["selected"]
    element = df[df["symbol"] == symbol].iloc[0]
    st.markdown("---")
    st.subheader(f"🔍 {element['name']} ({element['symbol']})")
    st.write(f"**원자번호:** {element['atomic_number']}")
    st.write(f"**족(Group):** {element['group']}")
    st.write(f"**주기(Period):** {element['period']}")
    st.write(f"**종류(Type):** {element['type']}")

    # --- 퀴즈 ---
    st.markdown("### 🧩 퀴즈 타임!")
    question = random.choice([
        f"{element['symbol']}의 원자번호는 무엇일까요?",
        f"{element['symbol']}은(는) 어떤 종류의 원소일까요?",
        f"{element['symbol']}은(는) 몇 족에 속하나요?"
    ])
    st.write(f"**문제:** {question}")

    answer = st.text_input("당신의 답:")
    if st.button("정답 확인"):
        correct = False
        if "원자번호" in question and str(element["atomic_number"]) in answer:
            correct = True
        elif "종류" in question and element["type"] in answer:
            correct = True
        elif "몇 족" in question and str(element["group"]) in answer:
            correct = True

        if correct:
            st.success("🎉 정답입니다! 훌륭해요!")
        else:
            st.error("😅 틀렸어요. 다시 도전해보세요!")

else:
    st.info("👆 위의 주기율표에서 원소를 클릭해보세요!")

st.markdown("---")
st.caption("© 2025 화학 탐험 게임 | Streamlit + Python")

