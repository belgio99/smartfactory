import apiClient from './apiClient';

// Recover the user information
export const getUserInfo = async (userId: string) => {
  try {
    const response = await apiClient.get(`/users/${userId}`);
    return response.data; // User data
  } catch (error) {
    console.error('Error to recover the account information: ', error);
    throw error;
  }
};

// Register new user
export const registerUser = async (username: string, email: string, password: string) => {
  try {
    const response = await apiClient.post('/users/register', {
      username,
      email,
      password,
    });
    return response.data; // Check the user registration
  } catch (error) {
    console.error('Error to register the user:', error);
    throw error;
  }
};

// Update the user information
export const updateUser = async (userId: string, updates: Record<string, unknown>) => {
  try {
    const response = await apiClient.put(`/users/${userId}`, updates);
    return response.data; // New details of the user
  } catch (error) {
    console.error('Error to update the user information:', error);
    throw error;
  }
};

// Delete the user
export const deleteUser = async (userId: string) => {
  try {
    const response = await apiClient.delete(`/users/${userId}`);
    return response.data; // Response of the deletion
  } catch (error) {
    console.error('Error to delete the user:', error);
    throw error;
  }
};
