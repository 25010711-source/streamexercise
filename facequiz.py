import streamlit as st
import random
import time
import pandas as pd
import sqlite3
import os
import io
import shutil
from PIL import Image

# ------------------------- DB 경로 (영구 저장) -------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "ranking.db")

# ------------------------- 자동 백업 -------------------------
def auto_backup_db():
    if not os.path.exists(DB_PATH):
        return
    backup_dir = os.path.join(os.path.dirname(__file__), "db_backup")
    os.makedirs(backup_dir, exist_ok=True)
    today = time.strftime('%Y-%m-%d')
    backup_filename = os.path.join(backup_dir, f"{today}.db")
    if not os.path.exists(backup_filename):
        shutil.copy(DB_PATH, backup_filename)

# ------------------------- 연예인 문제 데이터 -------------------------
CELEBRITY_IMAGES = [
    ("images/byunjae.jpg", "유병재"),
    ("images/kim.jpeg", "김우빈"),
    ("images/kimchaewon.jpg", "김채원"),
    ("images/leejungjae.jpg", "이정재"),
    ("images/shin.jpg", "신동엽"),
    ("images/son.jpg", "손흥민"),
    ("images/madonseok.jpg", "마동석"),
    ("images/jojungseok.jpg", "조정석"),
    ("images/yoojaeseok.jpg", "유재석"),
    ("images/jangdoyun.png", "장도연"),
    ("images/kanghodong.png", "강호동"),
    ("images/parkboyoung.png", "박보영"),
    ("images/kimnuna.jpg", "김연아"),
    ("images/parkjisung.png", "박지성"),
    ("images/sonyaejin.jpg", "손예진")
]

# ------------------------- DB 초기화 -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT,
            student_id TEXT,
            player_name TEXT,
            score INTEGER,
            elapsed_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_score(game_type, student_id, player_name, score, elapsed_time):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ranking (game_type, student_id, player_name, score, elapsed_time)
        VALUES (?, ?, ?, ?, ?)
    """, (game_type, student_id, player_name, score, elapsed_time))
    conn.commit()
    conn.close()

def get_ranking(game_type, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT student_id, player_name, score, elapsed_time
        FROM ranking
        WHERE game_type=?
        ORDER BY score DESC, elapsed_time ASC
        LIMIT ?
    """, (game_type, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

def download_csv_by_game(game_type, filename):
    conn = sqlite3.connect(DB_PATH)
    df_csv = pd.read_sql(f"SELECT * FROM ranking WHERE game_type='{game_type}' ORDER BY elapsed_time ASC", conn)
    df_csv['timestamp'] = pd.to_datetime(df_csv['timestamp']).dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
    conn.close()
    csv_buffer = io.BytesIO()
    df_csv.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    st.download_button(label=f"⬇ {game_type} CSV", data=csv_buffer, file_name=filename, mime="text/csv")

# ------------------------- 세션 초기화 -------------------------
def init_state():
    defaults = {
        "score":0, "total":0, "streak":0, "question_index":0,
        "questions_to_ask":10, "game_type":"눈코입 퀴즈", 
        "current_question":None, "used_questions":set(), "wrong_answers":[],
        "start_time":None, "elapsed_time":None, "game_over":False, "game_started":False,
        "score_saved":False,
        "user_guess":""   # ★ 엔터 제출용
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def reset_game():
    for key in ["score","total","streak","question_index","current_question","used_questions","wrong_answers","start_time","elapsed_time","game_over","game_started","score_saved","user_guess"]:
        if key=="used_questions": st.session_state[key]=set()
        elif key=="wrong_answers": st.session_state[key]=[]
        elif key in ["game_over","game_started","score_saved"]: st.session_state[key]=False
        elif key=="user_guess": st.session_state[key]=""
        else: st.session_state[key]=0 if isinstance(st.session_state.get(key),int) else None

# ------------------------- 다음 문제 -------------------------
def next_question():
    available_pool = [q for q in CELEBRITY_IMAGES if q not in st.session_state.used_questions]
    if not available_pool:
        st.session_state.used_questions.clear()
        available_pool = CELEBRITY_IMAGES.copy()

    image_file, answer = random.choice(available_pool)
    st.session_state.used_questions.add((image_file, answer))
    st.session_state.current_question = {"image_file": image_file, "correct": answer}

# ------------------------- 엔터키 제출 처리 -------------------------
def process_answer():
    guess = st.session_state.user_guess.strip()
    if not guess:
        return

    q = st.session_state.current_question
    st.session_state.total += 1

    if guess == q["correct"]:
        st.session_state.score += 1
    else:
        st.session_state.wrong_answers.append({
            "index": st.session_state.question_index + 1,
            "your_answer": guess,
            "correct_answer": q["correct"]
        })

    st.session_state.question_index += 1
    st.session_state.user_guess = ""  # 입력창 초기화

    if st.session_state.question_index >= st.session_state.questions_to_ask:
        st.session_state.game_over = True
    else:
        next_question()

    st.rerun()

# ------------------------- 메인 -------------------------
def main():
    st.set_page_config(page_title="눈코입 퀴즈", layout="wide")
    st.title("👀 눈·코·입만 보고 연예인 맞추기!")

    init_db()
    auto_backup_db()
    init_state()

    # ----------------- 왼쪽 순위표 -----------------
    with st.sidebar:
        st.header("🏆 순위표")
        ranking = get_ranking("눈코입 퀴즈")
        df = pd.DataFrame(ranking, columns=["학번","이름","점수","시간(초)"])
        df.index = df.index + 1
        df.index.name = "순위"
        st.dataframe(df, use_container_width=True)

        download_csv_by_game("눈코입 퀴즈", "celebrity_ranking.csv")

        if st.button("🔄 게임 재시작"):
            reset_game()
            st.rerun()

    # ----------------- 게임 시작 전 -----------------
    if not st.session_state.game_started:
        st.info("게임 시작 버튼을 눌러주세요.")
        if st.button("게임 시작"):
            st.session_state.game_started=True
            st.session_state.start_time=time.time()
            next_question()
            st.rerun()
        return

    # ----------------- 게임 종료 -----------------
    if st.session_state.game_over:
        if st.session_state.elapsed_time is None:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time

        st.write(f"🎉 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.write(f"⏱ 걸린 시간: {st.session_state.elapsed_time:.1f}초")

        # ⬇️ 여기서만 정답/오답 출력됨
        if st.session_state.wrong_answers:
            st.subheader("❌ 틀린 문제")
            df_wrong = pd.DataFrame([
                {
                    "문항 번호": wa["index"],
                    "선택한 답": wa["your_answer"],
                    "정답": wa["correct_answer"]
                } for wa in st.session_state.wrong_answers
            ])
            st.table(df_wrong)

        # 점수 저장
        if not st.session_state.score_saved:
            student_id = st.text_input("학번 입력:", key="student_id", value="")
            player_name = st.text_input("이름 입력:", key="player_name", value="")
            if st.button("점수 저장"):
                if student_id.strip() and player_name.strip():
                    save_score(
                        st.session_state.game_type,
                        student_id.strip(),
                        player_name.strip(),
                        st.session_state.score,
                        st.session_state.elapsed_time or 0
                    )
                    st.session_state.score_saved = True
                    st.success("점수가 저장되었습니다.")
                else:
                    st.warning("학번과 이름을 모두 입력해야 점수를 저장할 수 있습니다.")
        else:
            st.success("점수가 이미 저장되었습니다.")

        if st.button("🔄 게임 재시작"):
            reset_game()
            st.rerun()
        return

    # ----------------- 문제 표시 -----------------
    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index+1} / {st.session_state.questions_to_ask}")

    img = Image.open(q["image_file"])
    st.image(img, width=300)  # ★ 사진 크기 줄임

    # ----------------- 엔터키로 자동 제출 -----------------
    st.text_input(
        "연예인 이름을 입력하고 엔터키를 누르세요:",
        key="user_guess",
        on_change=process_answer
    )

if __name__=="__main__":
    main()
