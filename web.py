"""
Streamlit 화학 분자식 게임 (한국어 버전)

실행 방법:
1. pip install streamlit
2. streamlit run streamlit_chem_game.py
"""

import streamlit as st
import random
from typing import List, Tuple

# -------------------------
# 데이터: 기본 분자식 목록
# -------------------------
MOLECULES = [
    ("H2O", "물"),
    ("CO2", "이산화탄소"),
    ("O2", "산소"),
    ("N2", "질소"),
    ("CH4", "메테인"),
    ("C2H6", "에테인"),
    ("C2H5OH", "에탄올"),
    ("C6H6", "벤젠"),
    ("C6H12O6", "포도당"),
    ("NaCl", "염화나트륨"),
    ("HCl", "염화수소"),
    ("NH3", "암모니아"),
    ("H2SO4", "황산"),
    ("CaCO3", "탄산칼슘"),
    ("KNO3", "질산칼륨"),
    ("NaHCO3", "탄산수소나트륨"),
    ("H2O2", "과산화수소"),
    ("SiO2", "이산화규소"),
    ("Fe2O3", "산화철(III)"),
    ("AgNO3", "질산은"),
]

# -------------------------
# 문제 생성
# -------------------------

def generate_distractors(correct: str, pool: List[Tuple[str, str]], mode: str, n: int = 3) -> List[str]:
    choices = set()
    while len(choices) < n:
        f, nm = random.choice(pool)
        candidate = nm if mode == "formula_to_name" else f
        if candidate != correct:
            choices.add(candidate)
    return list(choices)


def make_question(pool: List[Tuple[str, str]], mode: str):
    formula, name = random.choice(pool)

    if mode == "formula_to_name":
        prompt = f"다음 화학식의 물질 이름은 무엇인가요? {formula}"
        correct = name
    else:
        prompt = f"다음 물질의 분자식은 무엇인가요? {name}"
        correct = formula

    distractors = generate_distractors(correct, pool, mode)
    options = distractors + [correct]
    random.shuffle(options)
    return prompt, options, correct

# -------------------------
# 상태 초기화
# -------------------------

def init_state():
    defaults = {
        "score": 0,
        "total": 0,
        "streak": 0,
        "question_index": 0,
        "questions_to_ask": 10,
        "mode": "formula_to_name",
        "current_question": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------------
# 다음 문제
# -------------------------

def next_question():
    pool = MOLECULES.copy()
    prompt, options, correct = make_question(pool, st.session_state.mode)
    st.session_state.current_question = {
        "prompt": prompt,
        "options": options,
        "correct": correct
    }

# -------------------------
# 게임 초기화
# -------------------------

def reset_game():
    for key in ["score","total","streak","question_index","current_question"]:
        st.session_state[key] = 0 if isinstance(st.session_state.get(key), int) else None

# -------------------------
# 메인 UI
# -------------------------

def main():
    st.set_page_config(page_title="화학 분자식 게임")
    st.title("⚗️ 화학 분자식 게임")
    st.write("분자식과 이름을 맞히는 연습 게임입니다.")

    with st.sidebar:
        st.header("설정")
        mode = st.radio("게임 모드", ("분자식 → 이름", "이름 → 분자식"))
        st.session_state.mode = "formula_to_name" if mode.startswith("분자식") else "name_to_formula"
        st.session_state.questions_to_ask = st.slider("문제 수", 5, 30, 10)
        if st.button("게임 초기화"):
            reset_game()
            st.rerun()

    init_state()

    # 문제 카운트 & 점수 표시
    st.subheader(f"문제 {st.session_state.question_index + 1} / {st.session_state.questions_to_ask}")
    st.metric("점수", f"{st.session_state.score}/{st.session_state.total}")
    st.metric("연속 정답", st.session_state.streak)

    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    st.write(q["prompt"])

    choice = st.radio("정답 선택:", q["options"], key=f"choice_{st.session_state.question_index}")

    if st.button("제출하기"):
        st.session_state.total += 1
        if choice == q["correct"]:
            st.session_state.score += 1
            st.session_state.streak += 1
            st.success("정답입니다!")
        else:
            st.session_state.streak = 0
            st.error(f"오답입니다. 정답: {q['correct']}")

        st.session_state.question_index += 1
        if st.session_state.question_index < st.session_state.questions_to_ask:
            next_question()
        else:
            st.write(f"게임 종료! 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.rerun()

    # progress 값이 0~1 범위 내에서만 계산되도록 방어
    progress_value = min(max(st.session_state.question_index / max(st.session_state.questions_to_ask,1),0.0),1.0)
    st.progress(progress_value)

if __name__ == "__main__":
    main()
