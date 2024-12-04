import axios from 'axios';

const BASE_URL = 'https://your-api-url.com'; // API URL

// Interfacce per i dati
export interface UserInfo {
  userId: string;
  username: string;
  email: string;
  role: string;
  access_token?: string;
  site: string;
}

export interface LoginResponse {
  outcome: boolean;
  userInfo?: UserInfo;
  message?: string;
}

export interface Report {
  id: string;
  title: string;
  description: string;
  createdAt: string;
}

export interface HistoricalDataResponse {
  [key: string]: any; // 
}

// Dashboard interface
export interface DashboardData {
  [key: string]: any;
}
//
export interface UserSettings {
  [key: string]: string | number | boolean;
}

//
export interface Alert {
  alertId: string;
  title: string;
  type: string;
  description: string;
  triggeredAt: string;
  machineName: string;
  isPush: boolean;
  isEmail: boolean;
  recipients: string[];
  severity: string;
}

///
///
///
///
///
///

// Method to login
export const login = async (
  user: string,
  isEmail: boolean,
  password: string
): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(`${BASE_URL}/smartfactory/login`, {
      user,
      isEmail,
      password,
    });
    return response.data;
  } catch (error: any) {
    console.error('Login API error:', error);
    throw new Error(error.response?.data?.message || 'Login failed');
  }
};

// Method to register
export const register = async (
  username: string,
  email: string,
  password: string,
  role: string,
  site: string
): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(`${BASE_URL}/smartfactory/signup`, {
      username,
      email,
      password,
      role,
      site,
    });
    return response.data;
  } catch (error: any) {
    console.error('Register API error:', error);
    throw new Error(error.response?.data?.message || 'Registration failed');
  }
};

// Method to get reports
export const getReports = async (userId?: string): Promise<Report[]> => {
  try {
    const response = await axios.get<{ data: Report[] }>(
      `${BASE_URL}/smartfactory/reports`,
      {
        params: { userId },
      }
    );
    return response.data.data;
  } catch (error: any) {
    console.error('Get Reports API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to retrieve reports');
  }
};

// Method to get historical data
export const getHistoricalData = async (query: string[]): Promise<HistoricalDataResponse> => {
  try {
    const response = await axios.get<{ data: HistoricalDataResponse }>(
      `${BASE_URL}/smartfactory/historical`,
      {
        params: { query },
      }
    );
    return response.data.data;
  } catch (error: any) {
    console.error('Get Historical Data API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to retrieve historical data');
  }
};

// API Dashboard
export const getDashboards = async (userId?: string): Promise<DashboardData> => {
  try {
    const response = await axios.get<{ data: DashboardData }>(
      `${BASE_URL}/smartfactory/dashboards`,
      {
        params: { userId },
      }
    );
    return response.data.data;
  } catch (error: any) {
    console.error('Get Dashboards API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to retrieve dashboards');
  }
};

// API GET used to update user settings
export const updateUserSettings = async (
  userId: string,
  settings: UserSettings
): Promise<void> => {
  try {
    await axios.post(`${BASE_URL}/smartfactory/settings/${userId}`, settings);
  } catch (error: any) {
    console.error('Update User Settings API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to update settings');
  }
};

// API POST used to get user settings
export const getUserSettings = async (userId: string): Promise<UserSettings> => {
  try {
    const response = await axios.get<{ userSettings: UserSettings }>(
      `${BASE_URL}/smartfactory/settings/${userId}`
    );
    return response.data.userSettings;
  } catch (error: any) {
    console.error('Get User Settings API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to retrieve user settings');
  }
};

// API GET used to get alerts
export const getAlerts = async (userId: string): Promise<Alert[]> => {
  try {
    const response = await axios.get<{ data: Alert[] }>(
      `${BASE_URL}/smartfactory/alerts/${userId}`
    );
    return response.data.data;
  } catch (error: any) {
    console.error('Get Alerts API error:', error);
    throw new Error(error.response?.data?.message || 'Failed to retrieve alerts');
  }
};