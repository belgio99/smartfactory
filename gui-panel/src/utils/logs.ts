import Cookies from 'js-cookie';

export interface LogEntry {
    id: number;
    type: string;
    header: string;
    body: string;
    isRead: boolean;
}

// Recupera i log dal cookie
export const getLogsFromCookies = (username: string): LogEntry[] => {
    const logs = Cookies.get(`logs_${username}`);
    return logs ? JSON.parse(logs) : [];
};

// Salva i log nel cookie
export const saveLogsToCookies = (username: string, logs: LogEntry[]) => {
    Cookies.set(`logs_${username}`, JSON.stringify(logs), { expires: 7 });
};

// Aggiunge un nuovo log e salva nei cookie
export const addLogEntry = (
    username: string,
    log: LogEntry,
    onNotification: (message: string) => void
) => {
    const currentLogs = getLogsFromCookies(username);
    const updatedLogs = [...currentLogs, log];
    saveLogsToCookies(username, updatedLogs);

    // Notifica l'utente di un nuovo log
    onNotification(`New log: ${log.header}`);
};