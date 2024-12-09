import React from 'react';
import styles from './styles/Home.module.css';

interface HomeProps {
  username: string;
  token: string;
  role: string;
  site: string;
}

const Home: React.FC<HomeProps> = ({ username, token, role, site }) => {
  return (
    <div className={styles.homeContainer}>
      <h1>Welcome, {username}!</h1>
      <p>This is your dashboard where you can access all the functionalities.</p>
      {/* Aggiungi qui altre sezioni o link */}
    </div>
  );
};

export default Home;
