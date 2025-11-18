import streamlit as st
import random, time, sqlite3
import pandas as pd
from typing import List, Tuple

# GitHub 업로드용
from github import Github

# -------------------------
# 설정
# -------------------------
DB_FILE = "./ranking.db"
GITHUB_TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"  # 본인 토큰
REPO_NAME = "YOUR_REPO_NAME"  # 본인 repo
BRANCH = "main"
PATH_IN_REPO = "ranking.db"

# -------------------------
# 데이터
# -------------------------
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

# -------------------------
# DB 초기화
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_type TEXT,
            player_name TEXT,
            score INTEGER,
            elapsed_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# -------------------------
# 점수 저장
# -------------------------
def save_score(game_type, player_name, score, elapsed_time):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO ranking (game_type, player_name, score, elapsed_time) VALUES (?, ?, ?, ?)",
                (game_type, player_name, score, elapsed_time))
    conn.commit()
    conn.close()
    upload_db_to_github()

# -------------------------
# GitHub 업로드
# -------------------------
def upload_db_to_github():
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_user().get_repo(REPO_NAME)
        with open(DB_FILE, "rb") as f:
            content = f.read()
        try:
            file = repo.get_contents(PATH_IN_REPO, ref=BRANCH)
            repo.update_file(PATH_IN_REPO, f"Update ranking {int(time.time())}", content, file.sha, branch=BRANCH)
        except:
            repo.create_file(PATH_IN_REPO, f"Create ranking {int(time.time())}", content, branch=BRANCH)
    except Exception as e:
        st.warning(f"GitHub 업로드 실패: {e}")

# -------------------------
# 순위 조회
# -------------------------
def get_ranking(game_type, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT player_name, score, elapsed_time FROM ranking WHERE game_type=? ORDER BY score DESC, elapsed_time ASC LIMIT ?",
                (game_type, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------------
# 보기 생성
# -------------------------
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

# -------------------------
# 상태 초기화
# -------------------------
def init_state():
    defaults = {
        "score":0, "total":0, "streak":0, "question_index":0,
        "questions_to_ask":10, "game_type":"화학식 게임", "mode":"molecule_to_name",
        "current_question":None, "used_questions":set(), "wrong_answers":[],
        "start_time":None, "elapsed_time":None, "game_over":False, "game_started":False,
        "player_name_input":""
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def reset_game():
    for key in ["score","total","streak","question_index","current_question","used_questions","wrong_answers","start_time","elapsed_time","game_over","game_started","player_name_input"]:
        if key=="used_questions": st.session_state[key]=set()
        elif key=="wrong_answers": st.session_state[key]=[]
        elif key in ["game_over","game_started"]: st.session_state[key]=False
        elif key=="player_name_input": st.session_state[key]=""
        else: st.session_state[key]=0 if isinstance(st.session_state.get(key),int) else None

# -------------------------
# 다음 문제
# -------------------------
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

# -------------------------
# 메인 UI
# -------------------------
def main():
    st.set_page_config(page_title="화학식/주기율표 게임")
    st.title("🧪 화학식/주기율표 게임")

    init_db()
    init_state()
    disabled_state = st.session_state.game_started

    # ---------------- Sidebar
    with st.sidebar:
        st.header("순위표")
        st.subheader("화학식 게임")
        df1=pd.DataFrame(get_ranking("화학식 게임"),columns=["이름","점수","시간(초)"])
        st.table(df1)
        st.subheader("주기율표 게임")
        df2=pd.DataFrame(get_ranking("주기율표 게임"),columns=["이름","점수","시간(초)"])
        st.table(df2)

    # ----------------- 게임 시작 화면 -----------------
    if not st.session_state.game_started:
        st.info("설정 후 게임 시작 버튼을 눌러주세요.")

        game_type = st.selectbox("게임 종류 선택", ["화학식 게임","주기율표 게임"])
        if game_type=="화학식 게임":
            selected_mode = st.selectbox("모드 선택", ["전체","분자식 → 이름","이름 → 분자식"])
        else:
            selected_mode = st.selectbox("모드 선택", ["전체","원소기호 → 이름","이름 → 원소기호"])
        st.session_state.questions_to_ask = st.slider("문제 수",5,20,10)

        if st.button("게임 시작"):
            st.session_state.game_started=True
            st.session_state.start_time=time.time()
            st.session_state.game_type = game_type
            # 선택 모드 세션 저장
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

    # ----------------- 게임 종료 화면 -----------------
    if st.session_state.game_over:
        if st.session_state.elapsed_time is None:
            st.session_state.elapsed_time = time.time() - st.session_state.start_time

        st.write(f"📝 게임 종류: {st.session_state.game_type}")
        st.write(f"📝 선택한 모드: {st.session_state.mode}")
        st.write(f"🎉 최종 점수: {st.session_state.score}/{st.session_state.total}")
        st.write(f"⏱ 걸린 시간: {st.session_state.elapsed_time:.1f}초")

        # 만점일 경우 이름 입력 가능
        max_score = st.session_state.questions_to_ask
        if st.session_state.score==max_score:
            st.session_state.player_name_input = st.text_input("만점 달성! 이름을 입력하세요", st.session_state.player_name_input)
            if st.session_state.player_name_input:
                save_score(st.session_state.game_type, st.session_state.player_name_input, st.session_state.score, st.session_state.elapsed_time)
                st.success("점수가 저장되고 GitHub에 업로드되었습니다.")

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
