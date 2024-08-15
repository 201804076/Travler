import React, { useState, useEffect } from "react";
import Loader from "./Loader";
import '../styles/chatBot.css';

const ChatBot = (props) => {
    const { chatPrompt } = props;
    const [loading, setLoading] = useState(false);
    const [replies, setReplies] = useState([chatPrompt]);
    const [userMessage, setUserMessage] = useState('');  // 입력한 메시지를 별도로 관리

    useEffect(() => {
        if (chatPrompt) {
            setReplies(prevReplies => [...prevReplies, chatPrompt]);
        }
    }, [chatPrompt]);

    const handleSubmit = async () => {  // handleSubmit 함수를 ChatBot 컴포넌트 내부로 이동
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
                body: JSON.stringify({ message: userMessage }),
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
                        onChange={(e) => setUserMessage(e.target.value)}  // 입력된 메시지를 상태에 저장
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
