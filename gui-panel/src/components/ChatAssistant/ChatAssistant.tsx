import React, {useEffect, useRef, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {interactWithAgent} from '../../api/ApiService';
import ChatInput from './ChatInput';
import MessageBubble, {XAISources} from "./ChatComponents";
import XAIEX from "../../api/mockData/XAIEX";

export interface Message {
    id: number;
    sender: 'user' | 'assistant';
    content: string;
    extraData?: {
        explanation?: XAISources[];
        dashboardData?: { target: string; metadata: any };
        report?: { userId: string; reportId: string };
    };
}

export interface ChatAssistantProps {
    username: string;
    userId: string;
}

const ChatAssistant: React.FC<ChatAssistantProps> = ({username, userId}) => {
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([{
        id: 0,
        sender: 'assistant',
        content: `Hello ${username}! How can I help you today?`
    }]);
    const [newMessage, setNewMessage] = useState('');
    const navigate = useNavigate();
    const [isTyping, setIsTyping] = useState(false);
    const containerRef = useRef<HTMLDivElement | null>(null);

    const toggleChat = () => setIsChatOpen((prev) => !prev);

    const handleNavigation = (target: string, metadata: any) => {
        navigate(target, {state: {metadata}});
    };

    // Effect to scroll to the bottom when messages change
    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.scrollTop = containerRef.current.scrollHeight;
        }
    }, [messages]); // Runs every time `messages` changes

    const handleSendMessage = () => {
        if (!newMessage.trim()) return;

        const userMessage: Message = {
            id: messages.length + 1,
            sender: 'user',
            content: newMessage,
        };

        setMessages((prev) => [...prev, userMessage]);

        function handleCommand(userMessage: Message) {
            if (userMessage.content === '/clear') {
                setMessages([]);
            }
            if (userMessage.content === '/dashboard') {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: messages.length + 2,
                        sender: 'assistant',
                        content: 'This is an example dashboard.',
                        extraData: {
                            explanation: XAIEX,
                            dashboardData: {
                                target: '/dashboard/new',
                                metadata:
                                    JSON.parse("[\n  {\n    \"line\": \"power_consumption_efficiency\"\n  },\n  {\n    \"area\": \"power_consumption_efficiency\"\n  },\n  {\n    \"barv\": \"power_consumption_efficiency\"\n  },\n  {\n    \"barh\": \"power_consumption_efficiency\"\n  }\n]")
                                ,
                            },
                        }
                    },
                ]);
            }
            if (userMessage.content === '/report') {
                setMessages((prev) => [
                    ...prev,
                    {
                        id: messages.length + 2,
                        sender: 'assistant',
                        content: 'Your report is ready for review.',
                        extraData: {
                            explanation: XAIEX,
                            report: {
                                userId: userId,
                                reportId: 'report_123',
                            },
                        },
                    },
                ]);
            }
        }

        //if the message is a command, handle it
        if (newMessage.startsWith('/')) {
            handleCommand(userMessage);
        } else {

            // Simulate assistant response
            setIsTyping(true);
            interactWithAgent(userId, userMessage.content)
                .then((response) => {
                    let extraData = {};
                    console.log(response);
                    let explanation: XAISources[];

                    try {
                        //try decoding the explanation string
                        const decodedExplanation: Record<string, any>[] = JSON.parse(response.textExplanation);
                        explanation = decodedExplanation.map(XAISources.decode);
                    } catch (e) {
                        console.error("Error decoding explanation: ", e);
                        explanation = [];
                    }

                    if (response.label) {
                        switch (response.label) {
                            case 'dashboard':
                                extraData = {
                                    explanation: explanation,
                                    dashboardData: {
                                        target: '/dashboard/new',
                                        metadata: response.data,
                                    },
                                };
                                break;
                            case 'report':
                                extraData = {
                                    explanation: explanation,
                                    report: {
                                        userId: userId,
                                        reportId: response.data,
                                    },
                                };
                                response.textResponse = 'The report ' + response.textResponse + ' is ready for review.';
                                break;
                            default:
                                extraData = {
                                    explanation: explanation,
                                };
                        }

                    }

                    const assistantMessage: Message = {
                        id: messages.length + 2,
                        sender: 'assistant',
                        content: response.textResponse,
                        extraData: extraData,
                    };
                    setMessages((prev) => [...prev, assistantMessage]);
                })
                .catch(() => {
                    setMessages((prev) => [
                        ...prev,
                        {
                            id: messages.length + 2,
                            sender: 'assistant',
                            content: `Sorry, I couldn't process that.`,
                        },
                    ]);
                }).finally(() => {
                setIsTyping(false); // Unlock input
            });

            // if the response is taking too long, send a message to the user
            // to let them know that the assistant is still processing
            setTimeout(() => {
                if (isTyping) {
                    setMessages((prev) => [
                        ...prev,
                        {
                            id: messages.length + 3,
                            sender: 'assistant',
                            content: `I'm still processing your request...`,
                        },
                    ]);
                }
            }, 5000);
        }

    }


    return (
        <div className="fixed bottom-1.5 right-2 z-50">
            {!isChatOpen && (
                <button
                    className="border border-gray-400 text-black w-fit h-fit pt-3 pb-3 p-4 bg-white-600 rounded-full shadow-md flex items-center justify-center hover:scale-110 transition-transform"
                    onClick={toggleChat}
                >
                    <img src={require('./icons/chat-icon.svg').default} alt="Chat Icon" className="w-8 h-8"/>
                    Chat
                </button>
            )}

            {isChatOpen && (
                <div
                    className=" w-96 h-[600] min-h-[20vh] max-h-[90vh] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col">
                    {/* Header Bar */}
                    <div
                        className="bg-blue-500 text-white px-4 py-3 flex justify-between rounded-t-lg transition duration-300">
                        <div className="flex items-center px-2 gap-2">
                            <img
                                src={'/icons/bot.svg'}
                                alt="Chat Icon"
                                className="w-8 h-8"
                            />
                            <h3 className="text-base font-medium tracking-wide">AI Assistant</h3>
                        </div>
                        <button
                            onClick={toggleChat}
                            className="text-white text-2xl font-bold hover:scale-110 hover:rotate-90 transition duration-300 ease-in-out"
                            aria-label="Close chat"
                        >
                            ×
                        </button>
                    </div>
                    <div className="bg-yellow-100 text-yellow-800 text-xs px-4 py-2">
                        Disclaimer: This is an AI-powered assistant. Responses may not always be accurate. Verify
                        important information.
                    </div>
                    <div ref={containerRef}
                         className="flex-grow p-4 overflow-y-auto bg-gray-50 space-y-2">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`flex justify-${message.sender === 'user' ? 'end' : 'start'}`}  // Ensures messages align right for user and left for assistant
                            ><MessageBubble
                                key={message.id}
                                message={message}
                                onNavigate={handleNavigation}
                            />
                            </div>
                        ))}
                    </div>
                    {/* Input Section */}
                    <div className="p-2 border-t bg-gray-50 flex items-center">
                        <ChatInput
                            newMessage={newMessage}
                            setNewMessage={setNewMessage}
                            handleSendMessage={handleSendMessage}
                            isTyping={isTyping}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatAssistant;
