import React, {useState} from 'react';
import classNames from 'classnames';
import {Message} from "./ChatAssistant";

export class XAISources {
    // base it off the explanation interface
    response_segment: number;
    context?: string;
    source_name?: string;
    original_context?: string;

    constructor(response_segment: number, context?: string, source_name?: string, original_context?: string) {
        this.response_segment = response_segment;
        this.context = context;
        this.source_name = source_name;
        this.original_context = original_context;
    }

    static decode(json: Record<string, any>): XAISources {
        //typechecks
        if (typeof json.reference_number !== "number") {
            console.log(json.reference_number);
            throw new Error("Invalid type for reference_number");
        }
        if (json.context && typeof json.context !== "string") {
            throw new Error("Invalid type for context");
        }
        if (json.source_name && typeof json.source_name !== "string") {
            throw new Error("Invalid type for source_name");
        }
        if (json.original_context && typeof json.original_context !== "string") {
            throw new Error("Invalid type for original_context");
        }

        return new XAISources(json.reference_number, json.context, json.source_name, json.original_context);
    }
}

interface MessageProps {
    message: Message;
    onNavigate: (target: string, metadata: any) => void;
}

const MessageBubble: React.FC<MessageProps> = ({message, onNavigate}) => {
    return (
        <div
            className={classNames(
                'w-fit max-w-[70%] px-4 py-2 rounded-lg text-start shadow-md',
                message.sender === "user"
                    ? 'bg-blue-200'
                    : 'bg-gray-200'
            )}
        >
            <div className="text-xs text-gray-600 font-semibold">
                {message.sender === 'user' ? 'You' : 'Assistant'}
            </div>
            <p className="text-gray-800 text-sm text-wrap break-words font-[450] ">{message.content}</p>
            {message.extraData && <ExtraDataButtons extraData={message.extraData} onNavigate={onNavigate}/>}
        </div>
    );
};

interface ExtraDataProps {
    extraData: {
        explanation?: XAISources[];
        dashboardData?: { target: string; metadata: any };
        report?: { userId: string; reportId: string };
    };
    onNavigate: (target: string, metadata: any) => void;
}

const ExtraDataButtons: React.FC<ExtraDataProps> = ({extraData, onNavigate}) => {
    const [isExplanationOpen, setIsExplanationOpen] = useState(false);

    const toggleExplanation = () => setIsExplanationOpen((prev) => !prev);

    const metadata = extraData.dashboardData;
    const [activeSource, setActiveSource] = useState<string | null>(null);
    const openSourceInModal = (source: string | undefined) => {
        if (source) setActiveSource(source);
    };
    const closeModal = () => setActiveSource(null);

    return (
        <div className="mt-2 space-y-2">

            {/* Dashboard Navigation Button */}
            {metadata && (
                <button
                    onClick={() => onNavigate("dashboards/new", metadata.metadata)}
                    className="inline-block px-4 py-2 text-white bg-green-500 hover:bg-green-600 rounded-lg text-sm shadow-md focus:outline-none"
                >
                    Go to Dashboard
                </button>
            )}

            {/* Report Button */}
            {extraData.report && (
                <div className="flex-col">
                    <button
                        onClick={() => onNavigate("reports/view", extraData.report)}
                        className="inline-block px-4 py-2 text-white bg-green-500 hover:bg-green-600 rounded-lg text-sm shadow-md focus:outline-none"
                    >
                        View Report
                    </button>
                    <button
                        onClick={() => onNavigate("reports/download", extraData.report)}
                        className="inline-block px-4 py-2 text-white bg-blue-500 hover:bg-blue-600 rounded-lg text-sm shadow-md focus:outline-none mt-2"
                    >
                        Download Report
                    </button>
                </div>
            )
            }

            {/* Explanation Button */}
            {extraData.explanation && extraData.explanation.length > 0 && (
                <div>
                    <button
                        onClick={toggleExplanation}
                        className="inline-block px-2 py-1 text-xs underline text-blue-500 focus:outline-none"
                    >
                        {isExplanationOpen ? "Hide Explanation" : "View Sources"}
                    </button>
                    {isExplanationOpen && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                            <div
                                className="bg-white max-h-[95vh] min-h-[50vh] rounded-lg shadow-lg p-4 max-w-lg w-full overflow-y-auto">
                                <div className="flex justify-between items-center mb-4">
                                    <h3 className="text-lg font-bold text-gray-800">Explanation</h3>
                                    <button
                                        onClick={toggleExplanation}
                                        className="text-gray-600 hover:text-gray-800"
                                        aria-label="Close"
                                    >
                                        ×
                                    </button>
                                </div>
                                <div>
                                    {activeSource && (
                                        <div
                                            className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
                                            <div
                                                className="bg-white min-h-fit rounded-lg shadow-lg p-4 max-w-lg w-full">
                                                <div className="flex justify-between items-center mb-4">
                                                    <h3 className="text-lg font-bold text-gray-800">Source Details</h3>
                                                    <button
                                                        onClick={closeModal}
                                                        className="text-gray-600 hover:text-gray-800"
                                                        aria-label="Close"
                                                    >
                                                        ×
                                                    </button>
                                                </div>
                                                <div
                                                    className="overflow-y-auto flex-wrap text-wrap max-h-[80vh] min-h-[40vh] text-gray-700">
                                                    <pre
                                                        className="whitespace-pre-wrap overflow-x-hidden">{activeSource}</pre>
                                                </div>
                                                <div className="mt-4 text-right">
                                                    <button
                                                        onClick={closeModal}
                                                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                                    >
                                                        Close
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                                {/* Loop through the explanation segments */}
                                {extraData.explanation.map((segment, index) => (
                                    <div key={index} className="mb-4">
                                        <div
                                            className="font-semibold text-lg">{"[" + segment.response_segment + "]"}</div>
                                        {segment.context && (
                                            <pre
                                                className="italic text-wrap text-gray-700 mb-2">Context: {segment.context}</pre>
                                        )}
                                        {segment.source_name && (
                                            <pre className="text-blue-600 mb-2 cursor-pointer"
                                                 onClick={() => openSourceInModal(segment?.original_context)}>
                                                Source: {segment.source_name}
                                            </pre>
                                        )}
                                    </div>
                                ))}

                                <div className="mt-4 text-right">
                                    <button
                                        onClick={toggleExplanation}
                                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

        </div>
    );
};

export default MessageBubble;