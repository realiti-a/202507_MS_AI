# ✈️ TravelGenie: AI 기반 맞춤형 여행 가이드 & 일정 추천 에이전트

[TravelGenie](https://reality0130-webapp-001-f5f6c5f6d6f2dhc3.eastus2-01.azurewebsites.net/)

## 📌 프로젝트 개요

**TravelGenie**는 사용자의 입력에 따라 적절한 여행 정보를 제공하는 **AI 기반 여행 가이드 에이전트**입니다.  
입력 방식에 따라 다음 두 가지 흐름을 자동 판단하여 최적의 정보를 제공합니다:

1. **관광지 기반 흐름**: 관광지 이름, 좌표, 사진 등 입력 시 → 요약 / 상세정보 / 주변명소 / 루트 추천 제공
2. **목적 기반 흐름**: 여행 목적, 예산, 인원, 계절 등을 입력 시 → 여행 추천지 / 일정 / 최적기 / 상세 계획 제공


## 💡 주요 기능

| 기능명 | 설명 |
|--------|------|
| 관광지 정보 요약 | GPT 기반 요약 (2~3문단) 제공 |
| 상세 가이드 | 운영시간, 주요 포인트, 포토존 등 가이드 |
| 주변 장소 추천 | Azure AI Search + 관광지 DB 기반 RAG |
| 관광 루트 추천 | GPT 기반 최적 경로(이동시간 포함) |
| 조건 기반 여행지 추천 | 입력 조건(예: 자연, 2박3일, 혼자 등)에 따라 여행지 선정 |
| 여행 일정 자동 생성 | Day1 ~ DayN 일정 구성 |
| 최적 여행 시기 안내 | GPT 및 날씨 데이터 기반 추천 |

---

## 🎯 주요 기능

### 1. AI Agent 자동 라우팅
- 사용자 입력을 자동으로 분석하여 "장소 정보" vs "여행 계획" 분류
- LangGraph를 활용한 ReAct Agent 패턴 구현

### 2. RAG 기반 관광지 정보 제공
- Azure AI Search를 활용한 시맨틱 검색
- Kakao Map API를 통한 실시간 데이터 수집
- 벡터 임베딩 기반 정확한 정보 검색

### 3. 맞춤형 여행 계획 생성
- Azure OpenAI GPT를 활용한 여행 일정 및 예산 추천
- 개인화된 여행 팁 및 준비물 가이드
- 동적 콘텐츠 파싱 및 구조화

## 🧠 기술 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   AI Agent       │    │  Azure OpenAI   │
│   Web UI        │────│   Router         │────│  GPT-4 Model    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        ▼                        │
         │              ┌──────────────────┐               │
         │              │  LangGraph       │               │
         │              │  ReAct Agent     │               │
         │              └──────────────────┘               │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Azure Web     │    │  Azure AI Search │    │  Kakao Map API  │
│   App Service   │    │  Vector Index    │    │  Real-time Data │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔧 기술 스택

### Microsoft Azure 서비스
- **Azure OpenAI Service**: GPT-4.1 Mini 모델, text-embedding-ada-002
- **Azure AI Search**: 시맨틱 검색 및 벡터 인덱싱
- **Azure Web App Service**: Streamlit 애플리케이션 배포

### 개발 프레임워크
- **Python 3.9+**: 서버 로직 및 Azure SDK
- **Streamlit**: 웹 인터페이스
- **LangChain/LangGraph**: AI Agent 워크플로우
- **Kakao Map API**: 실시간 관광지 데이터

### 주요 라이브러리
```
streamlit
openai
azure-search-documents
langchain-openai
langgraph
python-dotenv
requests
```

## 📁 프로젝트 구조

```
TravelGenie/
├── streamlit_app.py          # 메인 웹 애플리케이션
├── agent_router.py           # LangGraph 기반 AI Agent 라우터
├── tools.py                  # Agent 도구 정의
├── utils.py                  # 유틸리티 함수 (RAG, 검색 등)
├── kakaoAPI.py              # Kakao Map API 연동
├── streamlit.sh             # 배포 스크립트
├── .env.sample              # 환경 변수 템플릿
├── requirements.txt         # 의존성 패키지
└── README.md               # 프로젝트 문서
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone [repository-url]
cd TravelGenie

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# Azure OpenAI 설정
AZURE_OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=dev-gpt-4.1-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-10-21

# Azure AI Search 설정
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_INDEX_NAME=tour-guide-index
AZURE_SEARCH_API_KEY=your_search_api_key

# Kakao API 설정
KAKAO_API_KEY=your_kakao_api_key
```

### 3. 애플리케이션 실행

```bash
# 로컬 실행
streamlit run streamlit_app.py

# 또는 배포 스크립트 실행
bash streamlit.sh
```

## 💡 사용 방법

### 1. 관광지 정보 조회
```
입력: "경복궁 정보 알려줘"
결과: RAG 기반 상세 관광지 정보, 운영시간, 위치 등
```

### 2. 여행 계획 생성
```
입력: "3일 서울 여행 계획"
결과: 맞춤형 일정, 예산, 준비물, 여행 팁
```

### 3. 복합 질의
```
입력: "부산 맛집 추천"
결과: AI Agent가 자동 판단하여 적절한 도구 선택
```

## 🔍 핵심 기술 구현

### 1. AI Agent 라우팅 시스템
```python
# agent_router.py
def run_agent_node(state: AgentState):
    """LangGraph 기반 ReAct Agent 실행"""
    user_input = state.input 
    agent_input = {"messages": [{"role": "user", "content": user_input}]}
    output = agent.invoke(agent_input)
    return {"output": response}
```

### 2. RAG 파이프라인
```python
# utils.py
def search_rag(user_input):
    """벡터 기반 시맨틱 검색"""
    embedded = embed_text(user_input)
    results = search_client.search(
        search_text="",
        vector_queries=[{
            "vector": embedded,
            "fields": "contentVector",
            "k": 3,
            "kind": "vector"
        }]
    )
```

### 3. 실시간 데이터 수집
```python
# kakaoAPI.py
def search_place(query):
    """Kakao Map API를 통한 관광지 정보 수집"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {API_KEY}"}
    # ... API 호출 및 데이터 처리
```

## 🎨 UI/UX 특징

- **반응형 디자인**: 모바일/데스크톱 최적화
- **탭 기반 정보 구성**: 요약, 상세 가이드, 일정/주변정보
- **실시간 AI 파싱**: 응답을 구조화하여 사용자 친화적 표시
- **동적 콘텐츠**: 예산 정보, 여행 팁, 키워드 자동 생성

## 📊 성능 및 확장성

### 벡터 검색 최적화
- Azure AI Search의 시맨틱 검색 활용
- 임베딩 캐싱으로 응답 속도 개선
- 유사도 임계값 (0.9) 기반 정확도 향상

### 확장 계획
- 다국어 지원 (GPT 기반 번역)
- 실시간 날씨/교통 정보 통합
- 사용자 선호도 학습 및 개인화

## 🚀 Azure 배포

### Web App Service 배포
```bash
# Azure CLI 로그인
az login

# 리소스 그룹 생성
az group create --name rg-travelgenie --location koreacentral

# Web App 생성 및 배포
az webapp create --resource-group rg-travelgenie --plan asp-travelgenie --name travelgenie-app
```

### 환경 변수 설정
Azure Portal > App Service > Configuration에서 환경 변수 설정
