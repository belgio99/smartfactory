import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'https://api.redhat.com', // Sostituisci con l'URL dell'API esterna
  headers: {
    'Content-Type': 'application/json',
    // Aggiungi ulteriori intestazioni se richiesto, ad esempio token
    // Authorization: `Bearer ${yourToken}`
  },
  timeout: 5000, // Timeout di 5 secondi
});

export default apiClient;