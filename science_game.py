# ---------------------- 게임 종료 후 점수 저장 ----------------------
st.subheader("점수 저장")

# 저장 버튼은 항상 표시
if st.button("점수 저장"):

    student_id = st.text_input("학번 입력:", key="student_id", value="")
    player_name = st.text_input("이름 입력:", key="player_name", value="")

    # 학번이나 이름이 비어있으면 안내 후 저장 불가
    if not student_id or not player_name:
        st.warning("학번과 이름을 모두 입력해야 점수를 저장할 수 있습니다.")
    # 만점이 아니면 저장 불가
    elif st.session_state.score != st.session_state.questions_to_ask:
        st.info("만점일 경우에만 점수를 저장할 수 있습니다.")
    else:
        save_score(
            st.session_state.game_type,
            student_id,
            player_name,
            st.session_state.score,
            st.session_state.elapsed_time or 0
        )
        st.success("만점이므로 점수가 저장되었습니다.")
