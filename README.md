# DocuMind: AI 기반 사내 지식 질의응답(Q&A) 백엔드

> **"검색 증강 생성(RAG) 아키텍처를 활용한 지능형 문서 검색 및 답변 API 서버"**
> 방대한 사내 규정집과 PDF 문서들을 벡터 데이터베이스에 저장하고, 사용자의 질문에 맞춰 대형 언어 모델(LLM)이 정확한 근거를 바탕으로 답변을 생성하는 AI 백엔드 시스템입니다.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi) ![LangChain](https://img.shields.io/badge/LangChain-LLM%20Framework-1C3C3C?logo=langchain) ![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6F00?logo=chroma) ![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?logo=google) ![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker) ![Redis](https://img.shields.io/badge/Redis-Message%20Broker-DC382D?logo=redis) ![Celery](https://img.shields.io/badge/Celery-Task%20Queue-37814A?logo=celery)

## 프로젝트 개요 (Overview)
* **목표:** 사내 문서(PDF 등)를 기반으로 환각 현상(Hallucination) 없이 정확한 정보를 제공하는 RAG 기반 질의응답 API 서버 구축.
* **기간:** 2026.03.09 ~ (진행 중)
* **역할:** AI 백엔드 엔지니어링 (데이터 전처리, 임베딩 파이프라인, 벡터 DB 구축, LLM 연동, API 서빙, 도커 컨테이너화, 비동기 분산 처리)

## 시스템 아키텍처 (System Architecture)
1. **Data Ingestion (문서 로드 및 분할):** `PyPDF` 등을 활용해 문서를 텍스트로 추출하고 의미 단위로 분할(Text Split).
2. **Asynchronous Processing (비동기 분산 처리):** 무거운 문서 임베딩 작업을 메인 서버에서 분리하여, `Redis` 메시지 브로커와 `Celery` 워커를 통해 백그라운드에서 병렬 처리.
3. **Embedding & Vector Storage (벡터 변환 및 저장):** `HuggingFace` 오픈소스 모델을 활용해 텍스트를 고차원 벡터로 변환(Embedding)하고, 이를 초고속으로 검색할 수 있는 `ChromaDB`에 적재.
4. **Retrieval-Augmented Generation (검색 증강 생성):** 사용자의 질문과 가장 유사한 문서를 벡터 DB에서 검색(Retrieve)한 뒤, 해당 문맥을 프롬프트에 주입하여 **Google Gemini 2.5 Flash** 모델이 답변을 생성(Generate).
5. **API Serving (서비스 서빙):** `FastAPI`를 활용하여 사용자 질문을 받고 AI의 답변을 반환하는 초고속 RESTful API 엔드포인트 구축.
6. **Containerization (배포 환경):** `Docker`를 활용해 애플리케이션과 벡터 DB, Redis 등을 독립적인 컨테이너 환경으로 패키징하여 배포 안정성 확보.

## 개발 로그 (Development Log)
* **Phase 1 (기반 세팅):** 프로젝트 초기화 및 RAG 아키텍처 구축을 위한 핵심 도구(`LangChain`, `ChromaDB`, `FastAPI` 등) 환경 세팅 완료. (Day 1)
* **Phase 2 (데이터 전처리):** `PyPDFLoader` 및 최신 버전의 `RecursiveCharacterTextSplitter`를 활용하여 방대한 PDF 문서를 AI가 소화할 수 있는 크기로 분할(Chunking)하는 파이프라인 구축. (Day 2)
* **Phase 3 (임베딩 및 벡터 DB 구축):** 한국어 특화 오픈소스 모델(`jhgan/ko-sroberta-multitask`)을 활용하여 조각난 텍스트를 고차원 벡터로 임베딩하고, 이를 초고속 유사도 검색이 가능한 `ChromaDB`에 영구 적재(Persist). (Day 3)
* **Phase 4 (RAG 체인 및 LLM 연동):** 외부 API 버전 충돌 및 과금 문제를 해결하기 위해, 100% 무료이면서도 뛰어난 한국어 성능을 자랑하는 **Google Gemini 2.5 Flash** 모델을 도입하여 완벽한 지능형 질의응답 파이프라인 구축 완료. (Day 4)
* **Phase 5 (API 서버 구축):** `FastAPI`와 `Pydantic`을 활용하여 RAG 파이프라인을 RESTful API 엔드포인트(`/ask`)로 래핑하고, Uvicorn을 통해 서비스 서빙 환경 구축 완료. (Day 5)
* **Phase 6 (컨테이너화):** `Dockerfile`을 작성하여 RAG API 서버와 벡터 데이터베이스를 독립적인 환경에서 구동할 수 있도록 Docker 기반 배포 환경 구축 완료. (Day 6)
* **Phase 7 (비동기 분산 처리):** 대용량 문서 처리 시 발생하는 병목 현상을 방지하기 위해 `Redis`와 `Celery`를 도입하여 백그라운드 워커(Worker) 기반의 비동기 처리 아키텍처 구축. (Day 7)

## 기술 스택 (Tech Stack)
| Category | Technology | Usage |
| :--- | :--- | :--- |
| **Backend & Infra** | **FastAPI, Docker** | 비동기 기반 초고속 AI 질의응답 API 서버 구축 및 배포 |
| **Task Queue** | **Celery, Redis** | 대용량 문서 처리 작업을 위한 메시지 브로커 및 백그라운드 워커 |
| **AI & LLM** | **LangChain, Google Gemini** | LLM 파이프라인(RAG) 구성 및 생성형 AI 모델 적용 |
| **Database** | **ChromaDB** | 임베딩된 텍스트 벡터를 저장하고 유사도 검색을 수행하는 Vector DB |
| **Data Processing** | **PyPDF, HuggingFace** | PDF 문서 데이터 추출, 전처리 및 로컬 텍스트 임베딩 |

## 실행 방법 (How to Run)

### 1. 환경 변수 세팅
최상단 경로에 `.env` 파일을 만들고 아래 키를 입력하세요.
```env
GEMINI_API_KEY=AIzaSy...

```

### 2. 로컬 환경에서 실행

```bash
# 필수 패키지 설치
pip install -r requirements.txt

# Step 1: Redis 서버 실행 (Docker 활용)
docker run -d -p 6379:6379 --name documind-redis redis:alpine

# Step 2: Celery 워커 실행 (새 터미널 창)
celery -A src.worker.celery_app worker --loglevel=info

# Step 3: FastAPI 서버 실행 (새 터미널 창)
uvicorn src.main:app --reload

```


