import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Home';
import LoginForm from './components/LoginForm';

const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');
    const [token, setToken] = useState<string | null>(null);

    const handleLogin = (username: string, token: string) => {
        setIsAuthenticated(true);
        setUsername(username);
        setToken(token);
    };

    return (
        <Router>
            <div className=" flex flex-col justify-center text-center min-h-screen bg-gray-200 font-bold">
                {isAuthenticated ? (
                    <Routes>
                        {/* Rotta principale per la dashboard */}
                        <Route
                            path="/*"
                            element={<Home username={username} role="Floor Factory Manager"/>}
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
