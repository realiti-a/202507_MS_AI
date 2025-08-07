# agents/tools.py
from langchain.agents import Tool
from utils import search_rag, chat_with_rag, chat_with_gpt, extract_place_name, embed_text, upload_document_to_search, make_safe_id
from kakaoAPI import search_place, save_to_json

def search_tour_guide(input_text: str) -> str:
    place_name = extract_place_name(input_text)
    context = search_rag(place_name)

    if not context.strip():
        result = search_place(place_name)    
        if result:
            save_to_json(result)
            embed = embed_text(result["name"])
            result["id"] = make_safe_id(result["name"])
            result["contentVector"] = embed
            upload_document_to_search(result)
            return f"새로운 장소 정보를 추가했어요! 다시 실행해보세요."
        else:
            return f"'{place_name}'에 대한 정보를 찾을 수 없습니다."
    return chat_with_rag(input_text, context)

def recommend_trip_plan(input_text: str) -> str:
    return chat_with_gpt(input_text)

tools = [
    Tool(
        name="SearchTourGuide",
        func=search_tour_guide,
        description="특정 관광지에 대한 정보를 제공해주는 도구입니다."
    ),
    Tool(
        name="RecommendTripPlan",
        func=recommend_trip_plan,
        description="조건 기반으로 여행지를 추천하고 일정을 안내해주는 도구입니다."
    )
]