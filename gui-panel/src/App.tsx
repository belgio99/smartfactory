import React, {useEffect, useState} from 'react';
import {BrowserRouter as Router, Navigate, Route, Routes} from 'react-router-dom';
import DataManager from "./api/DataManager";
import Home from "./components/Home";
import LoginForm from "./components/LoginForm";


const App = () => {

    // User authentication state ---  set to true for development purposes
    //const [isAuthenticated, setIsAuthenticated] = useState(process.env.NODE_ENV === 'development');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userId, setUserId] = useState('');
    const [username, setUsername] = useState('Test User');
    const [token, setToken] = useState<string | null>(null);
    const [role, setRole] = useState('Tester');
    const [site, setSite] = useState('');
    const [email, setEmail] = useState('');
    const dataManager = DataManager.getInstance(); // force creation of the static instance on boot

    // Loading state to track if data is still being initialized
    const [loading, setLoading] = useState(false);

    // Method to handle the login event
    const handleLogin = (userId: string, username: string, token: string, role: string, site: string, email: string) => {
        setIsAuthenticated(true);
        setUserId(userId);
        setUsername(username);
        setToken(token);
        setRole(role);
        setSite(site);
        setEmail(email);
    };

    // Method to handle the logout event
    const handleLogout = () => {
        setIsAuthenticated(false);
        setUserId('');
        setUsername('');
        setToken(null);
        setRole('');
        setSite('');
        setEmail('');
    };

    // Method to login the test user
    const loginTestUser = () => {
        setUserId('9');
        handleLogin('9', 'user5', '', 'Tester', 'site1', 'test@smartfactory.com');
    };

    // Initialize data and set loading to false once done
    async function initializeData() {
        try {
            dataManager.setUserId(userId);
            await dataManager.initialize();
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
        if (isAuthenticated) {
            //loginTestUser();
            setLoading(true);
            console.log("Initializing data...");
            initializeData();
            setLoading(false);
        }
    }, [isAuthenticated]); // Empty dependency array means this will run only once on mount

    // Show loading screen while data is being initialized or user is not authenticated
    if (loading) {
        return (
            <div className="loading-screen">
                <div className="flex justify-center items-center h-40">
                    <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-gray-900"/>
                </div>
            </div>
        );
    }

    // Show login page if not authenticated
    if (!isAuthenticated) {
        return (
            <Router>
                <Routes>
                    <Route path="/" element={<LoginForm onLogin={handleLogin}/>}/>
                    <Route path="*" element={<Navigate to="/"/>}/>
                </Routes>
            </Router>
        );
    }

    // Show the home page (with the sidebar) once authenticated and data is initialized
    return (
        <Router>
            <div className="flex flex-col justify-center text-center min-h-screen bg-gray-200 font-bold">
                <Routes>
                    <Route
                        path="/*"
                        element={<Home userId={userId} username={username} role={role} token={token || ''} site={site}
                                       email={email} onLogout={handleLogout}/>}
                    />
                    <Route path="*" element={<Navigate to="/"/>}/>
                </Routes>
            </div>
        </Router>
    );
};

export default App;