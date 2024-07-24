import streamlit as st
import openai
import time

# Streamlit 앱 설정
st.set_page_config(page_title="ChatBot Web App", page_icon="🤖")

# OpenAI API 키 입력
api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password")

# Assistant ID 설정
ASSISTANT_ID = "asst_a7w12byNAgKRJP6ziutDRLfX"

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# OpenAI 클라이언트 설정
if api_key:
    openai.api_key = api_key

    # 채팅 인터페이스
    st.title("ChatBot Web App")

    # 이전 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant의 응답 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                # Thread 생성 또는 가져오기
                if not st.session_state.thread_id:
                    thread = openai.beta.threads.create()
                    st.session_state.thread_id = thread.id
                
                # 메시지 추가
                openai.beta.threads.messages.create(
                    thread_id=st.session_state.thread_id,
                    role="user",
                    content=prompt
                )

                # 실행 생성 및 응답 대기
                run = openai.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=ASSISTANT_ID
                )

                while run.status != "completed":
                    time.sleep(1)
                    run = openai.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )

                # 응답 가져오기
                messages = openai.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                # 최신 응답 표시
                assistant_response = messages.data[0].content[0].text.value
                full_response = assistant_response
                message_placeholder.markdown(full_response)
            
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")
                full_response = "죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다."
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.warning("OpenAI API 키를 입력해주세요.")