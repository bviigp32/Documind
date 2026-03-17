import streamlit as st
import requests
import uuid

# 페이지 기본 설정
st.set_page_config(page_title="DocuMind AI", layout="wide")

st.title("DocuMind 사내 지식 Q&A 시스템")
st.write("문서를 업로드하고 무엇이든 질문해 보세요. 이전 대화의 문맥을 모두 기억합니다.")

# API 서버 주소 설정
API_BASE_URL = "http://localhost:8000"

# 세션 ID 및 대화 기록 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바: 문서 업로드 기능
with st.sidebar:
    st.header("문서 업로드")
    uploaded_file = st.file_uploader("PDF 파일을 선택하세요", type=["pdf"])
    
    if st.button("업로드 및 처리 시작"):
        if uploaded_file is not None:
            with st.spinner("서버로 전송 중..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    response = requests.post(f"{API_BASE_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("업로드 성공. 백그라운드에서 문서를 분석하고 있습니다.")
                    else:
                        st.error(f"업로드 실패: {response.text}")
                except Exception as e:
                    st.error("API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        else:
            st.warning("먼저 파일을 선택해 주세요.")

# 메인 화면: 기존 대화 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 메인 화면: 사용자 질문 입력창
if prompt := st.chat_input("문서 내용에 대해 질문해 주세요."):
    # 사용자 질문을 화면에 표시하고 세션에 저장
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 요청 및 출력
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("답변을 생성하고 있습니다...")

        payload = {
            "session_id": st.session_state.session_id,
            "question": prompt
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/ask", json=payload)
            if response.status_code == 200:
                answer = response.json().get("answer", "")
                message_placeholder.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = response.json().get("detail", "알 수 없는 오류가 발생했습니다.")
                message_placeholder.error(f"서버 오류: {error_msg}")
        except Exception as e:
            message_placeholder.error("API 서버에 연결할 수 없습니다.")