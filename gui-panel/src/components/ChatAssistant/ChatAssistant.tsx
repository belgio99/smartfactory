import React, {useState} from 'react';
import classNames from 'classnames';
import { useNavigate } from 'react-router-dom';

export interface Message {
  id: number;
  sender: 'user' | 'assistant';
  content: string;
  extraData?: {
    type: string;
    [key: string]: any;
  };
}

const ChatAssistant: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const navigate = useNavigate();

  const toggleChat = () => setIsChatOpen((prev) => !prev);

  const handleNavigation = (data: any) => {
    navigate(data.target, { state: { metadata: data.metadata } });
  };

  const handleSendMessage = () => {
    if (!newMessage.trim()) return;

    const userMessage: Message = { id: messages.length + 1, sender: 'user', content: newMessage };
    setMessages((prev) => [...prev, userMessage]);
    setNewMessage('');

    setTimeout(() => {
      const assistantMessage: Message = {
        id: messages.length + 2,
        sender: 'assistant',
        content: `This is a placeholder response for: "${newMessage}"`,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    }, 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSendMessage();
  };

  return (
      <div className="fixed bottom-2 right-2 z-50">
        {/* Chat Toggle Button */}
        {!isChatOpen && (
            <button
              className="border border-gray-400 text-black w-fit h-fit pt-3 pb-3 p-4 mx-auto pd-2 bg-white-600 rounded-full shadow-md flex items-center justify-center hover:scale-110 transition-transform"
              onClick={toggleChat}
              aria-label="Open chat"
            >
              <img src={require('./icons/chat-icon.svg').default} alt="Chat Icon" className="w-8 h-8"/>
              Chat
            </button>
        )}

        {/* Chat Window */}
        {isChatOpen && (
            <div className="w-80 h-96 bg-white rounded-lg shadow-lg flex flex-col">
              {/* Chat Header */}
              <div className="bg-blue-500 text-white px-4 py-2 flex justify-between items-center rounded-t-lg">
                <h3 className="text-lg font-semibold">Virtual Assistant</h3>
                <button
                    onClick={toggleChat}
                    className="text-white text-xl font-bold hover:text-gray-300"
                    aria-label="Close chat"
                >
                  ×
                </button>
              </div>

              {/* Disclaimer */}
              <div className="bg-yellow-100 text-yellow-800 text-xs px-4 py-2">
                Disclaimer: This is an AI-powered assistant. Responses may not always be accurate. Please verify
                important information.
              </div>

              {/* Chat Messages */}
              <div className="flex-grow p-4 overflow-y-auto bg-gray-50 space-y-2">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={classNames(
                            'max-w-[70%] px-4 py-2 rounded-lg text-sm break-words',
                            message.sender === 'user'
                                ? 'self-end bg-blue-500 text-white'
                                : 'self-start bg-gray-200 text-gray-800'
                        )}
                    >
                      {message.content}
                    </div>
                ))}
              </div>

              {/* Chat Input */}
              <div className="flex p-2 border-t">
                <input
                    type="text"
                    className="flex-grow border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                />
                <button
                    onClick={handleSendMessage}
                    className="ml-2 bg-blue-400 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
        )}
      </div>
  );
};

export default ChatAssistant;
