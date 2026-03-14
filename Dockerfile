# 1. 파이썬 3.11 슬림 버전 이미지를 기반으로 설정
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 및 벡터 데이터베이스 복사
COPY src/ src/
COPY chroma_db/ chroma_db/

# 5. 컨테이너 포트 개방
EXPOSE 8000

# 6. 서버 실행 명령어
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]