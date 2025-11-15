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
import pandas as pd  # 틀린 문제 표용

# -------------------------
# 데이터: 쉬운 문제 30개 + 고3 수준 3개
# -------------------------
MOLECULES = [
    ("H2O", "물"), ("CO2", "이산화탄소"), ("O2", "산소"), ("N2", "질소"),
    ("CH4", "메테인"), ("C2H6", "에테인"), ("NaCl", "염화나트륨"), ("HCl", "염화수소"),
    ("NH3", "암모니아"), ("H2SO4", "황산"), ("CaCO3", "탄산칼슘"), ("NaHCO3", "탄산수소나트륨"),
    ("KNO3", "질산칼륨"), ("NaOH", "수산화나트륨"), ("KOH", "수산화칼륨"), ("Ca(OH)2", "수산화칼슘"),
    ("Mg(OH)2", "수산화마그네슘"), ("BaSO4", "황산바륨"), ("HNO3", "질산"), ("H3PO4", "인산"),
    ("KCl", "염화칼륨"), ("Na2CO3", "탄산나트륨"), ("K2CO3", "탄산칼륨"), ("MgSO4", "황산마그네슘"),
    ("CaSO4", "황산칼슘"), ("Al2O3", "산화알루미늄"), ("Fe2O3", "산화철(III)"), ("CuSO4", "황산구리(II)"),
    ("ZnO", "산화아연"), ("Na2SO4", "황산나트륨"),
    ("C6H6", "벤젠"), ("C6H12O6", "포도당"), ("CH3COOH", "아세트산"),
]

# -------------------------
# 문제 생성
# -------------------------
def generate_distractors(correct: str, pool: List[Tuple[str, str]], mode: str, n: int = 3) -> List[str]:
    choices = set()
    attempts = 0
    while len(choices) < n and attempts < 100:
        attempts += 1
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
        "score": 0, "total": 0, "streak": 0, "question_index": 0,
        "questions_to_ask": 10,  # 기본 문제 수 10
        "mode": "formula_to_name",
        "current_question": None, "used_questions": set(), "wrong_answers": [],
        "start_time": None, "game_over": False, "game_started": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------------
# 다음 문제
# -------------------------
def next_question():
    pool = MOLECULES.copy()
    available_pool = [m for m in pool if m not in st.session_state.used_questions]
    if not available_pool:
        st.session_state.used_questions.clear()
        available_pool = pool.copy()
    formula, name = random.choice(available_pool)
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
    st.session_state.current_question = {"prompt": prompt, "options": options, "correct": correct}

# -------------------------
# 게임 초기화
# -------------------------
def reset_game():
    for key in ["score","total","streak","question_index","current_question","used_questions","wrong_answers","start_time","game_over","game_started"]:
        if key == "used_questions": st.session_state[key] = set()
        elif key == "wrong_answers": st.session_state[key] = []
        elif key in ["game_over","game_started"]: st.session_state[key] = False
        else: st.session_state[key] = 0 if isinstance(st.session_state.get(key), int) else None

# -------------------------
# 메인 UI
# -------------------------
def main():
    st.set_page_config(page_title="화학 분자식 게임")
    st.title("⚗️ 화학 분자식 게임")

    with st.sidebar:
        st.header("설정")
        mode = st.radio("게임 모드", ("분자식 → 이름", "이름 → 분자식"))
        st.session_state.mode = "formula_to_name" if mode.startswith("분자식") else "name_to_formula"
        # 슬라이더 기본값 10
        st.session_state.questions_to_ask = st.slider("문제 수", 5, min(5, 33), 10)
        if st.button("게임 초기화"):
            reset_game()
            st.rerun()

    init_state()

    if not st.session_state.game_started:
        if st.button("게임 시작"):
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            next_question()
            st.rerun()
        return

    if st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time
        st.write(f"🎉 게임 종료! 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.write(f"⏱ 걸린 시간: {elapsed:.1f}초")

        if st.session_state.wrong_answers:
            st.subheader("❌ 틀린 문제 정답")

            # 데이터프레임 생성
            df_wrong = pd.DataFrame([
                {
                    "문항 번호": wa["index"],
                    "문제": wa["question"],
                    "선택한 답": wa["your_answer"],
                    "정답": wa["correct_answer"]
                } for wa in st.session_state.wrong_answers
            ])

            # HTML 스타일 적용: padding + 글자 드래그 금지
            styled_html = df_wrong.to_html(index=False, escape=False)
            styled_html = styled_html.replace(
                "<table border=\"1\" class=\"dataframe\">",
                "<table style='border-collapse: collapse; width: 100%; table-layout: fixed; user-select: none;'>"
            ).replace(
                "<th>", "<th style='padding: 8px; text-align: left;'>"
            ).replace(
                "<td>", "<td style='padding: 8px;'>"
            )

            st.markdown(styled_html, unsafe_allow_html=True)

        return

    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index + 1} / {st.session_state.questions_to_ask}")
    st.write(q["prompt"])

    choice = st.radio("정답 선택:", q["options"], index=None, key=f"choice_{st.session_state.question_index}")

    if choice is not None:
        st.session_state.total += 1
        if choice == q["correct"]:
            st.session_state.score += 1
            st.session_state.streak += 1
            st.success("정답입니다!")
        else:
            st.session_state.streak = 0
            st.error(f"오답입니다. 정답: {q['correct']}")
            # 틀린 문제 기록 (문항 번호 추가)
            st.session_state.wrong_answers.append({
                "index": st.session_state.question_index + 1,
                "question": q["prompt"],
                "your_answer": choice,
                "correct_answer": q["correct"]
            })

        st.session_state.question_index += 1
        if st.session_state.question_index >= st.session_state.questions_to_ask:
            st.session_state.game_over = True
        else:
            next_question()
        st.rerun()

    progress_value = st.session_state.question_index / st.session_state.questions_to_ask
    st.progress(progress_value)

if __name__ == "__main__":
    main()
