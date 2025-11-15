"""
Streamlit 화학 분자식 게임 (한국어 버전) - 쉬운 문제 30개 + 고3 수준 3개

실행 방법:
1. pip install streamlit
2. streamlit run streamlit_chem_game.py
"""

import streamlit as st
import random
import time
from typing import List, Tuple

# -------------------------
# 데이터: 쉬운 문제 30개 + 고3 수준 3개
# -------------------------
MOLECULES = [
    ("H2O", "물"),
    ("CO2", "이산화탄소"),
    ("O2", "산소"),
    ("N2", "질소"),
    ("CH4", "메테인"),
    ("C2H6", "에테인"),
    ("NaCl", "염화나트륨"),
    ("HCl", "염화수소"),
    ("NH3", "암모니아"),
    ("H2SO4", "황산"),
    ("CaCO3", "탄산칼슘"),
    ("NaHCO3", "탄산수소나트륨"),
    ("KNO3", "질산칼륨"),
    ("NaOH", "수산화나트륨"),
    ("KOH", "수산화칼륨"),
    ("Ca(OH)2", "수산화칼슘"),
    ("Mg(OH)2", "수산화마그네슘"),
    ("BaSO4", "황산바륨"),
    ("HNO3", "질산"),
    ("H3PO4", "인산"),
    ("KCl", "염화칼륨"),
    ("Na2CO3", "탄산나트륨"),
    ("K2CO3", "탄산칼륨"),
    ("MgSO4", "황산마그네슘"),
    ("CaSO4", "황산칼슘"),
    ("Al2O3", "산화알루미늄"),
    ("Fe2O3", "산화철(III)"),
    ("CuSO4", "황산구리(II)"),
    ("ZnO", "산화아연"),
    ("Na2SO4", "황산나트륨"),
    ("C6H6", "벤젠"),
    ("C6H12O6", "포도당"),
    ("CH3COOH", "아세트산"),
]

# -------------------------
# 오답 선택지 생성
# -------------------------
def generate_distractors(correct: str, pool: List[Tuple[str, str]], mode: str, n: int = 3) -> List[str]:
    choices = set()
    while len(choices) < n:
        f, nm = random.choice(pool)
        value = nm if mode == "formula_to_name" else f
        if value != correct:
            choices.add(value)
    return list(choices)

# -------------------------
# 세션 초기화
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
        "used_questions": set(),
        "start_time": None,
        "game_over": False,
        "game_started": False,
        "incorrect_answers": [],     
        "processed_indices": set()  
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------------
# 다음 문제 생성
# -------------------------
def next_question():
    pool = MOLECULES.copy()
    available = [m for m in pool if m not in st.session_state.used_questions]

    if not available:
        st.session_state.used_questions.clear()
        available = pool.copy()

    formula, name = random.choice(available)
    st.session_state.used_questions.add((formula, name))

    if st.session_state.mode == "formula_to_name":
        prompt = f"다음 화학식의 물질 이름은 무엇인가요? {formula}"
        correct = name
    else:
        prompt = f"다음 물질의 분자식은 무엇인가요? {name}"
        correct = formula

    distractors = generate_distractors(correct, pool, st.session_state.mode)
    options = distractors + [correct]
    random.shuffle(options)

    st.session_state.current_question = {
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "formula": formula,
        "name": name
    }

# -------------------------
# 게임 전체 리셋
# -------------------------
def reset_game():
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.streak = 0
    st.session_state.question_index = 0
    st.session_state.current_question = None
    st.session_state.used_questions = set()
    st.session_state.start_time = None
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.session_state.incorrect_answers = []
    st.session_state.processed_indices = set()

# -------------------------
# 메인 UI
# -------------------------
def main():
    st.set_page_config(page_title="화학 분자식 게임")
    st.title("⚗️ 화학 분자식 게임")

    init_state()

    # ----- 사이드바 -----
    with st.sidebar:
        st.header("설정")

        mode = st.radio("게임 모드", ("분자식 → 이름", "이름 → 분자식"))
        st.session_state.mode = "formula_to_name" if mode.startswith("분자식") else "name_to_formula"

        max_q = len(MOLECULES)
        st.session_state.questions_to_ask = st.slider("문제 수", 5, max_q, 10)

        if st.button("게임 초기화"):
            reset_game()
            st.rerun()

    # ----- 게임 시작 전 -----
    if not st.session_state.game_started:
        if st.button("게임 시작"):
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            next_question()
            st.rerun()

        st.write("왼쪽에서 설정을 선택하고 **게임 시작** 버튼을 눌러주세요.")
        return

    # ----- 게임 종료 화면 -----
    if st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time

        st.subheader("🎉 게임 종료!")
        st.write(f"### 점수: {st.session_state.score} / {st.session_state.total}")
        st.write(f"### 걸린 시간: {elapsed:.1f}초")

        if st.session_state.incorrect_answers:
            st.subheader("❌ 틀린 문제 목록")
            for i, item in enumerate(st.session_state.incorrect_answers, 1):
                st.markdown(f"**{i}.** {item['prompt']}")
                st.markdown(f"- 선택한 답: `{item['chosen']}`")
                st.markdown(f"- 정답: `{item['correct']}`")
                st.markdown("---")
        else:
            st.success("🎉 모든 문제를 맞췄습니다!")

        if st.button("다시 플레이"):
            reset_game()
            st.rerun()

        return

    # ----- 문제 표시 -----
    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index + 1} / {st.session_state.questions_to_ask}")
    st.write(q["prompt"])

    choice_key = f"choice_{st.session_state.question_index}"
    choice = st.radio("정답 선택:", q["options"], key=choice_key)

    # ----- 정답 처리 -----
    if st.session_state.question_index not in st.session_state.processed_indices:
        if choice:
            st.session_state.total += 1

            if choice == q["correct"]:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.success("정답입니다!")
            else:
                st.session_state.streak = 0
                st.error(f"오답입니다. 정답: {q['correct']}")
                st.session_state.incorrect_answers.append({
                    "prompt": q["prompt"],
                    "chosen": choice,
                    "correct": q["correct"],
                })

            st.session_state.processed_indices.add(st.session_state.question_index)
            st.session_state.question_index += 1

            if st.session_state.question_index >= st.session_state.questions_to_ask:
                st.session_state.game_over = True
            else:
                next_question()

            st.rerun()

    # ----- 진행 바 -----
    st.progress(st.session_state.question_index / st.session_state.questions_to_ask)

if __name__ == "__main__":
    main()
