import React, { useState, useEffect } from "react";
import Loader from "./Loader";
import '../styles/chatBot.css';

const ChatBot = (props) => {
    const { chatPrompt, flightData } = props;  // flightData를 받아옴
    const [loading, setLoading] = useState(false);
    const [replies, setReplies] = useState([]);
    const [userMessage, setUserMessage] = useState('');

    useEffect(() => {
        console.log("chatPrompt:", chatPrompt); // 현재 chatPrompt 출력
        console.log("flightData:", flightData); // flightData가 제대로 넘어오는지 확인
    
        if (chatPrompt) {
            setReplies(prevReplies => [...prevReplies, chatPrompt]);
        }
    }, [chatPrompt, flightData]);
    

    const handleSubmit = async () => {
        if (!userMessage.trim()) return;

        setLoading(true);
        setReplies([...replies, userMessage]);
        setUserMessage('');

        try {
            const response = await fetch("http://127.0.0.1:8000/chat", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    flightData: flightData  // 사용자 메시지와 함께 flightData도 보냄
                }),
            });
            const result = await response.json();
            setReplies(prevReplies => [...prevReplies, result.response]);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {loading && <Loader />}
            <div className="card">
                <div className="chat-header">ChatBot</div>
                <div className="chat-window">
                    <ul className="message-list">
                        {replies.map((reply, index) => (
                            <li key={index} className="message">
                                <div className="message-body">
                                    <pre>{reply}</pre>
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="chat-input">
                    <input
                        type="text"
                        className="message-input"
                        placeholder="메시지"
                        value={userMessage}
                        onChange={(e) => setUserMessage(e.target.value)}
                    />
                    <button className="ui-btn" onClick={handleSubmit}>
                        <span>입력</span>
                    </button>
                </div>
            </div>
        </>
    );
};

export default ChatBot;
