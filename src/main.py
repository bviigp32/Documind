import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from operator import itemgetter
from src.worker import process_document_task

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(title="DocuMind AI API", description="대화 기록이 유지되는 RAG 기반 질의응답 서버")

# 세션 구분을 위해 session_id 필드 추가
class QuestionRequest(BaseModel):
    session_id: str
    question: str

class AnswerResponse(BaseModel):
    session_id: str
    question: str
    answer: str

conversational_rag_chain = None
CHROMA_PERSIST_DIR = "./chroma_db"
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_session_history(session_id: str):
    """PostgreSQL 데이터베이스에서 특정 세션의 대화 기록을 불러옵니다."""
    return SQLChatMessageHistory(session_id, connection_string=DATABASE_URL)

@app.on_event("startup")
def startup_event():
    global conversational_rag_chain
    print("서버 시작 중: 데이터베이스 및 모델 연결 초기화...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 과거 대화 기록(history)을 주입할 수 있도록 MessagesPlaceholder 추가
    prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 제공된 문맥(Context)을 바탕으로 질문에 답하세요. 문맥에 없는 내용은 절대 지어내지 마세요.\n\n문맥:\n{context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=GEMINI_API_KEY
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    base_chain = (
        RunnablePassthrough.assign(
            context=itemgetter("question") | retriever | format_docs
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    # 데이터베이스와 연동된 메모리 체인 래핑
    conversational_rag_chain = RunnableWithMessageHistory(
        base_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="history",
    )
    print("초기화 완료: DocuMind API 서버 준비 완료.")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
        
    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    task = process_document_task.delay(file_path)
    return {"message": "백그라운드 처리 지시 성공", "filename": file.filename, "task_id": task.id}

@app.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    if not conversational_rag_chain:
        raise HTTPException(status_code=500, detail="RAG 체인이 초기화되지 않았습니다.")
    
    try:
        # session_id를 기준으로 대화 기록을 관리하며 답변 생성
        answer = conversational_rag_chain.invoke(
            {"question": req.question},
            config={"configurable": {"session_id": req.session_id}}
        )
        return AnswerResponse(session_id=req.session_id, question=req.question, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {str(e)}")