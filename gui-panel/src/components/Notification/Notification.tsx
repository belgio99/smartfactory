import React, { createContext, useContext, useReducer, useCallback } from 'react';

interface Notification {
    id: number;
    type: string; // 'Info', 'Error', 'Warning', etc.
    message: string;
    isRead: boolean;
}

interface NotificationState {
    notifications: Notification[];
}

interface NotificationContextProps {
    notifications: Notification[];
    addNotification: (notification: Notification) => void;
    removeNotification: (id: number) => void;
    markAsRead: (id: number) => void;
}

const NotificationContext = createContext<NotificationContextProps | undefined>(undefined);

const notificationReducer = (state: NotificationState, action: any): NotificationState => {
    switch (action.type) {
        case 'ADD_NOTIFICATION':
            return { notifications: [...state.notifications, action.payload] };
        case 'REMOVE_NOTIFICATION':
            return {
                notifications: state.notifications.filter(
                    (notification) => notification.id !== action.payload
                ),
            };
        case 'MARK_AS_READ':
            return {
                notifications: state.notifications.map((notification) =>
                    notification.id === action.payload
                        ? { ...notification, isRead: true }
                        : notification
                ),
            };
        default:
            throw new Error(`Unhandled action type: ${action.type}`);
    }
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [state, dispatch] = useReducer(notificationReducer, { notifications: [] });

    const addNotification = useCallback((notification: Notification) => {
        dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    }, []);

    const removeNotification = useCallback((id: number) => {
        dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
    }, []);

    const markAsRead = useCallback((id: number) => {
        dispatch({ type: 'MARK_AS_READ', payload: id });
    }, []);

    const value = {
        notifications: state.notifications,
        addNotification,
        removeNotification,
        markAsRead,
    };

    return (
        <NotificationContext.Provider value={value}>
            {children}
        </NotificationContext.Provider>
    );
};

export const useNotification = (): NotificationContextProps => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotification must be used within a NotificationProvider');
    }
    return context;
};