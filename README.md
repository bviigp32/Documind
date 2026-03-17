# DocuMind: AI 기반 사내 지식 질의응답(Q&A) 백엔드

> **"검색 증강 생성(RAG) 아키텍처를 활용한 지능형 문서 검색 및 답변 API 서버"**
> 방대한 사내 규정집과 PDF 문서들을 벡터 데이터베이스에 저장하고, 사용자의 질문에 맞춰 대형 언어 모델(LLM)이 정확한 근거를 바탕으로 답변을 생성하는 AI 백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![LangChain](https://img.shields.io/badge/LangChain-LLM%20Framework-1C3C3C?logo=langchain) ![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6F00?logo=chroma) ![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?logo=google) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![Redis](https://img.shields.io/badge/Redis-Message%20Broker-DC382D?logo=redis) ![Celery](https://img.shields.io/badge/Celery-Task%20Queue-37814A?logo=celery) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql)

## 프로젝트 개요 (Overview)
* **목표:** 사내 문서(PDF 등)를 기반으로 환각 현상(Hallucination) 없이 정확한 정보를 제공하는 RAG 기반 질의응답 API 서버 구축.
* **기간:** 2026.03.09 ~ (진행 중)
* **역할:** AI 백엔드 엔지니어링 (데이터 전처리, 임베딩 파이프라인, 벡터 DB 구축, LLM 연동, API 서빙, 비동기 분산 처리, 대화형 메모리 관리)

## 시스템 아키텍처 (System Architecture)
1. **Data Ingestion (문서 로드 및 분할):** `PyPDF` 등을 활용해 문서를 텍스트로 추출하고 의미 단위로 분할(Text Split).
2. **Asynchronous Processing (비동기 분산 처리):** 무거운 문서 임베딩 작업을 메인 서버에서 분리하여, `Redis` 메시지 브로커와 `Celery` 워커를 통해 백그라운드에서 병렬 처리.
3. **Embedding & Vector Storage (벡터 변환 및 저장):** `HuggingFace` 오픈소스 모델을 활용해 텍스트를 고차원 벡터로 변환(Embedding)하고, `ChromaDB`에 적재.
4. **Conversational Memory (대화 기록 관리):** `PostgreSQL` 데이터베이스를 연동하여 사용자의 세션별 질문과 답변 기록을 영구 저장하고, 연속적인 대화의 문맥(Context)을 유지.
5. **Retrieval-Augmented Generation (검색 증강 생성):** 사용자의 질문과 가장 유사한 문서를 벡터 DB에서 검색한 뒤, 과거 대화 기록과 함께 프롬프트에 주입하여 **Google Gemini 2.5 Flash** 모델이 답변을 생성.
6. **API Serving (서비스 서빙):** `FastAPI`를 활용하여 사용자 질문을 받고 AI의 답변을 반환하는 초고속 RESTful API 엔드포인트 구축.

## 개발 로그 (Development Log)
* **Phase 1~4 (기반 세팅 및 RAG 파이프라인 구축):** FastAPI 환경 세팅, 문서 청킹, HuggingFace 임베딩, ChromaDB 적재 및 Google Gemini 2.5 Flash 연동 완료. (Day 1~4)
* **Phase 5~6 (API 서빙 및 컨테이너화):** RESTful API 엔드포인트(`/ask`) 구축 및 Docker 기반 배포 환경 세팅. (Day 5~6)
* **Phase 7 (비동기 분산 처리):** 대용량 문서 처리 시 발생하는 병목 현상을 방지하기 위해 `Redis`와 `Celery`를 도입하여 백그라운드 워커 기반의 비동기 아키텍처 구축. (Day 7)
* **Phase 8 (대화형 메모리 구축):** `PostgreSQL`을 연동하여 사용자의 세션별 대화 기록을 저장하고, LangChain의 `RunnableWithMessageHistory`를 통해 이전 대화의 문맥을 기억하는 지능형 대화형(Conversational) RAG 시스템 완성. (Day 8)
* **Phase 9 (프론트엔드 구축):** `Streamlit`을 활용하여 사용자가 PDF 문서를 업로드하고 대화형으로 질의응답을 진행할 수 있는 직관적인 웹 UI 구현 완료. (Day 9)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, Docker** | 비동기 기반 초고속 AI 질의응답 API 서버 구축 및 배포 |
| **Task Queue** | **Celery, Redis** | 대용량 문서 처리 작업을 위한 메시지 브로커 및 백그라운드 워커 |
| **AI & LLM** | **LangChain, Google Gemini** | LLM 파이프라인(RAG) 구성 및 생성형 AI 모델 적용 |
| **Database** | **ChromaDB, PostgreSQL** | 벡터 저장소(Vector DB) 및 사용자 세션별 대화 기록(Memory) 관리 |

## 실행 방법 (How to Run)

### 1. 환경 변수 세팅
최상단 경로에 `.env` 파일을 만들고 아래 키를 입력하세요.
```env
GEMINI_API_KEY=AIzaSy...
DATABASE_URL=postgresql://documind:documind_pass@localhost:5432/documind_db

```

### 2. 로컬 환경에서 실행

```bash
# 필수 패키지 설치
pip install -r requirements.txt

# Step 1: Redis 및 PostgreSQL 서버 실행 (Docker 활용)
docker run -d -p 6379:6379 --name documind-redis redis:alpine
docker run -d -p 5432:5432 -e POSTGRES_USER=documind -e POSTGRES_PASSWORD=documind_pass -e POSTGRES_DB=documind_db --name documind-postgres postgres:15-alpine

# Step 2: Celery 워커 실행 (새 터미널 창)
celery -A src.worker.celery_app worker --loglevel=info

# Step 3: FastAPI 서버 실행 (새 터미널 창)
uvicorn src.main:app --reload

```

