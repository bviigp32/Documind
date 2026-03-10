import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_document(file_path: str):
    print(f"문서를 불러옵니다: {file_path}")
    
    # 1. PDF 문서 로드 (페이지 단위로 읽어오기)
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    print(f"총 {len(documents)} 페이지를 성공적으로 읽어왔습니다.")

    # 2. 텍스트 분할 (Chunking)
    # LLM이 소화할 수 있는 크기로 자르고, 문맥이 끊기지 않게 겹치게(overlap) 설정합니다.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,   # 한 덩어리당 최대 글자 수
        chunk_overlap=50, # 앞뒤 덩어리가 겹치는 글자 수 (문맥 단절 방지)
        separators=["\n\n", "\n", " ", ""] # 문단 -> 줄바꿈 -> 띄어쓰기 순으로 안전하게 자름
    )

    chunks = text_splitter.split_documents(documents)
    print(f"문서를 총 {len(chunks)}개의 조각(Chunk)으로 쪼갰습니다!")

    # 3. 잘 쪼개졌는지 첫 번째 조각 살짝 확인해보기
    if chunks:
        print("\n[첫 번째 조각 미리보기]")
        print("-" * 50)
        print(chunks[0].page_content)
        print("-" * 50)

    return chunks

if __name__ == "__main__":
    # 프로젝트 최상단 폴더(documind)에서 실행한다고 가정했을 때의 경로
    target_pdf = "data/sample.pdf"
    
    if not os.path.exists(target_pdf):
        print(f"{target_pdf} 파일이 없습니다. data 폴더에 'sample.pdf'를 꼭 넣어주세요!")
    else:
        # 함수 실행
        process_document(target_pdf)