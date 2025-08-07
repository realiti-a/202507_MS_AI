# utils.py

import json
from pathlib import Path
from dotenv import load_dotenv
import os  
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import base64

load_dotenv()
OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

def classify_input(input_text: str) -> str:
    """입력 문장이 장소 기반인지 조건 기반인지 분류"""
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {
                "role": "system",
                "content": "다음 입력이 '관광지 이름'인지 '여행 조건 설명'인지 판단해줘. 결과는 '장소' 또는 '조건' 중 하나만 반환해."
            },
            {"role": "user", "content": input_text}
        ]
    )
    return response.choices[0].message.content.strip()

def embed_text(text):
    """GPT 임베딩 벡터 생성"""
    response = client.embeddings.create(
        input=[text],
        model=EMBEDDING_DEPLOYMENT_NAME
    )
    return response.data[0].embedding

def append_json_file(filepath, new_data):
    """tour_data.json에 새 장소 추가"""
    if not Path(filepath).exists():
        with open(filepath, "w") as f:
            json.dump([new_data], f, indent=2, ensure_ascii=False)
    else:
        with open(filepath, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data.append(new_data)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)

def upload_document_to_search(doc):
    """Azure AI Search 인덱스에 문서 추가"""
    search_client.upload_documents(documents=[doc])

def chat_with_rag(user_input, context):
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "너는 친절한 여행 가이드야. 아래 정보를 참고해서 대답해." + context},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

def make_safe_id(text: str) -> str:
    encoded = base64.urlsafe_b64encode(text.encode()).decode()
    return encoded.rstrip("=")  # padding 제거


def search_rag(user_input):
    embedded = embed_text(user_input)
    results = search_client.search(
        search_text="",
        vector_queries=[
            {
                "vector": embedded,
                "fields": "contentVector",
                "k": 3,
                "kind": "vector"  # ← 반드시 추가!
            }
        ]
    )
    contents = []
    for doc in results:
        if doc.get('@search.score', 0) >= 0.9 and "description" in doc:
            contents.append(doc["description"])
    return "\n".join(contents)

def extract_place_name(user_input: str) -> str:
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "다음 사용자의 문장에서 '장소명'만 정확하게 추출해줘. 예: '서울대학교', '부산 해운대', '경복궁'. 장소 외의 단어는 제거해."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

def chat_with_gpt(user_input):
    response = client.chat.completions.create(
        model=OPENAI_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "너는 친절한 여행사 직원이야. 사용자의 질문에 대해 여행 정보를 제공해줘. 예산과 준비물도 함께 정리해줘."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content