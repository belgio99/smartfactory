import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {interactWithAgent} from '../../api/ApiService';
import ChatInput from './ChatInput';
import MessageBubble, {XAISources} from "./ChatComponents";

export interface Message {
    id: number;
    sender: 'user' | 'assistant';
    content: string;
    extraData?: {
        explanation?: XAISources[];
        dashboardData?: { target: string; metadata: any };
    };
}

export interface ChatAssistantProps {
    username: string;
}

const ChatAssistant: React.FC<ChatAssistantProps> = ({username}) => {
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [newMessage, setNewMessage] = useState('');
    const navigate = useNavigate();
    const [isTyping, setIsTyping] = useState(false);

    const toggleChat = () => setIsChatOpen((prev) => !prev);

    const handleNavigation = (target: string, metadata: any) => {
        navigate(target, {state: {metadata}});
    };

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
                            explanation: [
                                new XAISources("This is a sample dashboard that shows some key metrics.", "context", "source_name", 0.9, "original_context"),
                                new XAISources("You can click on the 'View Dashboard' button to see more details.", "context", "source_name", 0.9, "original_context"),
                                new XAISources("You can also click on the 'View Explanation' button to see an explanation of the data.", "context", "source_name", 0.9, "original_context"),
                            ],
                            dashboardData: {
                                target: '/dashboard/new',
                                metadata: {
                                    title: 'Dashboard',
                                    data: [
                                        {name: 'Sales', value: 100},
                                        {name: 'Revenue', value: 1000},
                                        {name: 'Customers', value: 10},
                                    ],
                                },
                            },
                        }
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
            interactWithAgent(userMessage.content)
                .then((response) => {
                    const assistantMessage: Message = {
                        id: messages.length + 2,
                        sender: 'assistant',
                        content: response.textResponse,
                        extraData: {}, //TODO: decode extra data
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
        <div className="fixed bottom-2 right-2 z-50">
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
                <div className="w-96 h-96 bg-white rounded-lg shadow-lg flex flex-col">
                    <div className="bg-blue-500 text-white px-4 py-2 flex justify-between items-center rounded-t-lg">
                        <h3 className="text-lg font-semibold">Virtual Assistant</h3>
                        <button
                            onClick={toggleChat}
                            className="text-white text-xl font-bold hover:text-gray-300"
                        >
                            ×
                        </button>
                    </div>
                    <div className="bg-yellow-100 text-yellow-800 text-xs px-4 py-2">
                        Disclaimer: This is an AI-powered assistant. Responses may not always be accurate. Verify
                        important information.
                    </div>
                    <div className="flex-grow p-4 overflow-y-auto bg-gray-50 space-y-2">
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
                    <div className="flex p-2 border-t">
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
