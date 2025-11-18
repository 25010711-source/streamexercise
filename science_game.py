import streamlit as st
import random, time, sqlite3
import pandas as pd
from github import Github

# -------------------------
# 데이터
# -------------------------
MOLECULES = [
    ("H2O", "물"), ("CO2", "이산화탄소"), ("O2", "산소"), ("N2", "질소"),
    ("CH4", "메테인"), ("C2H6", "에테인"), ("NaCl", "염화나트륨"), ("HCl", "염화수소"),
    ("NH3", "암모니아"), ("H2SO4", "황산"), ("CaCO3", "탄산칼슘"), ("NaHCO3", "탄산수소나트륨"),
    ("KNO3", "질산칼륨"), ("NaOH", "수산화나트륨"), ("KOH", "수산화칼륨"), ("Ca(OH)2", "수산화칼슘"),
    ("Mg(OH)2", "수산화마그네슘"), ("BaSO4", "황산바륨"), ("HNO3", "질산"), ("H3PO4", "인산"),
]

PERIODIC = [
    ("H", "수소"), ("He", "헬륨"), ("Li", "리튬"), ("Be", "베릴륨"), ("B", "붕소"),
    ("C", "탄소"), ("N", "질소"), ("O", "산소"), ("F", "플루오린"), ("Ne", "네온"),
    ("Na", "나트륨"), ("Mg", "마그네슘"), ("Al", "알루미늄"), ("Si", "규소"), ("P", "인"),
    ("S", "황"), ("Cl", "염소"), ("Ar", "아르곤"), ("K", "칼륨"), ("Ca", "칼슘")
]

# -------------------------
# SQLite 저장
# -------------------------
DB_PATH = "ranking.db"

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

def get_top_scores(game_type, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT player_name, score, elapsed_time FROM ranking
        WHERE game_type=?
        ORDER BY score DESC, elapsed_time ASC
        LIMIT ?
    """, (game_type, limit))
    rows = cur.fetchall()
    conn.close()
    return rows

# -------------------------
# GitHub 업로드
# -------------------------
def upload_db_to_github():
    try:
        token = st.secrets["GITHUB"]["TOKEN"]
        repo_name = st.secrets["GITHUB"]["REPO"]
        branch = st.secrets["GITHUB"].get("BRANCH","main")
        g = Github(token)
        repo = g.get_user().get_repo(repo_name)
        with open(DB_PATH,"rb") as f:
            content = f.read()
        try:
            file = repo.get_contents(DB_PATH, ref=branch)
            repo.update_file(DB_PATH, f"Update ranking {int(time.time())}", content, file.sha, branch=branch)
        except:
            repo.create_file(DB_PATH, f"Create ranking {int(time.time())}", content, branch=branch)
    except Exception as e:
        st.warning(f"GitHub 업로드 실패: {e}")

# -------------------------
# 게임 로직
# -------------------------
def generate_distractors(correct, pool, mode, n=3):
    choices = set()
    attempts = 0
    while len(choices) < n and attempts < 100:
        attempts += 1
        f,nm = random.choice(pool)
        candidate = nm if mode.endswith("_to_name") else f
        if candidate != correct:
            choices.add(candidate)
    return list(choices)

def next_question():
    mode = st.session_state.mode
    if mode=="molecule_all":
        current_mode=random.choice(["molecule_to_name","name_to_molecule"])
        pool=MOLECULES
    elif mode=="periodic_all":
        current_mode=random.choice(["periodic_to_name","name_to_periodic"])
        pool=PERIODIC
    else:
        current_mode=mode
        pool=MOLECULES if "molecule" in mode else PERIODIC
    available_pool=[m for m in pool if m not in st.session_state.used_questions]
    if not available_pool:
        st.session_state.used_questions.clear()
        available_pool=pool.copy()
    f,nm=random.choice(available_pool)
    st.session_state.used_questions.add((f,nm))
    if current_mode.endswith("_to_name"):
        prompt=f"다음 화학식의 이름은 무엇인가요? {f}" if "molecule" in current_mode else f"다음 원소기호의 이름은 무엇인가요? {f}"
        correct=nm
    else:
        prompt=f"다음 물질의 화학식은 무엇인가요? {nm}" if "molecule" in current_mode else f"다음 이름의 원소기호는 무엇인가요? {nm}"
        correct=f
    distractors=generate_distractors(correct,pool,current_mode)
    options=distractors+[correct]
    random.shuffle(options)
    st.session_state.current_question={"prompt":prompt,"options":options,"correct":correct}

def init_state():
    defaults={
        "score":0,"total":0,"streak":0,"question_index":0,
        "questions_to_ask":10,"game_type":"화학식 게임","mode":"molecule_to_name",
        "current_question":None,"used_questions":set(),"wrong_answers":[],
        "start_time":None,"elapsed_time":None,"game_over":False,"game_started":False
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

def reset_game():
    keys=["score","total","streak","question_index","current_question","used_questions",
          "wrong_answers","start_time","elapsed_time","game_over","game_started"]
    for key in keys:
        if key=="used_questions": st.session_state[key]=set()
        elif key=="wrong_answers": st.session_state[key]=[]
        elif key in ["game_over","game_started"]: st.session_state[key]=False
        else: st.session_state[key]=0 if isinstance(st.session_state.get(key),int) else None

# -------------------------
# Streamlit UI
# -------------------------
def main():
    st.set_page_config(page_title="과학 학습 게임")
    st.title("🧪 과학 학습 게임 (화학식 + 주기율표)")

    init_state()
    disabled_state = st.session_state.game_started

    # ---------------- Sidebar: 순위표 ----------------
    st.sidebar.header("🏆 순위표")
    for g_type in ["화학식 게임","주기율표 게임"]:
        st.sidebar.subheader(g_type)
        top_scores = get_top_scores(g_type)
        if top_scores:
            for i,(name,score,elapsed) in enumerate(top_scores,1):
                st.sidebar.write(f"{i}. {name} - {score}점 ({elapsed:.1f}s)")
        else:
            st.sidebar.write("아직 기록 없음")

    # ---------------- Sidebar: 설정 ----------------
    st.sidebar.header("게임 설정")
    game_type = st.sidebar.radio("게임 종류 선택",["화학식 게임","주기율표 게임"],index=0 if st.session_state.game_type=="화학식 게임" else 1, disabled=disabled_state)
    st.session_state.game_type=game_type

    if game_type=="화학식 게임":
        selected_mode=st.sidebar.radio("모드 선택",["전체","분자식 → 이름","이름 → 분자식"],index=0)
    else:
        selected_mode=st.sidebar.radio("모드 선택",["전체","원소기호 → 이름","이름 → 원소기호"],index=0)

    st.session_state.questions_to_ask = st.sidebar.slider("문제 수",5,20,10,disabled=disabled_state)

    # ---------------- 게임 시작 화면 ----------------
    if not st.session_state.game_started:
        st.info("설정 확인 후 '게임 시작' 버튼을 눌러주세요.")
        if st.button("게임 시작"):
            st.session_state.game_started=True
            st.session_state.start_time=time.time()
            # 모드 적용
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

    # ---------------- 게임 종료 화면 ----------------
    if st.session_state.game_over:
        if st.session_state.elapsed_time is None:
            st.session_state.elapsed_time=time.time()-st.session_state.start_time
        st.write(f"📝 게임 종류: {st.session_state.game_type}")
        st.write(f"📝 선택한 모드: {selected_mode}")
        st.write(f"🎉 최종 점수: {st.session_state.score}/{st.session_state.questions_to_ask}")
        st.write(f"⏱ 걸린 시간: {st.session_state.elapsed_time:.1f}초")

        # 틀린 문제 표시
        if st.session_state.wrong_answers:
            st.subheader("❌ 틀린 문제")
            df_wrong=pd.DataFrame([{"번호":wa["index"],"문제":wa["question"],"선택":wa["your_answer"],"정답":wa["correct_answer"]} for wa in st.session_state.wrong_answers])
            st.table(df_wrong)

        # 만점일 때만 이름 입력
        max_score = st.session_state.questions_to_ask
        if st.session_state.score==max_score:
            player_name = st.text_input("이름 입력 (만점만 저장 가능)")
            if player_name:
                save_score(st.session_state.game_type, player_name, st.session_state.score, st.session_state.elapsed_time)
                upload_db_to_github()
                st.success("점수가 저장되고 GitHub에 업로드되었습니다.")

        if st.button("게임 재시작"):
            reset_game()
            st.rerun()
        return

    # ---------------- 게임 진행 ----------------
    q = st.session_state.current_question
    st.subheader(f"문제 {st.session_state.question_index+1}/{st.session_state.questions_to_ask}")
    st.write(q["prompt"])

    choice=st.radio("정답 선택:",q["options"],index=None,key=f"choice_{st.session_state.question_index}")

    if choice is not None:
        st.session_state.total+=1
        if choice==q["correct"]:
            st.session_state.score+=1
            st.session_state.streak+=1
            st.success("정답입니다!")
        else:
            st.session_state.streak=0
            st.error(f"오답입니다. 정답: {q['correct']}")
            st.session_state.wrong_answers.append({"index":st.session_state.question_index+1,"question":q["prompt"],"your_answer":choice,"correct_answer":q["correct"]})

        st.session_state.question_index+=1
        if st.session_state.question_index>=st.session_state.questions_to_ask:
            st.session_state.game_over=True
        else:
            next_question()
        st.rerun()

    st.progress(st.session_state.question_index/st.session_state.questions_to_ask)

if __name__=="__main__":
    main()
