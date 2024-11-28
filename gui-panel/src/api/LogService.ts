import { mockLogData } from './mockData/mockDataLog';

export interface LogItem {
    id: number;
    type: string;
    header: string;
    body: string;
    isRead: boolean;
}

let logs = [...mockLogData]; // Clone mock data for testing

// Fetch logs
export const fetchLogs = (): LogItem[] => {
    return logs;
};

// Mark a log as read
export const markAsRead = (id: number): void => {
    logs = logs.map((log) =>
        log.id === id ? { ...log, isRead: true } : log
    );
};

// Mark a log as not read
export const markAsNotRead = (id: number): void => {
    logs = logs.map((log) =>
        log.id === id ? { ...log, isRead: false } : log
    );
}