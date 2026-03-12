import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[경고] .env 파일에서 GEMINI_API_KEY를 찾지 못했습니다!")

CHROMA_PERSIST_DIR = "./chroma_db"

def setup_rag_chain():
    print("임베딩 모델 로드 중...")
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    print("데이터베이스(ChromaDB) 연결 중...")
    vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    template = """다음 제공된 문맥(Context)을 바탕으로 질문(Question)에 답하세요. 
문맥에 없는 내용은 절대 지어내지 말고 "제공된 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요.

문맥:
{context}

질문: {question}

답변:"""
    prompt = PromptTemplate.from_template(template)

    print("구글 제미나이(Gemini 2.5 Flash) 사서 고용 중...")

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

    return rag_chain

if __name__ == "__main__":
    print("DocuMind 시스템을 초기화합니다...")
    chain = setup_rag_chain()
    
    question = "문서의 핵심 내용이 뭐야? 요약해 줘."
    
    print(f"\n사용자 질문: {question}")
    print("DocuMind 생각 중... (문서 검색 및 답변 생성)")
    
    answer = chain.invoke(question)
    
    print("-" * 50)
    print(f"AI 답변:\n{answer}")
    print("-" * 50)