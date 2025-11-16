import streamlit as st
import random

# --------------------------
# 데이터: 고1 수준 원소 기호/이름
# --------------------------
PERIODIC_DATA = [
    ("H", "수소"), ("He", "헬륨"), ("Li", "리튬"), ("Be", "베릴륨"), ("B", "붕소"),
    ("C", "탄소"), ("N", "질소"), ("O", "산소"), ("F", "플루오린"), ("Ne", "네온"),
    ("Na", "나트륨"), ("Mg", "마그네슘"), ("Al", "알루미늄"), ("Si", "규소"), ("P", "인"),
    ("S", "황"), ("Cl", "염소"), ("Ar", "아르곤"), ("K", "칼륨"), ("Ca", "칼슘")
]

# --------------------------
# 기존 화학식 문제 데이터
# --------------------------
MOLECULE_DATA = [
    ("H2O", "물"), ("CO2", "이산화탄소"), ("O2", "산소"), ("N2", "질소"), ("NH3", "암모니아"),
    ("CH4", "메테인"), ("C2H5OH", "에탄올"), ("NaCl", "염화 나트륨"), ("HCl", "염산"), ("H2SO4", "황산"),
    ("CaCO3", "탄산칼슘"), ("KCl", "염화칼륨"), ("NaHCO3", "탄산수소나트륨"), ("HNO3", "질산"), ("CO", "일산화탄소"),
    ("SO2", "아황산가스"), ("C6H12O6", "포도당"), ("MgO", "산화마그네슘"), ("Fe2O3", "산화철"), ("NaOH", "수산화나트륨")
]


# --------------------------
# Streamlit 기본 설정
# --------------------------
st.set_page_config(page_title="과학 게임", layout="wide")

# 드래그 방지 CSS
st.markdown("""
<style>
* {
    user-select: none;
}
table td:first-child {
    width: 80px !important;
}
select {
    padding-left: 20px;
    padding-right: 20px;
}
</style>
""", unsafe_allow_html=True)


# --------------------------
# 초기 session_state
# --------------------------
if "started" not in st.session_state:
    st.session_state.started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "questions_to_ask" not in st.session_state:
    st.session_state.questions_to_ask = 10
if "game_type" not in st.session_state:
    st.session_state.game_type = "화학식"


# --------------------------
# 왼쪽: 설정 영역
# --------------------------
with st.sidebar:
    st.header("게임 설정")

    st.session_state.game_type = st.selectbox(
        "게임 선택",
        ["화학식 게임", "주기율표 게임"]
    )

    st.session_state.questions_to_ask = st.slider(
        "문제 수 선택",
        min_value=5,
        max_value=20,
        value=10
    )

    if st.button("게임 초기화"):
        st.session_state.started = False
        st.session_state.questions = []
        st.session_state.user_answers = {}
        st.rerun()


# --------------------------
# 메인 화면
# --------------------------
st.title("과학 학습 게임")

if not st.session_state.started:

    st.info("왼쪽 설정을 확인 후 시작해 주세요!")

    if st.button("게임 시작", type="primary"):
        if st.session_state.game_type == "화학식 게임":
            dataset = MOLECULE_DATA
        else:
            dataset = PERIODIC_DATA

        st.session_state.questions = random.sample(dataset, st.session_state.questions_to_ask)
        st.session_state.started = True
        st.session_state.user_answers = {}
        st.rerun()

else:
    st.subheader(f"총 {st.session_state.questions_to_ask}문제")

    for idx, (question, answer) in enumerate(st.session_state.questions, start=1):
        user_key = f"q_{idx}"

        if st.session_state.game_type == "화학식 게임":
            q_text = f"{idx}. {question} 의 이름은?"
        else:
            q_text = f"{idx}. {question} 의 이름은?"

        st.write(q_text)

        st.session_state.user_answers[user_key] = st.text_input(
            "",
            key=user_key,
            label_visibility="collapsed"
        )

    if st.button("채점하기", type="primary"):
        correct = 0
        results = []

        for idx, (question, answer) in enumerate(st.session_state.questions, start=1):
            key = f"q_{idx}"
            user_ans = st.session_state.user_answers.get(key, "").strip()

            is_correct = (user_ans == answer)
            results.append((idx, question, user_ans, answer, is_correct))

            if is_correct:
                correct += 1

        st.success(f"정답 개수: {correct} / {len(st.session_state.questions)}")

        st.subheader("틀린 문제 정답 보기")

        wrong = [r for r in results if not r[4]]

        if len(wrong) == 0:
            st.write("모든 문제를 맞았습니다!")
        else:
            table_md = "|문항|문제|입력한 답|정답|\n|---|---|---|---|\n"
            for (num, q, ua, ans, _) in wrong:
                table_md += f"|{num}|{q}|{ua}|{ans}|\n"

            st.markdown(table_md)

        st.info("왼쪽 설정창에서 '게임 초기화'를 눌러 다시 시작하세요!")
