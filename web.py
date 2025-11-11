import streamlit as st
import pandas as pd
import random
import time

st.set_page_config(page_title="주기율표 퀴즈 게임", page_icon="🧪", layout="centered")

st.title("🧪 주기율표 탐험 퀘스트")

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

# --- 세션 상태 초기화 함수 ---
def reset_game():
    for key in [
        "started", "index", "score", "feedback", "question_type",
        "finished", "game_start_time", "start_time", "total_time"
    ]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- 게임 시작 전 화면 ---
if "started" not in st.session_state:
    st.markdown("### 🧠 화학 원소를 맞추는 퀴즈 게임입니다!")
    st.write("각 문제에 정답을 입력하고 **엔터를 눌러 제출**하세요.")
    st.write("모든 문제를 풀면 총 걸린 시간이 표시됩니다!")
    if st.button("🚀 게임 시작하기"):
        st.session_state.started = True
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.feedback = ""
        st.session_state.question_type = None
        st.session_state.finished = False
        st.session_state.game_start_time = time.time()  # 총 시간 시작
        st.session_state.start_time = time.time()
        st.session_state.total_time = 0
        st.rerun()

# --- 게임 진행 화면 ---
elif not st.session_state.get("finished", False):
    element = df.iloc[st.session_state.index]

    if st.session_state.question_type is None:
        st.session_state.question_type = random.choice(["symbol", "group", "type"])
        st.session_state.start_time = time.time()
        st.session_state.feedback = ""

    # 문제 만들기
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

    # 정답 확인 함수
    def check_answer():
        user = st.session_state.user_answer.strip()
        end_time = time.time()
        elapsed = end_time - st.session_state.start_time

        if user.lower() == correct_answer.lower():
            st.session_state.score += 1
            st.session_state.feedback = f"🎉 정답입니다! ({elapsed:.2f}초)"
            st.session_state.index += 1
            st.session_state.question_type = None
            st.session_state.user_answer = ""
            time.sleep(0.6)
            # 게임 종료 시점 확인
            if st.session_state.index >= len(df):
                st.session_state.finished = True
                st.session_state.total_time = time.time() - st.session_state.game_start_time
            st.rerun()
        else:
            st.session_state.feedback = f"❌ 오답입니다! ({elapsed:.2f}초) 다시 시도해보세요."

    # 입력창
    st.text_input(
        "정답을 입력하고 엔터를 누르세요:",
        key="user_answer",
        on_change=check_answer,
        placeholder="엔터키로 제출하세요",
    )

    if st.session_state.feedback:
        st.markdown(st.session_state.feedback)

    st.markdown(f"**현재 점수:** {st.session_state.score} / {len(df)}")

# --- 게임 종료 화면 ---
else:
    total_time = st.session_state.total_time
    st.success(f"🎉 모든 문제를 완료했습니다!")
    st.markdown(f"**최종 점수:** {st.session_state.score} / {len(df)}")
    st.markdown(f"⏱️ **총 걸린 시간:** {total_time:.2f}초")
    if st.button("🔁 다시 시작하기"):
        reset_game()

st.markdown("---")
st.caption("© 2025 화학 탐험 게임 | Streamlit + Python")
