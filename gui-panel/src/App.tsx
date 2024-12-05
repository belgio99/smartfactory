import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Home';
import LoginForm from './components/LoginForm';
import DataManager from "./api/PersistentDataManager";

const App = () => {
    // User authentication state
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userId, setUserId] = useState('');
    const [username, setUsername] = useState('');
    const [token, setToken] = useState<string | null>(null);
    const [role, setRole] = useState('');
    const [site, setSite] = useState('');
<<<<<<< HEAD
    const [role, setRole] = useState('');
    const [site, setSite] = useState('');

    // Method to handle the login event
<<<<<<< HEAD
    const handleLogin = (username: string, token: string, role: string, site: string) => {
    // Method to handle the login event
    const handleLogin = (username: string, token: string, role: string, site: string) => {
=======

    // Method to handle the login event
    const handleLogin = (username: string, token: string, role: string, site: string) => {
>>>>>>> fcd8ad7 (Changed login form and userInfo)
=======
    const handleLogin = (userId: string, username: string, token: string, role: string, site: string) => {
>>>>>>> 30aa761 (Added report api)
        setIsAuthenticated(true);
        setUserId(userId);
        setUsername(username);
        setToken(token);
        setRole(role);
        setSite(site);
    };

    // Method to handle the logout event
    const handleLogout = () => {
        setIsAuthenticated(false);
        setUserId('');
        setUsername('');
        setToken(null);
        setRole('');
        setSite('');
    }

    return (
        <Router>
            <div className=" flex flex-col justify-center text-center min-h-screen bg-gray-200 font-bold">
                {isAuthenticated ? (
                    <Routes>
                        {/* Rotta principale per la dashboard */}
                        <Route
                            path="/*"
                            element={<Home userId={userId} username={username} role={role} token={token || ''} site={site}/>}
                        />
                        {/* Reindirizza qualsiasi rotta non valida */}
                        <Route path="*" element={<Navigate to="/"/>}/>
                    </Routes>
                ) : (
                    <Routes>
                        {/* Rotta per il login */}
                        <Route path="/" element={<LoginForm onLogin={handleLogin}/>}/>
                        {/* Reindirizza qualsiasi rotta non valida */}
                        <Route path="*" element={<Navigate to="/"/>}/>
                    </Routes>
                )}
            </div>
        </Router>
    );
};

export default App;
