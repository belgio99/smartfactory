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

/**
  * API POST used to login
  * @param user - Username or email of the user
  * @param isEmail - Boolean to check if the user is an email
  * @param password - Password of the user
  * @returns Promise will return the login response
 */
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

/**
 * API POST used to register a new user
 * @param username - Username of the user
 * @param email - Email of the user
 * @param password - Password of the user
 * @param role - Role of the user
 * @param site - The site where the user is
 * @returns userInfo - The user information
 */
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

/**
 * API GET used to get reports
 * @param userId - The user ID
 * @returns Promise will return the reports
 */
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

/**
 * API GET used to get historical data
 * @param query - The query to get the historical data
 * @returns Promise will return the historical data
 */
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

/**
 * API GET used to get dashboards
 * @param userId - The user ID
 * @returns Promise will return the dashboards
 */
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

/**
 * API POST used to update user settings
 * @param userId - The user ID
 * @param settings - The user settings [key: string]: string | number | boolean
 * @returns Promise will return void
 */
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

/**
 * API GET used to get user settings
 * @param userId - The user ID
 * @returns Promise will return the user settings [key: string]: string | number | boolean
 */
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

/**
 * API GET used to get alerts
 * @param userId - The user ID
 * @returns Promise will return the alerts [key: string]: string | number | boolean
 */
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