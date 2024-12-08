import React, {useState} from 'react';
import styles from '../styles/LoginForm.module.css';
// API service
import {login, register, UserInfo} from '../api/ApiService';
// Security service
import {hashPassword} from '../api/security/securityService';

interface LoginFormProps {
    onLogin: (userId: string, username: string, token: string, role: string, site: string, email: string) => void;
}

const LoginForm: React.FC<LoginFormProps> = ({onLogin}) => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('');
    const [site, setSite] = useState('');
    const [token, setToken] = useState('');
    const [userId, setUserId] = useState('');
    const [email, setEmail] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmitLogin = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Check if is an email
            const isEmail = username.includes('@'); // Determina se l'input è un'email
            // Call the login API
            const hashedPassword = await hashPassword(password);
            // Pass the username, isEmail and hashed password
            const loginResponse: UserInfo = await login(username, isEmail, hashedPassword);
            console.log(username, isEmail, hashedPassword);
            //const loginResponse = await login(username, isEmail, password);
            console.log(loginResponse);
            // If the login is successful, call the onLogin function
            if (loginResponse) {
                if (loginResponse.access_token) {
                    // Call the onLogin function
                    // Pass the user information to the parent component
                    onLogin(loginResponse.userId,        // User ID
                        loginResponse.username,      // Username
                        loginResponse.access_token,  // Token
                        loginResponse.role,          // Role
                        loginResponse.site,          // Site
                        loginResponse.email);        // Email
                } else {
                    setError('Invalid credentials!');
                }
            } else {
                setError('Invalid credentials!');
            }
        } catch (err) {
            setError('Error during login. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmitRegister = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Check if is an email
            const isEmail = username.includes('@'); // Determina se l'input è un'email
            // Call the login API
            const hashedPassword = await hashPassword(password);
            // Pass the username, isEmail and hashed password

            // Call the register API
            const registerResponse = await register(username, email, hashedPassword, role, site);
            // If the register is successful, call the onLogin function
            if (registerResponse) {
                if (registerResponse.access_token) {
                    // Call the onLogin function
                    // Pass the user information to the parent component
                    onLogin(registerResponse.userId,        // User ID
                        registerResponse.username,      // Username
                        registerResponse.access_token,  // Token
                        registerResponse.role,          // Role
                        registerResponse.site,          // Site
                        registerResponse.email);        // Email
                } else {
                    setError('Invalid credentials!');
                }
            } else {
                setError('Error during registration. Please try again.');
            }
        } catch (err) {
            setError('Error during registration. Please try again.');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className={styles.loginContainer}>
            {isRegistering ?

                (<form onSubmit={handleSubmitRegister} className={styles.loginForm}>
                        <h2 className={styles.title}>Register</h2>
                        {error && <div className={styles.errorMessage}>{error}</div>}
                        <div className={styles.inputGroup}>
                            <label>Username:</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Password:</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            {/*Either Floor Factory Manager or Specialty Manufactory Owner */}
                            <label>Role:</label>
                            <select
                                value={role}
                                onChange={(e) => setRole(e.target.value)}
                                className={styles.input}
                            >
                                <option value="FloorFactoryManager">Floor Factory Manager</option>
                                <option value="SpecialtyManufactoryOwner">Specialty Manufactory Owner</option>
                            </select>
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Site:</label>
                            <input
                                type="text"
                                value={site}
                                onChange={(e) => setSite(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Email:</label>
                            <input
                                type="text"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <button type="submit" className={styles.loginButton} disabled={loading}>
                            {loading ? 'Loading...' : 'Register'}
                        </button>
                        <button type="button" onClick={() => setIsRegistering(false)} className={styles.loginButton}>
                            Cancel
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleSubmitLogin} className={styles.loginForm}>
                        <h2 className={styles.title}>Login</h2>
                        {error && <div className={styles.errorMessage}>{error}</div>}
                        <div className={styles.inputGroup}>
                            <label>Username:</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Password:</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className={styles.input}
                            />
                        </div>
                        <button type="submit" className={styles.loginButton} disabled={loading}>
                            {loading ? 'Loading...' : 'Login'}
                        </button>
                        <button type="button" className={styles.loginButton} disabled={loading}
                                onClick={() => {
                                    setIsRegistering(true);
                                    setError(null);
                                }}>
                            {loading ? 'Loading...' : 'Register (Testing Only)'}
                        </button>

                    </form>
                )
            }
        </div>

    );
};

export default LoginForm;
