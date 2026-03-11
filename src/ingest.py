import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ChromaDB가 로컬에 저장될 폴더 경로 지정
CHROMA_PERSIST_DIR = "./chroma_db"

def process_and_store_document(file_path: str):
    print(f"문서를 불러옵니다: {file_path}")
    
    # 1. PDF 문서 로드
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # 2. 텍스트 분할 (Chunking)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,   
        chunk_overlap=50, 
        separators=["\n\n", "\n", " ", ""] 
    )
    chunks = text_splitter.split_documents(documents)
    print(f"문서를 총 {len(chunks)}개의 조각(Chunk)으로 쪼갰습니다!")

    # 3. 임베딩 모델 설정 (한국어 특화 무료 오픈소스 모델 사용)
    print("임베딩 모델을 불러오는 중입니다... (최초 실행 시 다운로드에 시간이 걸릴 수 있습니다)")
    embeddings = HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask",
        model_kwargs={'device': 'cpu'}, # 맥북 환경에서도 안정적으로 돌아가도록 CPU 기본 설정
        encode_kwargs={'normalize_embeddings': True}
    )

    # 4. 벡터 DB(Chroma)에 변환된 데이터 저장
    print("조각난 텍스트를 숫자로 변환하여 벡터 DB에 저장합니다. 잠시만 기다려주세요...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    print(f"성공적으로 ChromaDB에 저장되었습니다! (저장 위치: {CHROMA_PERSIST_DIR})")
    return vectorstore

if __name__ == "__main__":
    target_pdf = "data/sample.pdf"
    
    if not os.path.exists(target_pdf):
        print(f"{target_pdf} 파일이 없습니다. data 폴더에 'sample.pdf'를 꼭 넣어주세요!")
    else:
        process_and_store_document(target_pdf)