import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 환경변수 로드
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# FastAPI 앱 초기화
app = FastAPI(title="DocuMind AI API", description="RAG 기반 사내 문서 질의응답 서버")

# 데이터 입출력을 위한 Pydantic 모델 정의
class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    question: str
    answer: str

# 전역 변수로 체인 저장
rag_chain = None
CHROMA_PERSIST_DIR = "./chroma_db"

@app.on_event("startup")
def startup_event():
    """서버가 시작될 때 무거운 AI 모델과 DB를 미리 메모리에 적재합니다."""
    global rag_chain
    print("서버 시작 중: 임베딩 모델, 벡터 DB, 제미나이 연결 초기화...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    template = """다음 제공된 문맥(Context)을 바탕으로 질문(Question)에 답하세요. 
문맥에 없는 내용은 절대 지어내지 말고 "제공된 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요.

문맥:
{context}

질문: {question}

답변:"""
    prompt = PromptTemplate.from_template(template)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=GEMINI_API_KEY
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("초기화 완료: DocuMind API 서버가 요청을 받을 준비가 되었습니다.")

@app.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    """사용자의 질문을 받아 RAG 체인을 통해 답변을 생성하고 반환합니다."""
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG 체인이 초기화되지 않았습니다.")
    
    try:
        # AI 모델에 질문 전달 및 답변 생성
        answer = rag_chain.invoke(req.question)
        return AnswerResponse(question=req.question, answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 생성 중 오류 발생: {str(e)}")