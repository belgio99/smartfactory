import React, {useEffect, useState} from 'react';
import {Link} from "react-router-dom";
import {Alert, logout} from '../../api/ApiService';
import dataManager from "../../api/DataManager";
import {fetchAlerts} from "../../api/LogService";

const formatPath = (path: string): string => {
    return path
        .replace(/^\/|\/$/g, '') // Trim leading/trailing slashes
        .replace(/[_-]/g, ' ') // Replace underscores and hyphens with spaces
        .replace(/\b\w/g, char => char.toUpperCase()); // Capitalize each word
};

interface HeaderProps {
    path: string; // e.g., "/user_settings"
    userAvatar: string;
    userName: string;
    userId: string;
    role: string;
    logoutHook?: () => void;
}

const Header: React.FC<HeaderProps> = ({path, userAvatar, userName, userId, role, logoutHook}) => {
    const [menuVisible, setMenuVisible] = useState(false);
    const [notifyVisible, setNotifyVisible] = useState(false);
    const pathSegments = path.split('/').filter(Boolean);
    const [alerts, setAlerts] = useState<Alert[]>([]);

    useEffect(() => {
        // Fetch alerts on mount
        if (userId) fetchAlerts(userId);

        // Fetch alerts every x minutes (e.g., 5 minutes)
        const interval = setInterval(() => {
            fetchAlerts(userId);
        }, 5 * 60 * 1000); // 5 minutes
        return () => clearInterval(interval); // Cleanup interval on unmount
    }, [userId]);

    // Function to determine color based on severity
    const getSeverityColor = (severity: string) => {
        switch (severity.toLowerCase()) {
            case 'High':
                return 'bg-red-500 text-white';
            case 'Medium':
                return 'bg-orange-500 text-white';
            case 'Low':
                return 'bg-green-500 text-white';
            default:
                return 'bg-gray-500 text-white';
        }
    };


    return (
        <header className="flex justify-between items-center px-4 py-5 border-b bg-white border-gray-200">
            <nav aria-label="Breadcrumb" className="flex items-center mx-auto">
                <ol className="flex list-none space-x-2 text-xl text-gray-700">
                    {pathSegments.map((segment, index) => {
                        const segmentName = formatPath(segment);
                        return (
                            <React.Fragment key={index}>
                                <li>
                                    {index < pathSegments.length - 1 ? (
                                        <Link
                                            to={`/${pathSegments.slice(0, index + 1).join('/')}`}
                                            className="text-blue-600 hover:underline"
                                        >
                                            {segmentName}
                                        </Link>
                                    ) : (
                                        <span className="text-gray-900">{segmentName}</span>
                                    )}
                                </li>
                                {index < pathSegments.length - 1 && <li className="text-gray-400">/</li>}
                            </React.Fragment>
                        );
                    })}
                </ol>
            </nav>

            <div className="flex items-center">
                <div>
                    <button
                        className="p-2 bg-transparent border-none cursor-pointer mr-2"
                        aria-label="Notifications"
                        onClick={() => setNotifyVisible(!notifyVisible)}
                    >
                        <img
                            src="https://cdn.builder.io/api/v1/image/assets/TEMP/1e6000a94d38944aa66f553de36c98d945ea357c55a35129d63120550b298eb6"
                            alt="Notification Icon"
                            className="w-5 h-5"
                        />

                    </button>
                    {/* Notification Menu */}
                    {notifyVisible && alerts && (
                        <div
                            className="absolute right-60 mt-2 w-64 bg-white border border-gray-300 rounded shadow-lg z-10 translate-x-1"
                        >
                            {/* Notification List */}
                            <ul className="p-2">
                                {alerts.length === 0 ? (
                                    <p>No alerts to display.</p>
                                ) : (
                                    alerts.map((alert) => (
                                        <li
                                            key={alert.alertId}
                                            className={`p-4 mb-4 rounded shadow ${getSeverityColor(alert.severity)}`}
                                        >
                                            <h2 className="text-lg font-semibold">{alert.title}</h2>
                                            <p>{alert.description}</p>
                                            <span className="text-sm">
                            Triggered At: {new Date(alert.triggeredAt).toLocaleString()}
                        </span>
                                        </li>
                                    ))
                                )}
                            </ul>
                            {/* Button to go to the notifications page */}
                            <Link
                                to="/log"
                                className="block p-2 text-center text-sm text-blue-600 hover:bg-gray-100"
                            >
                                View All Notifications
                            </Link>
                        </div>
                    )}

                </div>
                {/* User Menu */}
                <div className={`relative flex ${menuVisible ? 'z-10' : ''}`}
                     onMouseEnter={() => setMenuVisible(true)}
                     onMouseLeave={() => setMenuVisible(false)}
                >
                    <img
                        src={require('./icon/avatar_32_32.svg').default}
                        alt="User Avatar"
                        className="w-8 h-8 rounded-full mr-2"
                    />
                    <div>
                    <span className="text-sm text-gray-900 cursor-pointer">
                        {userName}
                        {<span className="text-gray-500">({role})</span>}
                    </span>
                        {menuVisible && (
                            <div
                                className="absolute right-0 top-8 w-auto mx-auto flex-col bg-white border-2 p-2 border-gray-200">
                                <div
                                    className="right-0 mt-2 ">
                                    <div className="flex items-center px-1">
                                        <img alt={"userIcon"}
                                             src={'/icons/user.svg'}
                                        />
                                        <Link
                                            to="/user-settings"
                                            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                        >
                                            User Settings
                                        </Link>
                                    </div>
                                    <div
                                        className=" right-0 mt-2">
                                        <div className="flex items-center px-1">
                                            <img alt={"userIcon"}
                                                 src={'/icons/logout.svg'}
                                                 className="w-5 h-5"
                                            />
                                            <button
                                                className="block w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                                onClick={() => {
                                                    logout(userId);
                                                    alert("Logging out...");
                                                    logoutHook?.();
                                                    dataManager.getInstance().invalidateCaches()
                                                }}
                                            >
                                                Logout
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                        )}
                    </div>

                </div>
            </div>
        </header>
    );
};

export default Header;
