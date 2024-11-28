import React from 'react';
import styles from './styles/Home.module.css';

interface HomeProps {
  username?: string;
}

const Home: React.FC<HomeProps> = ({ username }) => {
  return (
    <div className={styles.homeContainer}>
      <h1>Welcome, {username}!</h1>
      <p>This is your dashboard where you can access all the functionalities.</p>
      {/* Aggiungi qui altre sezioni o link */}
    </div>
  );
};

export default Home;
