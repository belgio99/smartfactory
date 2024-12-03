import React, { useState } from 'react';
import classNames from 'classnames';
import {Message} from "./ChatAssistant";

interface MessageProps {
    message: Message;
}

const MessageBubble: React.FC<MessageProps> = ({ message }) => {
    return (
        <div
            className={classNames(
                'message-bubble',
                message.sender === 'user' ? 'user-message' : 'assistant-message'
            )}
        >
            <p>{message.content}</p>
            {message.extraData && <MessageContent extraData={message.extraData} />}
        </div>
    );
};

export default MessageBubble;

interface MessageContentProps {
    extraData: {
        type: string;
        additionalContent?: string;
        sources?: string[];
    };
}

const MessageContent: React.FC<MessageContentProps> = ({ extraData }) => {
    const [showSources, setShowSources] = useState(false);

    const toggleSources = () => {
        setShowSources((prev) => !prev);
    };

    return (
        <div>
            {extraData.additionalContent && <div className="additional-content">{extraData.additionalContent}</div>}
            {extraData.sources && (
                <div className="sources-section">
                    <button onClick={toggleSources} className="view-sources-button">
                        {showSources ? 'Hide Sources' : 'View Sources'}
                    </button>
                    {showSources && <SourcesList sources={extraData.sources} />}
                </div>
            )}
        </div>
    );
};


interface SourcesListProps {
    sources: string[];
}

const SourcesList: React.FC<SourcesListProps> = ({ sources }) => {
    return (
        <ul className="sources-list">
            {sources.map((source, index) => (
                <li key={index}>
                    <a href={source} target="_blank" rel="noopener noreferrer" className="source-link">
                        {source}
                    </a>
                </li>
            ))}
        </ul>
    );
};

interface ChatInputProps {
    newMessage: string;
    setNewMessage: React.Dispatch<React.SetStateAction<string>>;
    handleSendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ newMessage, setNewMessage, handleSendMessage }) => {
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSendMessage(newMessage);
            setNewMessage('');
        }
    };

    return (
        <div className="chat-input">
            <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
                className="input-field"
            />
            <button
                onClick={() => handleSendMessage(newMessage)}
                className="send-button"
            >
                Send
            </button>
        </div>
    );
};

