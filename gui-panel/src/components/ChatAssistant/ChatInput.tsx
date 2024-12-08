import React from "react";

interface ChatInputProps {
    newMessage: string;
    setNewMessage: React.Dispatch<React.SetStateAction<string>>;
    handleSendMessage: (message: string) => void;
    isTyping: boolean; // Add this prop
}

const ChatInput: React.FC<ChatInputProps> = ({newMessage, setNewMessage, handleSendMessage, isTyping}) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !isTyping) {
            handleSendMessage(newMessage);
            setNewMessage('');
        }
    };

    return (
        <div className="chat-input flex items-center p-2 border-t w-full">
    <textarea
        className="input-field flex-grow border border-gray-300 rounded-lg px-3 py-2 text-sm font-normal outline-none focus:ring-2 focus:ring-blue-500 resize-none w-full overflow-hidden"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={isTyping}
        rows={1} // Start with a single row
        onInput={(e) => {
            const textarea = e.target as HTMLTextAreaElement; // Type assertion
            // Auto-resize textarea based on content
            textarea.style.height = 'auto';
            textarea.style.height = `${textarea.scrollHeight}px`;
        }}
    />

            {/* Send button with icon */}
            {newMessage.trim().length > 0 && !isTyping && (
                <button
                    className="send-button ml-2 bg-blue-400 text-white px-2.5 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors"
                    onClick={() => {
                        if (newMessage.trim() === '') return;
                        handleSendMessage(newMessage);
                        setNewMessage('');
                    }}
                    disabled={isTyping}
                >
                    <img src="/icons/send.svg" alt="Send" className="w-6 h-6 -rotate-45"/>
                </button>
            )}
        </div>


    );
};

export default ChatInput;
