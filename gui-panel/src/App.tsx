import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DataManager from "./api/PersistentDataManager";
import Home from "./components/Home";
import LoginForm from "./components/LoginForm";

const App = () => {
    // User authentication state ---  set to true for development purposes
    const [isAuthenticated, setIsAuthenticated] = useState(process.env.NODE_ENV === 'development');
    const [userId, setUserId] = useState('');
    const [username, setUsername] = useState('Test User');
    const [token, setToken] = useState<string | null>(null);
    const [role, setRole] = useState('Tester');
    const [site, setSite] = useState('');
<<<<<<< HEAD
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
=======
    const [role, setRole] = useState('');
    const [site, setSite] = useState('');

    // Method to handle the login event
    const handleLogin = (username: string, token: string, role: string, site: string) => {
    // Method to handle the login event
    const handleLogin = (username: string, token: string, role: string, site: string) => {
>>>>>>> eca968f (Changed login form and userInfo)
        setIsAuthenticated(true);
        setUserId(userId);
        setUsername(username);
        setToken(token);
        setRole(role);
        setSite(site);
    };

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> eca968f (Changed login form and userInfo)
    // Method to handle the logout event
    const handleLogout = () => {
        setIsAuthenticated(false);
        setUserId('');
        setUsername('');
        setToken(null);
        setRole('');
        setSite('');
<<<<<<< HEAD
<<<<<<< HEAD
    };

<<<<<<< HEAD
=======
    // Initialize data and set loading to false once done
=======
>>>>>>> 1ffe85c (Changed login form and userInfo)
    async function initializeData() {
        try {
            const dataManager = DataManager.getInstance();
            await dataManager.initialize();
<<<<<<< HEAD
            console.log("Data initialization completed.");
            console.log("KPI List:", dataManager.getKpiList());
            console.log("Machine List:", dataManager.getMachineList());
            console.log("Dashboards:", dataManager.getDashboards());
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
=======
        } catch (error) {
            console.error("Error during initialization:", error);
        }
    }

    initializeData().then(
        () => {
            console.log("Data initialization completed.");
            // log the kpi list and the machine list
            const dataManager = DataManager.getInstance();
            console.log("KPI List:", dataManager.getKpiList());
            console.log("Machine List:", dataManager.getMachineList());
        },
        error => console.error("Error during data initialization:", error)
    );

>>>>>>> 1ffe85c (Changed login form and userInfo)
=======
    }

>>>>>>> eca968f (Changed login form and userInfo)
    return (
        <Router>
            <div className="flex flex-col justify-center text-center min-h-screen bg-gray-200 font-bold">
                <Routes>
                    <Route
                        path="/*"
                        element={<Home userId={userId} username={username} role={role} token={token || ''} site={site} />}
                    />
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;