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
    df_csv = pd.read_sql(
        f"SELECT * FROM ranking WHERE game_type='{game_type}' ORDER BY elapsed_time ASC",
        conn
    )
    df_csv['timestamp'] = pd.to_datetime(df_csv['timestamp']).dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')
    conn.close()
    csv_buffer = io.BytesIO()
    df_csv.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    st.download_button(
        label=f"⬇ {game_type} CSV",
        data=csv_buffer,
        file_name=filename,
        mime="text/csv"
    )

# ------------------------- 세션 초기화 -------------------------
def init_state():
    if "initialized" not in st.session_state:
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.streak = 0
        st.session_state.question_index = 0
        st.session_state.questions_to_ask = 10   # ✅ 항상 10문제
        st.session_state.game_type = "눈코입 퀴즈"
        st.session_state.current_question = None
        st.session_state.used_questions = set()
        st.session_state.wrong_answers = []
        st.session_state.start_time = None
        st.session_state.elapsed_time = None
        st.session_state.game_over = False
        st.session_state.game_started = False
        st.session_state.score_saved = False
        st.session_state.user_guess = ""
        st.session_state.initialized = True

def reset_game():
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.streak = 0
    st.session_state.question_index = 0
    st.session_state.current_question = None
    st.session_state.used_questions = set()
    st.session_state.wrong_answers = []
    st.session_state.start_time = None
    st.session_state.elapsed_time = None
    st.session_state.game_over = False
    st.session_state.game_started = False
    st.session_state.score_saved = False
    st.session_state.user_guess = ""
    # ⚠️ questions_to_ask = 10 은 절대 건드리지 않음

# ------------------------- 다음 문제 -------------------------
def next_question():
    available_pool = [q for q in CELEBRITY_IMAGES if q not in st.session_state.used_questions]
    if not available_pool:
        st.session_state.used_questions.clear()
        available_pool = CELEBRITY_IMAGES.copy()

    image_file, answer = random.choice(available_pool)
    st.session_state.used_questions.add((image_file, answer))
    st.session_state.current_question = {
        "image_file": image_file,
        "correct": answer
    }

# ------------------------- 엔터키 제출 -------------------------
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
    st.session_state.user_guess = ""

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

    # ----------------- 사이드바 -----------------
    with st.sidebar:
        st.header("🏆 순위표")
        ranking = get_ranking("눈코입 퀴즈")
        df = pd.DataFrame(ranking, columns=["학번", "이름", "점수", "시간(초)"])
        df.index = df.index + 1
        df.index.name = "순위"
        st.dataframe(df, use_container_width=True)

        download_csv_by_game("눈코입 퀴즈", "celebrity_ranking.csv")

        if st.button("🔄 게임 재시작"):
            reset_game()
            st.rerun()

    # ----------------- 시작 전 -----------------
    if not st.session_state.game_started:
        st.info("게임 시작 버튼을 눌러주세요.")
        if st.button("게임 시작"):
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            next_question()
            st.rerun()
        return

    # ----------------- 게임 종료 -----------------
    if st.session_state.game_over:
        if st.session_state.elapsed_time is None:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time

        st.write(f"🎉 최종 점수: {st.session_state.score}/10")
        st.write(f"⏱ 걸린 시간: {st.session_state.elapsed_time:.1f}초")

        if st.session_state.wrong_answers:
            st.subheader("❌ 틀린 문제")
            st.table(pd.DataFrame(st.session_state.wrong_answers))

        if not st.session_state.score_saved:
            student_id = st.text_input("학번 입력")
            player_name = st.text_input("이름 입력")
            if st.button("점수 저장"):
                if student_id and player_name:
                    save_score(
                        st.session_state.game_type,
                        student_id,
                        player_name,
                        st.session_state.score,
                        st.session_state.elapsed_time
                    )
                    st.session_state.score_saved = True
                    st.success("저장 완료")
                else:
                    st.warning("학번이랑 이름 둘 다 필요함")
        else:
            st.success("이미 저장됨")

        return

    # ----------------- 문제 -----------------
    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index + 1} / 10")
    st.image(Image.open(q["image_file"]), width=300)

    st.text_input(
        "연예인 이름 입력 후 엔터",
        key="user_guess",
        on_change=process_answer
    )

if __name__ == "__main__":
    main()
