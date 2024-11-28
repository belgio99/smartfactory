import React, { useState } from 'react';
import { secureLogin } from '../api/security/securityService'; // Importa il servizio API
import styles from '../styles/LoginForm.module.css';

interface LoginFormProps {

    onLogin: (username: string, token: string) => void;
  
  }

const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);

    try {
      //let data = await secureLogin(username, password); // Chiamata all'API
      //console.log('Risultato API:', data);
      const data = {
        success: true,
        user: {
          username: 'test',
          token: '12345'
        }
      };
      if (data.success) {
        onLogin(username, password); // Notifica il login riuscito
      } else {
        alert('Credenziali non valide!');
      }
    } catch (error) {
      alert('Errore durante il login. Riprova.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.loginContainer}>
      <form onSubmit={handleSubmit} className={styles.loginForm}>
        <h2 className={styles.title}>Login</h2>
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
      </form>
    </div>
  );
};

export default LoginForm;
