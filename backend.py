from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from amadeus import Client, ResponseError
from openai import OpenAI
import requests
import re
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Amadeus 및 OpenAI API 키 설정
amadeus_client_id = "fe3si2AT8QusGNTAxDgxA7WXerqJc5b5"
amadeus_client_secret = "0RVDy7zAUaqrCl55"
openai_api_key = "sk-cAhJUzH84yjULvNihOe0meYXsRKzM08qhApWayPY24T3BlbkFJKI6DVVqvbtyVI59_Dwcdwr-K08WD8JgTYfWHeZRX0A"

# Amadeus 클라이언트 초기화
amadeus = Client(
    client_id=amadeus_client_id,
    client_secret=amadeus_client_secret
)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=openai_api_key)

# 항공편 검색 요청 형식을 정의하는 Pydantic 모델
class FlightSearchRequest(BaseModel):
    originLocationCode: str
    destinationLocationCode: str
    departureDate: str
    returnDate: str = None
    adults: int = 1

# 챗봇 메시지 형식을 정의하는 Pydantic 모델
class ChatRequest(BaseModel):
    message: str

messages = [
    {"role": "system", "content": "You are a helpful Travel Guide, and only use Korean."}
]

# 환율 정보를 가져오는 함수
def get_exchange_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    response.raise_for_status()
    rates = response.json()["rates"]
    return rates["KRW"]

@app.post("/flights")
async def search_flights(request: FlightSearchRequest):
    try:
        # departureDate가 비어 있거나 올바르지 않은 경우 처리
        if not request.departureDate or not re.match(r'\d{4}-\d{2}-\d{2}', request.departureDate):
            logger.error(f"Invalid departureDate format: {request.departureDate}")
            raise HTTPException(status_code=400, detail="departureDate는 YYYY-MM-DD 형식의 필수 입력 값입니다.")

        logger.info(f"Received flight search request: {request.dict()}")

        search_params = {
            "originLocationCode": request.originLocationCode,
            "destinationLocationCode": request.destinationLocationCode,
            "departureDate": request.departureDate,
            "adults": request.adults,
        }

        if request.returnDate:
            search_params["returnDate"] = request.returnDate

        response = amadeus.shopping.flight_offers_search.get(**search_params)

        if not response.data:
            logger.info("No flights found for the given criteria.")
            return {"flight_data": [], "chatbot_message": "해당 조건에 맞는 항공편이 없습니다."}

        logger.info(f"Amadeus API response: {response.data}")
        return {"flight_data": response.data, "chatbot_message": f"{len(response.data)}개의 항공편을 찾았습니다."}

    except ResponseError as error:
        logger.error(f"Amadeus API Error: {error}\nError Message: {error.response.result}")
        raise HTTPException(status_code=500, detail="Amadeus API Error")
    except HTTPException as http_error:
        logger.error(f"Input validation error: {http_error.detail}")
        raise http_error
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected Server Error")


@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # 여기서 'message' 객체의 속성에 접근할 때 인덱싱을 피하고 속성으로 접근.
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        return {"response": assistant_message}
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
