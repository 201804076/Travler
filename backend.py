# backend.py
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

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Amadeus 및 OpenAI API 키 설정
amadeus = Client(
    client_id="fe3si2AT8QusGNTAxDgxA7WXerqJc5b5",
    client_secret="0RVDy7zAUaqrCl55"
)

client = OpenAI(api_key="sk-cAhJUzH84yjULvNihOe0meYXsRKzM08qhApWayPY24T3BlbkFJKI6DVVqvbtyVI59_Dwcdwr-K08WD8JgTYfWHeZRX0A")

# 항공편 검색 요청 형식을 정의하는 Pydantic 모델
class FlightSearchRequest(BaseModel):
    originLocationCode: str
    destinationLocationCode: str
    departureDate: str
    returnDate: str = None
    adults: int = 1

class ChatRequest(BaseModel):
    message: str

messages = [
    {"role": "system", "content": "You are a helpful Travel Guide, and only use Korean."}
]

@app.post("/flights")
async def search_flights(request: FlightSearchRequest):
    try:
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
    flight_data = request.flightData if "flightData" in request else None
    logger.info(f"User message: {user_message}")  # 추가된 로그
    logger.info(f"Flight data received: {flight_data}")  # 추가된 로그

    messages.append({"role": "user", "content": user_message})
    
    if flight_data:
        # flight_data를 활용해 추가 정보를 제공
        messages.append({"role": "system", "content": f"현재 항공편 정보: {len(flight_data)}개의 항공편이 있습니다."})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        return {"response": assistant_message}
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
