import React from "react";

interface ChatInputProps {
    newMessage: string;
    setNewMessage: React.Dispatch<React.SetStateAction<string>>;
    handleSendMessage: (message: string) => void;
    isTyping: boolean; // Add this prop
}

const ChatInput: React.FC<ChatInputProps> = ({ newMessage, setNewMessage, handleSendMessage, isTyping }) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !isTyping) {
            handleSendMessage(newMessage);
            setNewMessage('');
        }
    };

    return (
        <div className="chat-input flex p-2 border-t">
            <input
                type="text"
                className="input-field flex-grow border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                disabled={isTyping} // Disable input when typing
            />
            <button
                className="send-button ml-2 bg-blue-400 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                onClick={() => {
                    if (newMessage.trim() === '') return;
                    handleSendMessage(newMessage);
                    setNewMessage('');
                }}
                disabled={isTyping} // Disable button when typing
            >
                {isTyping ? 'Waiting...' : 'Send'} {/* Feedback for user */}
            </button>
        </div>
    );
};

export default ChatInput;
