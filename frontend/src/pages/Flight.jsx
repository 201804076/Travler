import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import Navbar from "../components/Navbar";
import ChatBot from "../components/ChatBot";

const Flight = () => {
    const location = useLocation();
    const { originLocationCode, destinationLocationCode, departureDate, returnDate, adults } = location.state;

    const [flights, setFlights] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [messages, setMessages] = useState([]);

    // 날짜를 "YYYY-MM-DD" 형식으로 변환하는 함수
    function formatDate(date) {
        if (!date) return null;
        const d = new Date(date);
        let month = '' + (d.getMonth() + 1);
        let day = '' + d.getDate();
        const year = d.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [year, month, day].join('-');
    }

    useEffect(() => {
        const fetchFlights = async () => {
            // departureDate가 없는 경우 오류 처리
            if (!departureDate) {
                setError("출발 날짜는 필수입니다.");
                setLoading(false);
                return;
            }
    
            setLoading(true);
            try {
                const body = {
                    originLocationCode,
                    destinationLocationCode,
                    departureDate: formatDate(departureDate),
                    returnDate: returnDate ? formatDate(returnDate) : null,
                    adults,
                };
    
                console.log("Request Body:", body); // 디버깅을 위해 로그 출력
                const response = await fetch("http://localhost:8000/flights", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(body),
                });
    
                const data = await response.json();
                if (response.ok) {
                    if (data.flight_data.length === 0) {
                        setError("해당 조건에 맞는 항공편을 찾을 수 없습니다.");
                    } else {
                        setFlights(data.flight_data.slice(0, 10) || []);
                        setMessages(prevMessages => [...prevMessages, { role: "assistant", content: data.chatbot_message }]);
                    }
                } else {
                    setError(data.detail || "항공편을 불러오는 중 오류가 발생했습니다.");
                }
            } catch (err) {
                setError("항공편을 불러오는 중 오류가 발생했습니다.");
            } finally {
                setLoading(false);
            }
        };
    
        fetchFlights();
    }, [originLocationCode, destinationLocationCode, departureDate, returnDate, adults]);
    
    

    const renderFlightList = () => {
        return flights.map((flight, index) => (
            <div key={index} className="flight-item">
                <p>출발지: {flight.origin}</p>
                <p>도착지: {flight.destination}</p>
                <p>출발 시간: {flight.departureTime}</p>
                <p>도착 시간: {flight.arrivalTime}</p>
                <p>가격: {flight.price_krw} KRW</p>
            </div>
        ));
    };

    const renderChatBot = () => {
        if (loading) {
            return <ChatBot chatPrompt="항공편 정보를 불러오고 있습니다..." />;
        } else if (error) {
            return <ChatBot chatPrompt="항공편을 불러오는 중 오류가 발생했습니다." />;
        } else if (flights.length > 0) {
            return (
                <>
                    <ChatBot chatPrompt={`현재 ${flights.length}개의 항공편을 찾았습니다.`} />
                    <div className="flight-list">
                        {renderFlightList()}
                    </div>
                </>
            );
        } else {
            return <ChatBot chatPrompt="항공편을 찾을 수 없습니다." />;
        }
    };

    return (
        <>
            <Navbar />
            {renderChatBot()}
        </>
    );
}

export default Flight;
