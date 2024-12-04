import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DataManager from "./api/PersistentDataManager";
import Home from "./components/Home";
import LoginForm from "./components/LoginForm";

const App = () => {
<<<<<<< HEAD
<<<<<<< HEAD
    // User authentication state
    const [isAuthenticated, setIsAuthenticated] = useState(true);
=======
    // User authentication state ---  set to true for development purposes
    const [isAuthenticated, setIsAuthenticated] = useState(process.env.NODE_ENV === 'development');
    const [userId, setUserId] = useState('');
>>>>>>> ebe76ee (Use new format for machine data structures)
=======
    // User authentication state
    const [isAuthenticated, setIsAuthenticated] = useState(false);
>>>>>>> 9be6c8f (Changed login form and userInfo)
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
<<<<<<< HEAD
>>>>>>> fcd8ad7 (Changed login form and userInfo)
=======
    const handleLogin = (userId: string, username: string, token: string, role: string, site: string) => {
>>>>>>> 30aa761 (Added report api)
=======
>>>>>>> 9be6c8f (Changed login form and userInfo)
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
        setUsername('');
        setToken(null);
        setRole('');
        setSite('');
<<<<<<< HEAD
    };

<<<<<<< HEAD
=======
    // Initialize data and set loading to false once done
    async function initializeData() {
        try {
            const dataManager = DataManager.getInstance();
            await dataManager.initialize();
            console.log("Data initialization completed.");
            console.log("KPI List:", dataManager.getKpiList());
            console.log("Machine List:", dataManager.getMachineList());
        } catch (error) {
            console.error("Error during initialization:", error);
        } finally {
            setLoading(false);  // Ensure loading is false once data initialization is done
        }
    }

    // Call initializeData on component mount
    useEffect(() => {
        initializeData();
    }, []); // Empty dependency array means this will run only once on mount

    // Show loading screen while data is being initialized or user is not authenticated
    if (loading && !isAuthenticated) {
        return (
            <div className="loading-screen">
                <h1>Loading...</h1>
            </div>
        );
=======
>>>>>>> 9be6c8f (Changed login form and userInfo)
    }

>>>>>>> 6439e03 (switch kpi list with new one)
    return (
        <Router>
            <div className="flex flex-col justify-center text-center min-h-screen bg-gray-200 font-bold">
                {isAuthenticated ? (
                    <Routes>
                        {/* Rotta principale per la dashboard */}
                        <Route
                            path="/*"
                            element={<Home username={username} role="Floor Factory Manager" token={token || ''} site={site}/>}
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
