# ... (이전 코드 동일)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("게임 설정 & 순위")
    # 게임 재시작 버튼
    if st.button("🔄 게임 재시작"):
        reset_game()
        st.rerun()

    st.subheader("순위표")
    # 세로 2열 배치
    ranking1 = get_ranking("화학식 게임")
    ranking2 = get_ranking("주기율표 게임")

    # 세로 2열: st.columns(1) × 2 대신 그냥 아래로 배치
    st.subheader("화학식 게임 1~10등")
    if ranking1:
        df1 = pd.DataFrame(ranking1, columns=["학번","이름","점수","시간(초)"])
        df1.index = df1.index + 1
        df1.index.name = "순위"
        st.table(df1)

    st.subheader("주기율표 게임 1~10등")
    if ranking2:
        df2 = pd.DataFrame(ranking2, columns=["학번","이름","점수","시간(초)"])
        df2.index = df2.index + 1
        df2.index.name = "순위"
        st.table(df2)

    st.subheader("게임 종류 선택")
    game_type = st.radio(
        "",
        ["화학식 게임","주기율표 게임"],
        index=0 if st.session_state.game_type=="화학식 게임" else 1,
        disabled=disabled_state
    )
    st.session_state.game_type = game_type

# ... (나머지 코드는 이전과 동일)
