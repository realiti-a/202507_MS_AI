import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from utils import embed_text, upload_document_to_search, classify_input, chat_with_rag, make_safe_id, extract_place_name, search_rag, chat_with_gpt
from kakaoAPI import search_place, save_to_json
from agent_router import run_agent

load_dotenv()
# 페이지 설정
st.set_page_config(
    page_title="TravelGenie Agent", 
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 커스텀 CSS 스타일
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🧭 TravelGenie</h1>
    <p>AI Agent 기반 스마트 여행 가이드</p>
</div>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("🎯 사용 가이드")
    st.markdown("""
    **입력 예시:**
    - 🏰 장소: "경복궁 정보 알려줘"
    - 🗺️ 조건: "3일 서울 여행 계획"
    - 🍜 맛집: "부산 맛집 추천"
    - 🏨 숙박: "제주도 호텔 정보"
    """)
    
    st.header("⚡ 기능")
    st.markdown("""
    - AI Agent 자동 분석
    - 실시간 정보 검색
    - 맞춤형 여행 계획
    - 상세 가이드 제공
    """)

# 메인 입력 영역
col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.text_input(
        "✈️ 여행지나 조건을 입력해 주세요:",
        placeholder="예: 경복궁 관광 정보, 3일 부산 여행 계획, 제주도 맛집 추천"
    )

with col2:
    generate_btn = st.button("🚀 여행 정보 생성", type="primary", use_container_width=True)

def parse_agent_response(response: str):
    """AI를 활용한 스마트 파싱으로 Agent 응답을 구조화"""
    from utils import client
    import os
    
    # AI 파싱 프롬프트
    parsing_prompt = f"""
다음 여행 정보를 3개 섹션으로 나누어 JSON 형식으로 정리해줘:

1. summary: 핵심 요약 (2-3문장으로 간단하게)
2. detailed_guide: 상세한 여행 가이드 (구체적인 정보, 팁, 추천사항)  
3. additional_info: 일정, 주변정보, 예산, 교통 등 부가정보

응답 형식:
{{
  "summary": "요약 내용...",
  "detailed_guide": "상세 가이드 내용...",
  "additional_info": "추가 정보 내용..."
}}

원본 텍스트:
{response}
"""

    try:
        # AI로 파싱 수행
        parsing_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "당신은 여행 정보를 체계적으로 정리하는 전문가입니다. JSON 형식으로만 응답하세요."},
                {"role": "user", "content": parsing_prompt}
            ],
            temperature=0.3
        )
        
        parsed_text = parsing_response.choices[0].message.content.strip()
        
        # JSON 파싱 시도
        import json
        import re
        
        # JSON 부분만 추출 (```json 태그 제거)
        json_match = re.search(r'```json\s*(.*?)\s*```', parsed_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # {} 로 둘러싸인 부분 찾기
            json_match = re.search(r'\{.*\}', parsed_text, re.DOTALL)
            json_str = json_match.group(0) if json_match else parsed_text
        
        parsed_data = json.loads(json_str)
        
        # 검증 및 기본값 설정
        result = {
            "summary": parsed_data.get("summary", "").strip(),
            "detailed_guide": parsed_data.get("detailed_guide", "").strip(), 
            "additional_info": parsed_data.get("additional_info", "").strip()
        }
        
        # 비어있는 섹션 처리
        if not result["summary"]:
            result["summary"] = response[:200] + "..." if len(response) > 200 else response
            
        if not result["detailed_guide"]:
            result["detailed_guide"] = response
            
        return result
        
    except Exception as e:
        print(f"AI 파싱 실패, 기본 파싱 사용: {e}")
        # AI 파싱 실패시 기본 파싱으로 폴백
        return {
            "summary": response[:300] + "..." if len(response) > 300 else response,
            "detailed_guide": response,
            "additional_info": "추가 정보를 준비 중입니다."
        }
    
# def parse_agent_response(response: str):
#     """Agent 응답을 파싱해서 구조화된 정보로 변환"""
#     # 기본 구조
#     parsed = {
#         "summary": "",
#         "detailed_guide": "",
#         "additional_info": ""
#     }
    
#     # 간단한 파싱 로직 (실제로는 더 정교하게 만들 수 있음)
#     lines = response.split('\n')
#     current_section = "summary"
    
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
            
#         # 섹션 구분자 감지
#         if any(keyword in line.lower() for keyword in ['상세', 'detail', '가이드', 'guide']):
#             current_section = "detailed_guide"
#         elif any(keyword in line.lower() for keyword in ['추가', '주변', '일정', 'schedule', 'nearby']):
#             current_section = "additional_info"
        
#         parsed[current_section] += line + "\n"
    
#     # 요약이 비어있으면 전체 응답의 첫 부분을 요약으로
#     if not parsed["summary"].strip():
#         parsed["summary"] = response[:200] + "..." if len(response) > 200 else response
    
#     return parsed

def create_detailed_guide(detailed_text, user_input):
    """상세 가이드 탭 내용 생성 - AI로 여행팁과 체크리스트 동적 생성"""
    st.markdown("### 📖 상세 여행 가이드")
    
    if detailed_text.strip():
        st.markdown(detailed_text)
    else:
        st.markdown("상세한 여행 정보를 제공합니다.")
        st.markdown(detailed_text or "추가 정보가 준비 중입니다.")
    
    # AI로 맞춤형 여행팁 생성
    st.markdown("---")
    st.markdown("### 💡 맞춤 여행 팁")
    
    try:
        from utils import client
        import os
        
        # 여행팁 생성 프롬프트
        tips_prompt = f"""
다음 여행 정보를 바탕으로 실용적인 여행 팁을 생성해주세요:

사용자 요청: {user_input}
상세 정보: {detailed_text}

다음 형식으로 응답해주세요:
PREPARATION: 준비사항 3-4개 (체크리스트 형태)
USEFUL_INFO: 유용한 정보 3-4개 (팁 형태)

예시 형식:
PREPARATION:
- 여권 유효기간 6개월 이상 확인
- 현지 날씨에 맞는 의복 준비
- 필수 약품 및 상비약 챙기기

USEFUL_INFO:
- 현지 교통카드 미리 구매하기
- 구글 번역기 앱 다운로드
- 현지 화폐 소액 준비
"""

        tips_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "여행 전문가로서 실용적이고 구체적인 팁을 제공하세요."},
                {"role": "user", "content": tips_prompt}
            ],
            temperature=0.4
        )
        
        tips_content = tips_response.choices[0].message.content.strip()
        
        # 응답 파싱
        preparation_section = ""
        useful_info_section = ""
        
        if "PREPARATION:" in tips_content:
            sections = tips_content.split("USEFUL_INFO:")
            preparation_section = sections[0].replace("PREPARATION:", "").strip()
            if len(sections) > 1:
                useful_info_section = sections[1].strip()
        
        # 준비사항 표시
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🎒 준비사항 체크리스트:**")
            if preparation_section:
                st.markdown(preparation_section)
            else:
                st.markdown("- 여행 일정 재확인\n- 필수 서류 준비\n- 짐 패킹 체크")
        
        with col2:
            st.markdown("**💎 유용한 정보:**")
            if useful_info_section:
                st.markdown(useful_info_section)
            else:
                st.markdown("- 현지 정보 미리 조사\n- 비상연락처 준비\n- 여행보험 가입")
                
    except Exception as e:
        # 기본 팁 표시
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **🎒 준비사항 체크리스트:**
            - 여권/신분증 확인
            - 숙박 예약 확인
            - 교통편 예약
            - 여행 보험 가입
            """)
        
        with col2:
            st.markdown("""
            **💎 유용한 정보:**
            - 📱 현지 앱 다운로드
            - 💳 결제수단 준비
            - 🗺️ 오프라인 지도 다운
            - 📞 비상연락처 메모
            """)

def create_schedule_info(additional_text, user_input):
    """일정/주변 정보 탭 내용 생성"""
    st.markdown("### 🗓️ 추천 일정 & 주변 정보")
    
    if additional_text.strip():
        st.markdown(additional_text)
    
    # AI로 예산 정보 추출 및 생성
    try:
        from utils import client
        import os
        
        budget_prompt = f"""
다음 여행 정보를 바탕으로 예상 예산을 분석해주세요:
- 숙박비 (1박 기준)
- 식비 (1일 기준) 
- 교통비 (�왕복 기준)

숫자만 원화 단위로 응답하세요. 형식: 숙박비,식비,교통비
예: 120000,60000,40000

원본 정보: {additional_text}
사용자 입력: {user_input}
"""

        budget_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "여행 예산을 분석하는 전문가입니다. 숫자만 간단히 응답하세요."},
                {"role": "user", "content": budget_prompt}
            ],
            temperature=0.3
        )
        
        budget_str = budget_response.choices[0].message.content.strip()
        budget_parts = budget_str.split(',')
        
        if len(budget_parts) >= 3:
            accommodation = f"{int(budget_parts[0]):,}원"
            food = f"{int(budget_parts[1]):,}원" 
            transport = f"{int(budget_parts[2]):,}원"
        else:
            raise Exception("예산 파싱 실패")
            
    except Exception as e:
        # 기본값 사용
        accommodation = "150,000원"
        food = "80,000원"
        transport = "50,000원"
    
    # 예산 정보 표시
    st.markdown("---")
    st.markdown("### 💰 예상 예산")
    
    budget_col1, budget_col2, budget_col3 = st.columns(3)
    with budget_col1:
        st.metric("숙박비", accommodation, "1박 기준")
    with budget_col2:
        st.metric("식비", food, "1일 기준")
    with budget_col3:
        st.metric("교통비", transport, "왕복 기준")

def create_summary_content(summary_text):
    """요약 탭 내용 생성"""
    st.markdown("### 📋 여행 정보 요약")
    
    # 요약 정보를 박스로 표시
    st.markdown(f"""
    <div class="info-box">
        {summary_text}
    </div>
    """, unsafe_allow_html=True)
    
    # AI로 키워드 추출
    try:
        from utils import client
        import os
        
        keyword_prompt = f"""
다음 여행 정보에서 핵심 키워드 5개를 추출해주세요. 
키워드는 쉼표로 구분해서 나열하세요. (예: 관광지, 맛집, 호텔, 교통, 예산)

텍스트: {summary_text}
"""
        
        keyword_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {"role": "system", "content": "여행 정보에서 핵심 키워드만 간단히 추출하세요."},
                {"role": "user", "content": keyword_prompt}
            ],
            temperature=0.3
        )
        
        keywords_str = keyword_response.choices[0].message.content.strip()
        keywords = [kw.strip() for kw in keywords_str.split(',') if kw.strip()]
        
        if keywords:
            st.markdown("### 🏷️ 핵심 키워드")
            cols = st.columns(min(len(keywords), 5))
            for i, keyword in enumerate(keywords[:5]):
                with cols[i]:
                    st.button(f"#{keyword}", disabled=True)
    except Exception as e:
        # 키워드 추출 실패시 기본 키워드 사용
        default_keywords = ["여행", "관광", "정보"]
        st.markdown("### 🏷️ 관련 키워드") 
        cols = st.columns(len(default_keywords))
        for i, keyword in enumerate(default_keywords):
            with cols[i]:
                st.button(f"#{keyword}", disabled=True)



# if st.button("여행 정보 생성"):
#     if user_input:
#         with st.spinner("AI Agent가 정보를 분석 중입니다..."):
#             try:
#                 result = run_agent(user_input)
#                 st.success("✅ 생성 완료")
#                 st.markdown(result)
#             except Exception as e:
#                 st.error(f"❌ 에러 발생: {e}")
#     else:
#         st.warning("입력값을 먼저 작성해주세요.")

if generate_btn:
    if user_input:
        with st.spinner("🤖 AI Agent가 정보를 분석 중입니다..."):
            try:
                # Agent 실행
                result = run_agent(user_input)
                
                # 성공 메시지
                st.markdown("""
                <div class="success-box">
                    <strong>✅ 분석 완료!</strong> AI Agent가 맞춤형 여행 정보를 생성했습니다.
                </div>
                """, unsafe_allow_html=True)
                
                # 응답 파싱
                parsed_result = parse_agent_response(result)
                
                # print("=" * 50)
                # print(parsed_result)  # 디버깅용
                # print("=" * 50)
                
                # 탭 생성
                tab1, tab2, tab3 = st.tabs(["📋 요약", "📖 상세 가이드", "🗓️ 일정 & 주변정보"])
                
                with tab1:
                    create_summary_content(parsed_result["summary"])
                
                with tab2:
                    create_detailed_guide(parsed_result["detailed_guide"], user_input)
                
                with tab3:
                    create_schedule_info(parsed_result["additional_info"], user_input)
                
                # 원본 응답 (디버깅용, 접을 수 있게)
                with st.expander("🔧 원본 Agent 응답 (디버깅용)"):
                    st.text(result)
                
            except Exception as e:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>❌ 에러 발생:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)
                
                # 에러 해결 팁
                st.markdown("### 🔧 문제 해결 방법")
                st.markdown("""
                1. 입력을 더 구체적으로 작성해보세요
                2. 네트워크 연결을 확인해보세요
                3. 잠시 후 다시 시도해보세요
                """)
    else:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ 알림:</strong> 여행지나 조건을 먼저 입력해주세요.
        </div>
        """, unsafe_allow_html=True)

# 푸터
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🧭 TravelGenie - Powered by AI Agent Technology</p>
        <p>더 나은 여행을 위한 스마트한 선택</p>
    </div>
    """, unsafe_allow_html=True)

# st.set_page_config(page_title="TravelGenie", page_icon="🌍")
# st.title("🌍 TravelGenie - AI 여행 가이드")

# user_input = st.text_input("여행지나 여행 조건을 입력해 주세요:")

# if st.button("여행 정보 생성"):
#     if user_input:
#         with st.spinner("AI가 여행 정보를 생성 중입니다..."):
#             input_type = classify_input(user_input)
#             if input_type == "장소":
#                 place = extract_place_name(user_input)
#                 context = search_rag(place)
#                 if not context.strip():
#                     # 없는 경우 JSON, AI Search에 추가
#                     st.info(f"'{place}'에 대한 정보가 없습니다. 새로운 장소 정보를 추가합니다.")
#                     result = search_place(place)    
#                     if result:
#                         save_to_json(result)
#                         embed = embed_text(result["name"])
#                         result["id"] = make_safe_id(result["name"])
#                         result["contentVector"] = embed
#                         upload_document_to_search(result)
#                         st.info("새로운 장소 정보를 추가했어요! 다시 실행해보세요.")
#                     else:
#                         st.info(f"'{place}'에 대한 정보를 찾을 수 없습니다.")   
#                 else:
#                     result = chat_with_rag(user_input, context)
#                     # st.info(context.strip())
#                     st.success("✅ 생성 완료")
#                     st.markdown(result)
#             elif input_type == "조건":
#                 # 조건 기반 GPT 호출
#                 result = chat_with_gpt(user_input)
#                 st.success("✅ 조건 기반 추천 완료")
#                 st.markdown(result)
#             else:
#                 st.warning("입력 유형을 분류하지 못했어요.")
            
#     else:
#         st.warning("입력값을 먼저 작성해주세요.")