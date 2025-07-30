# ✈️ TravelGenie: AI 기반 맞춤형 여행 가이드 & 일정 추천 에이전트

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

## 🧠 기술 아키텍처

```mermaid
graph TD;
    User -->|입력| Streamlit_UI
    Streamlit_UI --> Azure_Functions
    Azure_Functions -->|LangChain Agent| GPT_Model
    Azure_Functions --> Azure_AI_Search
    Azure_Functions --> Cosmos_DB
    GPT_Model --> Output
    Azure_AI_Search --> Output
    Cosmos_DB --> Output
    Output --> Streamlit_UI
