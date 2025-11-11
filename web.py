import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="주기율표 퀴즈 게임", page_icon="🧪", layout="centered")

st.title("🧪 주기율표 탐험 퀘스트")
st.markdown("정답을 맞추면 다음 원소로 자동 진행됩니다!")

# --- 데이터 ---
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

# --- 세션 초기화 ---
if "index" not in st.session_state:
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.feedback = ""
    st.session_state.question_type = None
    st.session_state.finished = False

# --- 현재 원소 ---
if st.session_state.index >= len(df):
    st.session_state.finished = True

if not st.session_state.finished:
    element = df.iloc[st.session_state.index]

    # 새 문제 출제 (한 원소에 한 문제)
    if st.session_state.question_type is None:
        st.session_state.question_type = random.choice(["symbol", "group", "type"])
        st.session_state.start_time = time.time()
        st.session_state.feedback = ""

    # 문제 표시
    if st.session_state.question_type == "symbol":
        question = f"{element['name']}의 기호(symbol)는 무엇일까요?"
        correct_answer = element["symbol"]
    elif st.session_state.question_type == "group":
        question = f"{element['symbol']}은(는) 몇 족에 속할까요?"
        correct_answer = str(element["group"])
    else:
        question = f"{element['symbol']}은(는) 어떤 종류의 원소일까요?"
        correct_answer = element["type"]

    st.markdown(f"### 🧩 문제 {st.session_state.index + 1} / {len(df)}")
    st.markdown(f"**{question}**")

    # --- 정답 체크 함수 ---
    def check_answer():
        user = st.session_state.user_answer.strip()
        end_time = time.time()
        elapsed = end_time - st.session_state.start_time

        if user.lower() == correct_answer.lower():
            st.session_state.score += 1
            st.session_state.feedback = f"🎉 정답입니다! ({elapsed:.2f}초) → 다음 문제로 이동합니다."
            st.session_state.index += 1
            st.session_state.question_type = None
        else:
            st.session_state.feedback = f"❌ 오답입니다! ({elapsed:.2f}초) 다시 시도해보세요."

    # --- 입력 (엔터로 제출) ---
    st.text_input("정답을 입력하고 엔터를 누르세요:", key="user_answer", on_change=check_answer)

    if st.session_state.feedback:
        st.markdown(st.session_state.feedback)

    st.markdown(f"**현재 점수:** {st.session_state.score} / {len(df)}")

else:
    st.success(f"🎉 모든 문제를 완료했습니다! 최종 점수: {st.session_state.score}/{len(df)}")
    if st.button("🔁 다시 시작하기"):
        for key in ["index", "score", "feedback", "question_type", "finished"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

st.markdown("---")
st.caption("© 2025 화학 탐험 게임 | Streamlit + Python")
