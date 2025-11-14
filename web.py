"""
Streamlit Chemical Formula Game

How to run locally:
1. Install requirements: pip install streamlit
2. Run: streamlit run streamlit_chem_game.py

This single-file Streamlit app includes:
- Two game modes: "Formula → Name" and "Name → Formula"
- Multiple-choice questions with plausible distractors
- Score, streak, and progress tracking
- Hints and difficulty levels
- Small built-in dataset of common molecules; easily extendable

Drop this file into a Git repository and push to GitHub. Then deploy with Streamlit Cloud or other host.

Author: Generated for the user
"""

import streamlit as st
import random
import textwrap
from typing import List, Tuple

# -------------------------
# Data: common molecules
# -------------------------
# Each entry: (formula, name)
MOLECULES = [
    ("H2O", "Water"),
    ("CO2", "Carbon dioxide"),
    ("O2", "Oxygen"),
    ("N2", "Nitrogen"),
    ("CH4", "Methane"),
    ("C2H6", "Ethane"),
    ("C2H5OH", "Ethanol"),
    ("C6H6", "Benzene"),
    ("C6H12O6", "Glucose"),
    ("NaCl", "Sodium chloride"),
    ("HCl", "Hydrochloric acid"),
    ("NH3", "Ammonia"),
    ("H2SO4", "Sulfuric acid"),
    ("CaCO3", "Calcium carbonate"),
    ("KNO3", "Potassium nitrate"),
    ("NaHCO3", "Sodium bicarbonate"),
    ("H2O2", "Hydrogen peroxide"),
    ("SiO2", "Silicon dioxide"),
    ("Fe2O3", "Iron(III) oxide"),
    ("AgNO3", "Silver nitrate")
]

# -------------------------
# Utility functions
# -------------------------

def generate_distractors(correct: str, pool: List[Tuple[str, str]], mode: str, n: int = 3) -> List[str]:
    """Generate n distractors for a correct answer.
    mode: 'formula_to_name' or 'name_to_formula'
    """
    choices = set()
    attempts = 0
    while len(choices) < n and attempts < 200:
        attempts += 1
        item = random.choice(pool)
        candidate = item[1] if mode == "formula_to_name" else item[0]
        if candidate == correct:
            continue
        # Slightly prefer entries that share elements or word patterns
        choices.add(candidate)
    return list(choices)


def make_question(pool: List[Tuple[str, str]], mode: str) -> Tuple[str, List[str], str]:
    """Create a question. Returns (prompt, options, correct)
    - mode 'formula_to_name': prompt shows formula, options are names
    - mode 'name_to_formula': prompt shows name, options are formulas
    """
    formula, name = random.choice(pool)
    if mode == "formula_to_name":
        prompt = f"Which compound has the formula {formula}?"
        correct = name
        distractors = generate_distractors(correct, pool, mode)
    else:
        prompt = f"What is the molecular formula of {name}?"
        correct = formula
        distractors = generate_distractors(correct, pool, mode)

    options = distractors + [correct]
    random.shuffle(options)
    return prompt, options, correct


# -------------------------
# Game state helpers
# -------------------------

def init_state():
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "total" not in st.session_state:
        st.session_state.total = 0
    if "streak" not in st.session_state:
        st.session_state.streak = 0
    if "question_index" not in st.session_state:
        st.session_state.question_index = 0
    if "questions_to_ask" not in st.session_state:
        st.session_state.questions_to_ask = 10
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "mode" not in st.session_state:
        st.session_state.mode = "formula_to_name"
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "Easy"
    if "used_questions" not in st.session_state:
        st.session_state.used_questions = set()


def next_question():
    pool = MOLECULES.copy()
    # Difficulty could influence pool size or distractor quality
    if st.session_state.difficulty == "Easy":
        pool = [m for m in MOLECULES if m[1] in ["Water", "Carbon dioxide", "Oxygen", "Methane", "Ethanol", "Sodium chloride", "Glucose"] ]
    elif st.session_state.difficulty == "Medium":
        pool = MOLECULES
    else:  # Hard
        pool = MOLECULES + [ ("C3H8", "Propane"), ("C4H10", "Butane"), ("C3H6", "Propene") ]

    # Avoid repeating the same exact pair in a single session
    attempts = 0
    while attempts < 100:
        attempts += 1
        formula, name = random.choice(pool)
        pair_key = (formula, name)
        if pair_key not in st.session_state.used_questions:
            st.session_state.used_questions.add(pair_key)
            break
    prompt, options, correct = make_question(pool, st.session_state.mode)
    st.session_state.current_question = {
        "prompt": prompt,
        "options": options,
        "correct": correct
    }


def reset_game():
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.streak = 0
    st.session_state.question_index = 0
    st.session_state.used_questions = set()
    st.session_state.current_question = None


# -------------------------
# Streamlit UI
# -------------------------

def main():
    st.set_page_config(page_title="Chemical Formula Game", layout="centered")
    st.title("⚗️ 화학 분자식 게임")
    st.write("간단하고 재미있는 분자식 암기 게임 — 점수를 쌓고 연속 정답(streak)을 유지해 보세요!")

    # Sidebar: settings
    with st.sidebar:
        st.header("설정")
        mode = st.radio("게임 모드", ("Formula → Name", "Name → Formula"))
        st.session_state.mode = "formula_to_name" if mode.startswith("Formula") else "name_to_formula"
        st.session_state.questions_to_ask = st.slider("문제 수", min_value=5, max_value=30, value=10, step=1)
        st.session_state.difficulty = st.selectbox("난이도", ("Easy", "Medium", "Hard"))
        st.markdown("---")
        if st.button("게임 초기화"):
            reset_game()
            st.experimental_rerun()

    init_state()

    # Start / progress
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader(f"문제 {st.session_state.question_index+1} / {st.session_state.questions_to_ask}")
    with col2:
        st.metric("점수", f"{st.session_state.score}/{st.session_state.total}")
        st.metric("연속 정답", st.session_state.streak)

    # If no current question, generate one
    if st.session_state.current_question is None or st.session_state.question_index >= st.session_state.questions_to_ask:
        if st.session_state.question_index >= st.session_state.questions_to_ask:
            st.success("모든 문제 완료!")
            st.write(f"최종 점수: {st.session_state.score}/{st.session_state.total}")
            if st.button("다시 플레이"):
                reset_game()
                next_question()
                st.session_state.question_index = 0
                st.experimental_rerun()
            st.stop()
        else:
            next_question()

    q = st.session_state.current_question
    st.write(q["prompt"])

    # Show options as radio buttons
    choice = st.radio("정답을 선택하세요:", q["options"], key=f"choice_{st.session_state.question_index}")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("제출", key=f"submit_{st.session_state.question_index}"):
            st.session_state.total += 1
            if choice == q["correct"]:
                st.session_state.score += 1
                st.session_state.streak += 1
                st.success("정답입니다! 🎉")
            else:
                st.session_state.streak = 0
                st.error(f"오답입니다 — 정답은: {q['correct']}")
            st.session_state.question_index += 1
            if st.session_state.question_index < st.session_state.questions_to_ask:
                next_question()
            else:
                # end
                pass
            st.experimental_rerun()
    with col_b:
        if st.button("힌트", key=f"hint_{st.session_state.question_index}"):
            # Simple hint system: show elements in formula or word parts
            if st.session_state.mode == "formula_to_name":
                # show chemical elements present (naive parse)
                elements = extract_elements_from_formula(q["correct"] if False else q["prompt"])  # prompt contains formula in this mode
                st.info(f"힌트 — 포함된 원소: {elements}")
            else:
                # show first letters of formula
                st.info(f"힌트 — 정답의 첫 글자: {q['correct'][0]}")
    with col_c:
        if st.button("다음 문제", key=f"next_{st.session_state.question_index}"):
            st.session_state.question_index += 1
            if st.session_state.question_index < st.session_state.questions_to_ask:
                next_question()
            else:
                pass
            st.experimental_rerun()

    # Progress bar
    progress = st.session_state.question_index / st.session_state.questions_to_ask
    st.progress(progress)

    # Show small table of recent performance
    st.markdown("---")
    st.subheader("오늘의 통계")
    st.write(f"총 시도: {st.session_state.total}, 정답: {st.session_state.score}, 연속 정답: {st.session_state.streak}")

    # Footer: small how-to and extendability
    st.markdown("---")
    st.markdown(textwrap.dedent(
        """
        **앱 확장 아이디어**
        - 더 많은 분자식을 CSV로 관리하고 업로드 기능 추가
        - 학생용 레벨(중학교/고등학교/대학)별 문제집 구성
        - GitHub Actions를 이용해 테스트와 배포 자동화
        - Streamlit Cloud에 배포하여 URL을 공유
        """
    ))


# -------------------------
# Helper: naive element extraction for hints
# -------------------------

def extract_elements_from_formula(prompt: str) -> str:
    """Very naive parser: extracts uppercase letters (and following lowercase) as elements.
    If prompt contains words (like the full prompt string), try to find formula inside.
    """
    # try to find a formula-like token like containing letters and digits and possibly parentheses
    tokens = prompt.replace('?', ' ').split()
    candidate = None
    for t in tokens:
        if any(c.isdigit() for c in t) and any(c.isalpha() for c in t):
            candidate = t
            break
    if candidate is None:
        # fallback: use the prompt as-is
        candidate = prompt
    elements = []
    i = 0
    while i < len(candidate):
        c = candidate[i]
        if c.isupper():
            elem = c
            j = i + 1
            if j < len(candidate) and candidate[j].islower():
                elem += candidate[j]
                i += 1
            elements.append(elem)
        i += 1
    return ", ".join(elements) if elements else "정보 없음"


if __name__ == "__main__":
    main()
