import {mockLogData} from './mockData/mockDataLog';
import {getAlerts} from "./ApiService";
import DataManager from "./DataManager";

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

export const fetchAlerts = async (userId: string) => {
    await DataManager.getInstance().waitUntilInitialized();
    console.log("Fetching alerts...");
    return getAlerts(userId).then((response) => {
        console.log("Alerts fetched: ", response);
        return response;
    }).catch((error) => {
        console.log("Error fetching alerts: ", error);
        return [];
    });
};

// Mark a log as read
export const markAsRead = (id: number): void => {
    logs = logs.map((log) =>
        log.id === id ? {...log, isRead: true} : log
    );
};

// Mark a log as not read
export const markAsNotRead = (id: number): void => {
    logs = logs.map((log) =>
        log.id === id ? {...log, isRead: false} : log
    );
}