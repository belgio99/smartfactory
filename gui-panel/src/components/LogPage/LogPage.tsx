import React, {useState, useMemo} from 'react';
import styles from './styles/LogPage.module.css';
import {fetchLogs, markAsRead} from '../../api/LogService';
import {FaInfoCircle, FaExclamationTriangle, FaTimesCircle, FaChevronDown, FaChevronUp} from 'react-icons/fa';

interface LogItem {
    id: number;
    type: string;
    header: string;
    body: string;
    isRead: boolean;
}

const LogPage: React.FC = () => {
    const [logs, setLogs] = useState<LogItem[]>(fetchLogs());
    const [expandedLog, setExpandedLog] = useState<number | null>(null);
    const [filterType, setFilterType] = useState<string>('All');
    const [filterReadStatus, setFilterReadStatus] = useState<string>('All');

    const handleFilterTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setFilterType(e.target.value);
    };

    const handleFilterReadStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setFilterReadStatus(e.target.value);
    };

    const filteredLogs = useMemo(
        () =>
            logs.filter((log) => {
                const matchesType = filterType === 'All' || log.type === filterType;
                const matchesReadStatus =
                    filterReadStatus === 'All' ||
                    (filterReadStatus === 'Read' && log.isRead) ||
                    (filterReadStatus === 'Unread' && !log.isRead);
                return matchesType && matchesReadStatus;
            }),
        [logs, filterType, filterReadStatus]
    );

    const handleExpand = (id: number) => {
        setExpandedLog((prev) => (prev === id ? null : id));
        const targetLog = logs.find((log) => log.id === id);
        if (targetLog && !targetLog.isRead) {
            markAsRead(id);
            setLogs((prevLogs) =>
                prevLogs.map((log) => (log.id === id ? {...log, isRead: true} : log))
            );
        }
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'Info':
                return <FaInfoCircle className={styles.iconInfo}/>;
            case 'Warning':
                return <FaExclamationTriangle className={styles.iconWarning}/>;
            case 'Error':
                return <FaTimesCircle className={styles.iconError}/>;
            default:
                return null;
        }
    };

    return (
        <div className="bg-white flex-col rounded-lg shadow-lg w-auto max-w-5xl mx-auto px-6 pt-3">
            <h1 className={styles.title}>Log Notifications</h1>

            <div className="mb-4 flex space-x-4 font-semibold">
                <div>
                    <label htmlFor="logFilterType" className="text-sm font-medium text-gray-700">
                        Filter by Type:
                    </label>
                    <select
                        id="logFilterType"
                        value={filterType}
                        onChange={handleFilterTypeChange}
                        className="ml-2 p-2 border border-gray-300 rounded-md shadow-sm"
                    >
                        <option value="All">All</option>
                        <option value="Info">Info</option>
                        <option value="Warning">Warning</option>
                        <option value="Error">Error</option>
                    </select>
                </div>

                <div>
                    <label htmlFor="logFilterReadStatus" className="text-sm font-medium text-gray-700">
                        Show:
                    </label>
                    <select
                        id="logFilterReadStatus"
                        value={filterReadStatus}
                        onChange={handleFilterReadStatusChange}
                        className="ml-2 p-2 border border-gray-300 rounded-md shadow-sm"
                    >
                        <option value="All">All</option>
                        <option value="Read">Read</option>
                        <option value="Unread">Unread</option>
                    </select>
                </div>
            </div>

            <div className="text-start p-5" role="list">
                {filteredLogs.map((log) => (
                    <div
                        key={log.id}
                        className={`border rounded-lg p-4 mb-4 cursor-pointer transition-transform transform hover:scale-105 ${log.isRead
                            ? 'bg-gray-50  text-gray-500' // Faded gray for read
                            : 'bg-white text-gray-800'   // Clean white for unread 
                        }`}
                        role="listitem"
                    >
                        <div
                            className="flex items-center justify-between"
                            onClick={() => handleExpand(log.id)}
                            role="button"
                            aria-expanded={expandedLog === log.id}
                        >
                            {/* Icon */}
                            <div className="flex items-center space-x-4">
                                {getIcon(log.type)}
                                <div className="flex flex-col">
                                    <span className="text-lg font-semibold ">{log.header}</span>
                                    <span className={log.isRead
                            ? "text-sm text-gray-400 font-normal" : "text-sm text-gray-500"}>{log.type}</span>
                                </div>
                            </div>

                            {/* Status and Expand Toggle */}
                            <div className="flex items-center space-x-4">
                                {!log.isRead && (
                                    <span className="w-3 h-3 bg-blue-500 rounded-full"></span>
                                )}
                                <span className="text-gray-600">
                        {expandedLog === log.id ? <FaChevronUp/> : <FaChevronDown/>}
                    </span>
                            </div>
                        </div>

                        {/* Expanded Body */}
                        {expandedLog === log.id && (
                            <div className="mt-4 text-gray-600 font-normal">
                                <p>{log.body}</p>
                            </div>
                        )}
                    </div>
                ))}
            </div>

        </div>
    )
        ;
};

export default LogPage;
