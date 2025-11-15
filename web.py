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
    # 쉬운 문제 30개
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
    # 고3 수준 3개
    ("C6H6", "벤젠"),
    ("C6H12O6", "포도당"),
    ("CH3COOH", "아세트산"),
]

# -------------------------
# 문제 생성 - 오답 후보들 생성 함수
# -------------------------
def generate_distractors(correct: str, pool: List[Tuple[str, str]], mode: str, n: int = 3) -> List[str]:
    choices = set()
    attempts = 0
    while len(choices) < n and attempts < 500:  # 충분한 시도 허용
        attempts += 1
        f, nm = random.choice(pool)
        candidate = nm if mode == "formula_to_name" else f
        if candidate != correct:
            choices.add(candidate)
    # fallback: 같은 pool에서 랜덤으로라도 채움
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
    return {"prompt": prompt, "options": options, "correct": correct, "formula": formula, "name": name}

# -------------------------
# 세션 상태 초기화
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
        "incorrect_answers": [],     # 틀린 문제 기록
        "processed_indices": set(),  # 이미 처리한 문제 인덱스(중복 처리를 막음)
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------------
# 다음 문제 준비
# -------------------------
def next_question():
    pool = MOLECULES.copy()
    # used_questions는 (formula, name) 튜플의 set
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

    st.session_state.current_question = {
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "formula": formula,
        "name": name
    }

# -------------------------
# 게임 리셋
# -------------------------
def reset_game():
    # 안전하게 필요한 키들만 초기화
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

    # 상태 초기화는 사이드바보다 먼저 해두면 안전
    init_state()

    with st.sidebar:
        st.header("설정")
        mode = st.radio("게임 모드", ("분자식 → 이름", "이름 → 분자식"))
        st.session_state.mode = "formula_to_name" if mode.startswith("분자식") else "name_to_formula"

        # 문제 수 슬라이더: 최소 5, 최대는 전체 분자 수
        max_q = len(MOLECULES)
        st.session_state.questions_to_ask = st.slider("문제 수", 5, max_q, value=10, step=1)

        if st.button("게임 초기화"):
            reset_game()
            st.experimental_rerun()

    # 시작 전
    if not st.session_state.game_started:
        if st.button("게임 시작"):
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            # 초기 문제 준비
            next_question()
            st.experimental_rerun()
        # 안내 메시지
        st.write("설정을 확인한 뒤 '게임 시작'을 눌러주세요.")
        return

    # 게임 종료 화면
    if st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time if st.session_state.start_time else 0.0
        st.subheader("🎉 게임 종료")
        st.write(f"최종 점수: **{st.session_state.score} / {st.session_state.total}**")
        st.write(f"걸린 시간: **{elapsed:.1f}초**")
        st.write(f"최장 연속 정답: **{st.session_state.streak}**")

        if st.session_state.incorrect_answers:
            st.subheader("❌ 틀린 문제 목록")
            for idx, item in enumerate(st.session_state.incorrect_answers, 1):
                st.markdown(f"**{idx}.** {item['prompt']}")
                st.markdown(f"- 선택한 답: `{item['chosen']}`")
                st.markdown(f"- 정답: `{item['correct']}`")
                # (선택적으로) 화학식과 이름도 같이 보여줌
                if "formula" in item and "name" in item:
                    st.markdown(f"- 분자식: `{item['formula']}` / 이름: `{item['name']}`")
                st.write("---")
        else:
            st.success("✨ 모든 문제를 맞췄습니다!")

        # 다시 시작 버튼
        if st.button("다시 플레이"):
            reset_game()
            st.experimental_rerun()
        return

    # 현재 문제 표시
    q = st.session_state.current_question
    # 안전장치: current_question이 None이면 다음 문제 준비
    if q is None:
        next_question()
        st.experimental_rerun()
        return

    st.subheader(f"문제 {st.session_state.question_index + 1} / {st.session_state.questions_to_ask}")
    st.write(q["prompt"])

    # 라디오의 key는 문제 인덱스를 포함해서 고유하게
    choice_key = f"choice_{st.session_state.question_index}"
    choice = st.radio("정답 선택:", q["options"], index=0, key=choice_key)

    # 중복 처리 방지: processed_indices에 현재 인덱스가 없다면 처리
    if choice is not None and st.session_state.question_index not in st.session_state.processed_indices:
        # 정답 처리
        st.session_state.total += 1
        if choice == q["correct"]:
            st.session_state.score += 1
            st.session_state.streak += 1
            st.success("정답입니다!")
        else:
            # 틀린 경우 오답 기록에 저장
            st.session_state.streak = 0
            st.error(f"오답입니다. 정답: {q['correct']}")
            st.session_state.incorrect_answers.append({
                "prompt": q["prompt"],
                "chosen": choice,
                "correct": q["correct"],
                "formula": q.get("formula", ""),
                "name": q.get("name", "")
            })

        # 현재 문제를 처리 완료로 표시(중복 처리 방지)
        st.session_state.processed_indices.add(st.session_state.question_index)

        # 다음 문제 준비: 인덱스 증가 전에 게임 종료 여부 판단
        st.session_state.question_index += 1

        if st.session_state.question_index >= st.session_state.questions_to_ask:
            st.session_state.game_over = True
        else:
            next_question()

        # 상태가 바뀌었으므로 rerun
        st.experimental_rerun()

    # 진행도 표시
    progress_value = st.session_state.question_index / st.session_state.questions_to_ask
    st.progress(progress_value)

if __name__ == "__main__":
    main()
