import streamlit as st
import random
import time
import pandas as pd
import sqlite3
from typing import List, Tuple

DB_PATH = "ranking.db"

# ------------------------- 데이터 -------------------------
MOLECULES = [
    ("H2O", "물"), ("CO2", "이산화탄소"), ("O2", "산소"), ("N2", "질소"),
    ("CH4", "메테인"), ("C2H6", "에테인"), ("NaCl", "염화나트륨"), ("HCl", "염화수소"),
    ("NH3", "암모니아"), ("H2SO4", "황산"), ("CaCO3", "탄산칼슘"), ("NaHCO3", "탄산수소나트륨"),
    ("KNO3", "질산칼륨"), ("NaOH", "수산화나트륨"), ("KOH", "수산화칼륨"), ("Ca(OH)2", "수산화칼슘"),
    ("Mg(OH)2", "수산화마그네슘"), ("BaSO4", "황산바륨"), ("HNO3", "질산"), ("H3PO4", "인산"),
    ("KCl", "염화칼륨"), ("Na2CO3", "탄산나트륨"), ("K2CO3", "탄산칼륨"), ("MgSO4", "황산마그네슘"),
    ("CaSO4", "황산칼슘"), ("Al2O3", "산화알루미늄"), ("Fe2O3", "산화철(III)"), ("CuSO4", "황산구리(II)"),
    ("ZnO", "산화아연"), ("Na2SO4", "황산나트륨"), ("C6H6", "벤젠"), ("C6H12O6", "포도당"), ("CH3COOH", "아세트산"),
]

PERIODIC = [
    ("H", "수소"), ("He", "헬륨"), ("Li", "리튬"), ("Be", "베릴륨"), ("B", "붕소"),
    ("C", "탄소"), ("N", "질소"), ("O", "산소"), ("F", "플루오린"), ("Ne", "네온"),
    ("Na", "나트륨"), ("Mg", "마그네슘"), ("Al", "알루미늄"), ("Si", "규소"), ("P", "인"),
    ("S", "황"), ("Cl", "염소"), ("Ar", "아르곤"), ("K", "칼륨"), ("Ca", "칼슘")
]

# ------------------------- DB 관련 -------------------------
def save_score(game_type, player_name, score, elapsed_time):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT,
            player_name TEXT,
            score INTEGER,
            elapsed_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        INSERT INTO ranking (game_type, player_name, score, elapsed_time)
        VALUES (?, ?, ?, ?)
    """, (game_type, player_name, score, elapsed_time))
    conn.commit()
    conn.close()

def get_ranking(game_type, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT,
            player_name TEXT,
            score INTEGER,
            elapsed_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.execute("""
        SELECT player_name, score, elapsed_time
        FROM ranking
        WHERE game_type=?
        ORDER BY score DESC, elapsed_time ASC
        LIMIT ?
    """, (game_type, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

# ------------------------- 보기 생성 -------------------------
def generate_distractors(correct: str, pool: List[Tuple[str,str]], mode: str, n: int=3) -> List[str]:
    choices = set()
    attempts = 0
    while len(choices) < n and attempts < 100:
        attempts += 1
        f, nm = random.choice(pool)
        candidate = nm if mode.endswith("_to_name") else f
        if candidate != correct:
            choices.add(candidate)
    return list(choices)

# ------------------------- 상태 초기화 -------------------------
def init_state():
    defaults = {
        "score":0, "total":0, "streak":0, "question_index":0,
        "questions_to_ask":10, "game_type":"화학식 게임", "mode":"molecule_to_name",
        "current_question":None, "used_questions":set(), "wrong_answers":[],
        "start_time":None, "elapsed_time":None, "game_over":False, "game_started":False,
        "player_name_entered":False
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def reset_game():
    for key in ["score","total","streak","question_index","current_question","used_questions","wrong_answers","start_time","elapsed_time","game_over","game_started","player_name_entered"]:
        if key=="used_questions": st.session_state[key]=set()
        elif key=="wrong_answers": st.session_state[key]=[]
        elif key in ["game_over","game_started","player_name_entered"]: st.session_state[key]=False
        else: st.session_state[key]=0 if isinstance(st.session_state.get(key),int) else None

# ------------------------- 다음 문제 -------------------------
def next_question():
    if st.session_state.mode=="molecule_all":
        current_mode = random.choice(["molecule_to_name","name_to_molecule"])
        pool = MOLECULES
    elif st.session_state.mode=="periodic_all":
        current_mode = random.choice(["periodic_to_name","name_to_periodic"])
        pool = PERIODIC
    else:
        current_mode = st.session_state.mode
        pool = MOLECULES if "molecule" in current_mode else PERIODIC

    available_pool = [m for m in pool if m not in st.session_state.used_questions]
    if not available_pool:
        st.session_state.used_questions.clear()
        available_pool = pool.copy()

    f, nm = random.choice(available_pool)
    st.session_state.used_questions.add((f,nm))

    if current_mode.endswith("_to_name"):
        prompt = f"다음의 이름은 무엇인가요? {f}" if "periodic" in current_mode else f"다음 화학식의 이름은 무엇인가요? {f}"
        correct = nm
    else:
        prompt = f"다음 기호는 무엇인가요? {nm}" if "periodic" in current_mode else f"다음 물질의 화학식은 무엇인가요? {nm}"
        correct = f

    distractors = generate_distractors(correct,pool,current_mode)
    options = distractors+[correct]
    random.shuffle(options)
    st.session_state.current_question={"prompt":prompt,"options":options,"correct":correct}

# ------------------------- 메인 -------------------------
def main():
    st.set_page_config(page_title="과학 학습 게임")
    st.title("🧪 과학 학습 게임 (화학식 + 주기율표)")

    init_state()
    disabled_state = st.session_state.game_started

    # ---------------- Sidebar ----------------
    with st.sidebar:
        st.header("순위표")
        st.subheader("화학식 게임")
        df_m = pd.DataFrame(get_ranking("화학식 게임"), columns=["이름","점수","시간(초)"])
        st.table(df_m)
        st.subheader("주기율표 게임")
        df_p = pd.DataFrame(get_ranking("주기율표 게임"), columns=["이름","점수","시간(초)"])
        st.table(df_p)

        st.header("게임 설정")
        game_type = st.radio(
            "게임 종류 선택",
            ["화학식 게임","주기율표 게임"],
            index=0 if st.session_state.game_type=="화학식 게임" else 1,
            disabled=disabled_state
        )
        st.session_state.game_type = game_type

        if game_type=="화학식 게임":
            selected_mode = st.radio("모드 선택", ["전체","분자식 → 이름","이름 → 분자식"],
                                     index=["전체","분자식 → 이름","이름 → 분자식"].index(
                                         {"molecule_all":"전체",
                                          "molecule_to_name":"분자식 → 이름",
                                          "name_to_molecule":"이름 → 분자식"}.get(st.session_state.mode,"전체")
                                     ),
                                     disabled=disabled_state)
        else:
            selected_mode = st.radio("모드 선택", ["전체","원소기호 → 이름","이름 → 원소기호"],
                                     index=["전체","원소기호 → 이름","이름 → 원소기호"].index(
                                         {"periodic_all":"전체",
                                          "periodic_to_name":"원소기호 → 이름",
                                          "name_to_periodic":"이름 → 원소기호"}.get(st.session_state.mode,"전체")
                                     ),
                                     disabled=disabled_state)
        st.session_state.questions_to_ask = st.slider("문제 수",5,20,10, disabled=disabled_state)

    # ----------------- 게임 시작 -----------------
    if not st.session_state.game_started:
        st.info("설정을 확인 후 '게임 시작' 버튼을 눌러주세요.")
        if st.button("게임 시작"):
            st.session_state.game_started=True
            st.session_state.start_time=time.time()
            if game_type=="화학식 게임":
                if selected_mode=="전체": st.session_state.mode="molecule_all"
                elif selected_mode=="분자식 → 이름": st.session_state.mode="molecule_to_name"
                else: st.session_state.mode="name_to_molecule"
            else:
                if selected_mode=="전체": st.session_state.mode="periodic_all"
                elif selected_mode=="원소기호 → 이름": st.session_state.mode="periodic_to_name"
                else: st.session_state.mode="name_to_periodic"
            next_question()
            st.rerun()
        return

    # ----------------- 게임 종료 -----------------
    if st.session_state.game_over:
        if st.session_state.elapsed_time is None:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time

        st.write(f"📝 게임 종류: {st.session_state.game_type}")
        st.write(f"🎉 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.write(f"⏱ 걸린 시간: {st.session_state.elapsed_time:.1f}초")

        # 틀린 문제
        if st.session_state.wrong_answers:
            st.subheader("❌ 틀린 문제 정답")
            df_wrong=pd.DataFrame([{"문항 번호":wa["index"],"문제":wa["question"],"선택한 답":wa["your_answer"],"정답":wa["correct_answer"]} for wa in st.session_state.wrong_answers])
            st.table(df_wrong)

        # 만점이면 이름 입력 가능
        if st.session_state.score == st.session_state.questions_to_ask and not st.session_state.player_name_entered:
            player_name = st.text_input("🎖 만점 달성! 이름 입력:")
            if player_name:
                save_score(st.session_state.game_type, player_name, st.session_state.score, st.session_state.elapsed_time)
                st.session_state.player_name_entered=True
                st.success("점수가 저장되었습니다.")

        if st.button("게임 재시작"):
            reset_game()
            st.rerun()
        return

    # ----------------- 게임 진행 -----------------
    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index+1} / {st.session_state.questions_to_ask}")
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

    st.progress(st.session_state.question_index / st.session_state.questions_to_ask)

if __name__=="__main__":
    main()
