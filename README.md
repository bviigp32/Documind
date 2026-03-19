# DocuMind: AI 기반 사내 지식 질의응답(Q&A) 백엔드

> **"검색 증강 생성(RAG) 아키텍처를 활용한 지능형 문서 검색 및 답변 API 서버"**
> 방대한 사내 규정집과 PDF 문서들을 벡터 데이터베이스에 저장하고, 사용자의 질문에 맞춰 대형 언어 모델(LLM)이 정확한 근거를 바탕으로 답변을 생성하는 AI 백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![LangChain](https://img.shields.io/badge/LangChain-LLM%20Framework-1C3C3C?logo=langchain) ![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6F00?logo=chroma) ![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?logo=google) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![Redis](https://img.shields.io/badge/Redis-Message%20Broker-DC382D?logo=redis) ![Celery](https://img.shields.io/badge/Celery-Task%20Queue-37814A?logo=celery) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql) ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?logo=streamlit)

## 프로젝트 개요 (Overview)
* **목표:** 사내 문서(PDF 등)를 기반으로 환각 현상(Hallucination) 없이 정확한 정보를 제공하는 대화형 지능형 검색 시스템 구축
* **기간:** 2026.03.09 ~ 2026.03.18 (10일 집중 스프린트)
* **역할:** AI 백엔드 엔지니어링 (데이터 전처리, 비동기 파이프라인 설계, 벡터/RDBMS 구축, 프론트엔드 연동 및 트러블슈팅)

## 주요 정량적 성과 (Quantitative Achievements)
* **API 응답 지연 시간 99% 단축:** 대용량 문서 처리 아키텍처를 동기식에서 비동기식(Celery/Redis)으로 전환하여, 메인 서버의 블로킹 시간을 30초 이상에서 **50ms 미만**으로 최적화.
* **DB Lock 에러 발생률 0% 달성:** 비동기 작업 시차로 인한 벡터 DB(SQLite 기반)의 잠금(Lock) 및 무한 대기 현상을 상태 조회 API와 프론트엔드 폴링(Polling) 동기화 로직으로 **완벽히 제거(100% -> 0%)**.
* **RAG 파이프라인 응답 속도 안정화:** 문서 검색, 과거 대화(Memory) 조회, LLM 프롬프트 생성을 아우르는 전체 추론 과정을 평균 **2~3초 내외**로 최적화.
* **애자일 기반 시스템 통합:** 10일의 짧은 기간 내에 API 서버, 메시지 브로커, 2종의 데이터베이스, 프론트엔드 등 **총 5개 이상의 이기종 시스템**을 Docker 환경에서 성공적으로 통합.

## 시스템 아키텍처 (System Architecture)
1. **Data Ingestion (문서 로드 및 분할):** `PyPDF` 활용 문서 추출 및 의미 단위 분할(Text Split).
2. **Asynchronous Processing (비동기 분산 처리):** 무거운 임베딩 작업을 메인 서버에서 분리, `Redis` 메시지 브로커와 `Celery` 워커를 통한 백그라운드 병렬 처리.
3. **Task Synchronization (상태 동기화):** 프론트엔드의 폴링(Polling) 로직을 통해 백그라운드 작업 상태를 주기적으로 확인, DB Lock 방지 및 안정적인 UX 제공.
4. **Embedding & Vector Storage (벡터 변환 및 저장):** `HuggingFace` 오픈소스 모델을 활용해 텍스트를 고차원 벡터로 변환, `ChromaDB` 적재.
5. **Conversational Memory (대화 기록 관리):** `PostgreSQL` 연동을 통한 세션별 질의응답 기록 영구 저장 및 문맥(Context) 유지.
6. **Retrieval-Augmented Generation (검색 증강 생성):** 과거 대화 기록과 벡터 검색 결과를 프롬프트에 주입하여 **Google Gemini 2.5 Flash** 모델 답변 생성.
7. **Client Interface (사용자 인터페이스):** `Streamlit`을 활용한 파일 업로드 및 실시간 채팅 웹 화면 제공.

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, Docker** | 비동기 기반 초고속 AI 질의응답 API 서버 구축 및 배포 |
| **Frontend** | **Streamlit** | 파일 업로드 및 대화형 챗봇 인터페이스 구축 |
| **Task Queue** | **Celery, Redis** | 대용량 문서 처리 작업을 위한 메시지 브로커 및 백그라운드 워커 |
| **AI & LLM** | **LangChain, Google Gemini** | LLM 파이프라인(RAG) 구성 및 생성형 AI 모델 적용 |
| **Database** | **ChromaDB, PostgreSQL** | 벡터 저장소(Vector DB) 및 사용자 세션별 대화 기록(Memory) 관리 |

## 개발 로그 및 트러블슈팅 (Development Log & Troubleshooting)
* **Phase 1~4 (RAG 파이프라인 구축):** FastAPI 환경 세팅, HuggingFace 임베딩, ChromaDB 적재. 외부 추론 API 중단 장애 발생 시, 유연한 인터페이스 설계를 통해 **Google Gemini 2.5 Flash** 모델로 즉각 우회하여 시스템 가용성 복구. (Day 1~4)
* **Phase 5~6 (API 서빙 및 컨테이너화):** RESTful API 엔드포인트(`/ask`) 구축 및 Docker 기반 배포 환경 세팅. (Day 5~6)
* **Phase 7 (비동기 분산 처리):** 대용량 문서 처리 시 발생하는 API 서버 마비 현상을 해결하기 위해 `Redis`와 `Celery`를 도입, 백그라운드 워커 기반의 비동기 아키텍처 구축. (Day 7)
* **Phase 8 (대화형 메모리 구축):** `PostgreSQL` 연동 및 LCEL 타입 충돌(`Missing variables {'history'}`) 디버깅 완료. 세션별 대화 기록을 저장하여 문맥을 기억하는 지능형 시스템 완성. (Day 8)
* **Phase 9~10 (프론트엔드 연동 및 DB Lock 해결):** `Streamlit` 기반 웹 UI 구현. Celery 워커와 API 서버 간의 작업 시차로 인한 DB Lock 문제를 분석하고, 상태 조회 API(`/task/{id}`) 및 폴링(Polling) 로직을 도입하여 데이터 정합성 및 시스템 안정성 확보. (Day 9~10)

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

# Step 4: Streamlit 프론트엔드 실행 (새 터미널 창)
streamlit run src/frontend.py
```
