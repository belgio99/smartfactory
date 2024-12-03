import apiClient from '../apiClient';

// Esempio di hashing password (simulato dall'API)
export const hashPassword = async (password: string) => {
  try {
    const response = await apiClient.post('/security/hash', { password });
    return response.data; // Contiene l'hash generato
  } catch (error) {
    console.error('Errore nella richiesta API:', error);
    throw error;
  }
};

// Esempio di login sicuro
export const secureLogin = async (username: string, password: string) => {
  try {
    const response = await apiClient.post('/auth/login', { username, password });
    return response.data; // Contiene i dettagli del login
  } catch (error) {
    console.error('Errore durante il login:', error);
    throw error;
  }
};
