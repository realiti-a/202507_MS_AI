import requests
import os
from dotenv import load_dotenv
import json

def search_place(query):
    load_dotenv()
    API_KEY = os.getenv("KAKAO_API_KEY")
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {API_KEY}"}  # Kakao API는 "KakaoAK {API_KEY}" 형식
    params = {
        "query": query,
        "category_group_code": "AT4",  # 관광명소(관광,문화시설)
        "size": 1
    }

    res = requests.get(url, headers=headers, params=params)  # set이 아니라 get 사용
    result = res.json()

    if result.get("documents"):
        place = result["documents"][0]
        return {
            "name": place["place_name"],
            "description": f"{place['place_name']}은 {place['address_name']}에 위치한 관광명소입니다.",
            "location": place["address_name"],
            # "lat": place["y"],
            # "lng": place["x"],
            # "category": place["category_name"],
            "url": place["place_url"]
        }
    else:
        print("API 응답:", result)  # 디버깅용 출력
        return None


def format_kakao_place(data):
    return {
        "name": data["name"],
        "description": data["description"],
        "hours": "",  # 카카오는 운영시간 제공 X, 추론 필요
        "location": data["location"],
        "highlights": [],  # 사진 등도 없음, 수동 추가 or GPT로 추론
        "nearby": [],      # 추후 확장 가능
        "url": data["url"]
    }

def save_to_json(place_data, filename="tour_data.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(format_kakao_place(place_data))

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 테스트
if __name__ == "__main__":
    place_names = [
        "경복궁",
        "남산타워",
        "명동",
        "홍대",
        "인사동",
        "부산 해운대",
        "제주도 한라산",
        "경주 불국사",
        "전주 한옥마을",
        "강릉 경포대",
        "여수 오동도",
        "속초 설악산",
        "광주 무등산",
        "울산 태화강",
        "대구 팔공산",
        "인천 송도",
        "수원 화성",
        "광화문광장",
        "부산 광안리",
        "서울숲",
        "창덕궁",
        "서울 올림픽공원",
        "서울 국립중앙박물관",
        "서울 롯데월드타워",
        "서울 동대문디자인플라자",
        "서울 북촌한옥마을",
        "서울 청계천",
        "서울 남산골한옥마을",
        "서울 성수동",
        "서울 용산전자상가",
        "서울 가로수길",
        "서울 이태원",
        "서울 홍대입구",
        "서울 압구정",
        "고려대학교 캠퍼스",
        "연세대학교 캠퍼스",
        "성균관대학교 캠퍼스",
    ]

    for place in place_names:
        result = search_place(place)    
        if result:
            save_to_json(result)
            print(f"관광지 정보 '{result['name']}'가 JSON 파일에 저장되었습니다.")
        else:
            print(f"'{place}'에 대한 정보를 찾을 수 없습니다.")
        print(result)