"""
Streamlit 화학 분자식 게임 (한국어 버전) - Google Sheet 연동

특징:
- 시작 시 이름 입력
- 고유 ID 기반 사칭 방지
- 게임 종료 시 점수와 걸린 시간을 Google Sheet에 저장
- Google Sheet에서 리더보드 읽어와 Streamlit 화면에 표시
"""

import streamlit as st
import random
import time
import pandas as pd
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Tuple

# -------------------------
# Google Sheet 설정
# -------------------------
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Service account JSON 파일 경로
SERVICE_ACCOUNT_FILE = 'service_account.json'  # 실제 파일명으로 교체
SHEET_NAME = 'ChemGameLeaderboard'  # Google Sheet 이름

credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open(SHEET_NAME).sheet1

# -------------------------
# 데이터: 쉬운 문제 30개 + 고3 수준 3개
# -------------------------
MOLECULES = [
    ("H2O", "물"),("CO2", "이산화탄소"),("O2", "산소"),("N2", "질소"),("CH4", "메테인"),
    ("C2H6", "에테인"),("NaCl", "염화나트륨"),("HCl", "염화수소"),("NH3", "암모니아"),("H2SO4", "황산"),
    ("CaCO3", "탄산칼슘"),("NaHCO3", "탄산수소나트륨"),("KNO3", "질산칼륨"),("NaOH", "수산화나트륨"),("KOH", "수산화칼륨"),
    ("Ca(OH)2", "수산화칼슘"),("Mg(OH)2", "수산화마그네슘"),("BaSO4", "황산바륨"),("HNO3", "질산"),("H3PO4", "인산"),
    ("KCl", "염화칼륨"),("Na2CO3", "탄산나트륨"),("K2CO3", "탄산칼륨"),("MgSO4", "황산마그네슘"),("CaSO4", "황산칼슘"),
    ("Al2O3", "산화알루미늄"),("Fe2O3", "산화철(III)"),("CuSO4", "황산구리(II)"),("ZnO", "산화아연"),("Na2SO4", "황산나트륨"),
    ("C6H6", "벤젠"),("C6H12O6", "포도당"),("CH3COOH", "아세트산"),
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

    st.session_state.current_question = {
        "prompt": prompt,
        "options": options,
        "correct": correct
    }

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
        "used_questions": set(),
        "start_time": None,
        "game_over": False,
        "game_started": False,
        "user_id": str(uuid.uuid4()),
        "user_name": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# -------------------------
# 게임 초기화
# -------------------------

def reset_game():
    for key in ["score","total","streak","question_index","current_question","used_questions",
                "start_time","game_over","game_started","user_name"]:
        if key == "used_questions":
            st.session_state[key] = set()
        elif key == "game_started" or key == "game_over":
            st.session_state[key] = False
        elif key == "user_name":
            st.session_state[key] = ""
        else:
            st.session_state[key] = 0

# -------------------------
# Google Sheet 기록
# -------------------------

def save_score_to_sheet(name, score, total, elapsed):
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    sheet.append_row([st.session_state.user_id, name, score, total, round(elapsed,1), now])

def load_leaderboard():
    records = sheet.get_all_records()
    if not records:
        return pd.DataFrame(columns=['ID','이름','점수','총문제','시간','날짜'])
    df = pd.DataFrame(records)
    df = df.sort_values(by=['점수','시간'], ascending=[False, True]).reset_index(drop=True)
    return df

# -------------------------
# 메인 UI
# -------------------------

def main():
    st.set_page_config(page_title="화학 분자식 게임")
    st.title("⚗️ 화학 분자식 게임")
    st.write("쉬운 문제 30개와 고3 수준 문제 3개를 포함한 게임입니다.")

    with st.sidebar:
        st.header("설정")
        mode = st.radio("게임 모드", ("분자식 → 이름", "이름 → 분자식"))
        st.session_state.mode = "formula_to_name" if mode.startswith("분자식") else "name_to_formula"
        st.session_state.questions_to_ask = st.slider("문제 수", 5, min(5, 33), 20)

        if st.button("게임 초기화"):
            reset_game()
            st.rerun()

    init_state()

    # 이름 입력 후 시작
    if not st.session_state.game_started:
        name_input = st.text_input("이름을 입력하세요 (사칭 방지)", key="name_input")
        if st.button("게임 시작"):
            if not name_input.strip():
                st.warning("이름을 입력해야 게임을 시작할 수 있습니다.")
            else:
                st.session_state.user_name = name_input.strip()
                st.session_state.game_started = True
                st.session_state.start_time = time.time()
                next_question()
                st.rerun()
        return

    # 게임 진행
    if st.session_state.game_over:
        elapsed = time.time() - st.session_state.start_time
        st.write(f"🎉 게임 종료! {st.session_state.user_name}님의 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.write(f"⏱ 걸린 시간: {elapsed:.1f}초")

        # Google Sheet에 기록 저장
        save_score_to_sheet(st.session_state.user_name, st.session_state.score, st.session_state.total, elapsed)

        # 리더보드 표시
        lb_df = load_leaderboard()
        st.subheader("🏆 리더보드")
        st.dataframe(lb_df[['이름','점수','총문제','시간','날짜']])
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
