# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("게임 설정 & 순위")

    # 게임 재시작
    if st.button("🔄 게임 재시작"):
        reset_game()
        st.rerun()

    # ---------------- 게임 종류 & 모드 선택 ----------------
    st.subheader("게임 종류 선택")
    game_type = st.radio(
        "",
        ["화학식 게임","주기율표 게임"],
        index=0 if st.session_state.game_type=="화학식 게임" else 1,
        disabled=disabled_state
    )
    st.session_state.game_type = game_type

    if game_type == "화학식 게임":
        selected_mode = st.radio(
            "모드 선택",
            ["전체", "분자식 → 이름", "이름 → 분자식"],
            index=0,
            disabled=disabled_state
        )
    else:
        selected_mode = st.radio(
            "모드 선택",
            ["전체", "원소기호 → 이름", "이름 → 원소기호"],
            index=0,
            disabled=disabled_state
        )

    # 문항 수 선택
    st.subheader("문항 수")
    questions_to_ask = st.slider("문제 수 선택", 5, 20, 10, disabled=disabled_state)
    st.session_state.questions_to_ask = questions_to_ask

    # 모드 내부 코드 적용
    if selected_mode=="전체":
        st.session_state.mode = "molecule_all" if game_type=="화학식 게임" else "periodic_all"
    elif selected_mode=="분자식 → 이름": st.session_state.mode="molecule_to_name"
    elif selected_mode=="이름 → 분자식": st.session_state.mode="name_to_molecule"
    elif selected_mode=="원소기호 → 이름": st.session_state.mode="periodic_to_name"
    elif selected_mode=="이름 → 원소기호": st.session_state.mode="name_to_periodic"

    # ---------------- 순위표 가로 스크롤 ----------------
    st.subheader("순위표 (가로 스크롤 가능)")

    ranking1 = get_ranking("화학식 게임")
    ranking2 = get_ranking("주기율표 게임")

    df1 = pd.DataFrame(ranking1, columns=["학번","이름","점수","시간(초)"])
    df1.insert(0, "게임", "화학식 게임")
    df1.index = df1.index + 1
    df1.index.name = "순위"

    df2 = pd.DataFrame(ranking2, columns=["학번","이름","점수","시간(초)"])
    df2.insert(0, "게임", "주기율표 게임")
    df2.index = df2.index + 1
    df2.index.name = "순위"

    st.dataframe(df1, use_container_width=True)
    st.dataframe(df2, use_container_width=True)

    # ---------------- CSV 다운로드 ----------------
    show_csv_download()
