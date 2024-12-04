import axios from 'axios';

const BASE_URL = 'https://your-api-url.com'; // API URL

/**
 * Interface UserInfo
 * @param userId string - The user ID
 * @param username string - The username of the user
 * @param email string - The email of the user
 * @param role string - The role of the user
 * @param access_token string - The access token of the user
 * @param site string - The site of the user
 */
export interface UserInfo {
  userId: string;
  username: string;
  email: string;
  role: string;
  access_token?: string;
  site: string;
}

/**
 * Interface LoginResponse
 * @param outcome string - The outcome of the login
 * @param userInfo UserInfo - The user information [UserInfo] of the login
 * @param message string - The message of the login
 */
export interface LoginResponse {
  outcome: boolean;
  userInfo?: UserInfo;
  message?: string;
}


/**
 * Interface Report
 * @param id string - The ID of the report
 * @param title string - The title of the report
 * @param description string - The description of the report
 * @param createdAt string - The creation date of the report
 */
export interface Report {
  id: string;
  title: string;
  description: string;
  createdAt: string;
}

/**
 * Interface HistoricalDataResponse
 * @param any [key: string] any - The key of the historical data
 */
export interface HistoricalDataResponse {
  [key: string]: any; // 
}

/**
 * Interface DashboardData
 * @param any [key: string] any - The key of the dashboard data
 */
export interface DashboardData {
  [key: string]: any;
}

/**
 * Interface UserSettings
 * @param any [key: string] string | number | boolean - The key of the user settings
 */
export interface UserSettings {
  [key: string]: string | number | boolean;
}

/**
 * Interface Alert
 * @param alertId string - The alert ID
 * @param title string - The title of the alert
 * @param type string - The type of the alert
 * @param description string - The description of the alert
 * @param triggeredAt string - The trigger date of the alert
 * @param machineName string - The machine name of the alert
 * @param isPush boolean - The push notification of the alert
 * @param isEmail boolean - The email notification of the alert
 * @param recipients string[] - The recipients of the alert
 * @param severity string - The severity of the alert
 */
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

/**
 * Interface AIResponse
 * @param textResponse string - The text response of the AI
 * @param data string (optional) - The data of the AI
 */
interface AIResponse {
  textResponse: string;
  data?: string;
}

/**
 * Interface KPIObject
 * @param id string (optional) - The ID of the KPI
 * @param name string - The name of the KPI
 * @param description string - The description of the KPI
 * @param formula string - The formula of the KPI
 */
interface KPIObject {
  id?: string;
  name: string;
  description: string;
  formula: string;
}

/**
 * Interface KPIValue
 * @param value string - The value of the KPI
 */
interface KPIValue {
  value: string;
}

///
///
///
///
///

/**
  * API POST used to login
  * @param user string - Username or email of the user
  * @param isEmail boolean - Boolean to check if the user is an email
  * @param password string - Password of the user
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
 * @param username sring - Username of the user
 * @param email string - Email of the user
 * @param password string - Password of the user
 * @param role string - Role of the user
 * @param site string - The site where the user is
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
 * @param userId string - The user ID
 * @returns Promise will return the reports
 */
export const getReports = async (userId: string): Promise<Report[]> => {
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
 * @param query string[] - The query to get the historical data
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
 * @param userId string - The user ID
 * @returns Promise will return the dashboards
 */
export const getDashboards = async (userId: string): Promise<DashboardData> => {
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
 * @param userId string - The user ID
 * @param settings string - The user settings [key: string]: string | number | boolean
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
 * @param userId string - The user ID
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
 * @param userId string - The user ID
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

/**
 * API POST used to take the response of the AI
 * @param userInput string - The user input
 * @returns Promise will return the AI response
 */
export const interactWithAgent = async (userInput: string): Promise<{ textResponse: string; data?: string }> => {
  const response = await axios.post(`${BASE_URL}/smartfactory/agent`, { userInput });
  return response.data;
};

/**
 * API POST used to calculate the KPI
 * @param alert Alert - The alert to post
 * @returns Promise will return void
 */
export const postAlert = async (alert: Alert): Promise<void> => {
  await axios.post(`${BASE_URL}/smartfactory/postAlert`, alert);
};

/**
 * API POST used to get the KPIs
 * @returns KPIObject - Promise will return the KPIs
 */
export const retrieveKPIs = async (): Promise<KPIObject[]> => {
  const response = await axios.get<{ kpis: KPIObject[] }>(`${BASE_URL}/smartfactory/kpi`);
  return response.data.kpis;
};

/**
 * API GET used to calculate the KPI value
 * @param kpiId string - The KPI ID
 * @param machineId string (optional) - The machine ID
 * @param startTime string (optional) - The start time
 * @param endTime string (optional) - The end time
 * @returns KPIValue - The KPI value
 */
export const calculateKPIValue = async (kpiId: string, machineId?: string, startTime?: string, endTime?: string): Promise<KPIValue> => {
  const response = await axios.get<KPIValue>(`${BASE_URL}/smartfactory/${kpiId}/calculate`, {
    params: { machineId, startTime, endTime },
  });
  return response.data;
};

/**
 * API POST used to insert the KPI
 * @param kpi KPI - The KPI to insert
 * @returns string - Promise will return the KPI ID
 */
export const insertKPI = async (kpi: Omit<KPIObject, 'id'>): Promise<string> => {
  const response = await axios.post<{ kpiId: string }>(`${BASE_URL}/smartfactory/kpi`, { kpi });
  return response.data.kpiId;
};

/**
 * API POST used to update the Dashboard settings
 * @param userId string - The user ID
 * @param settings DashboardData - The dashboard settings
 * @returns Promise will return void
 */
export const postDashboardSettings = async (userId: string, settings: DashboardData): Promise<void> => {
  await axios.post(`${BASE_URL}/smartfactory/dashboardSettings/${userId}`, settings);
};

/**
 * API GET used to retrieve the Dashboard settings
 * @param userId string - The user ID
 * @returns Promise will return the dashboard settings
 */
export const retrieveDashboardSettings = async (userId: string): Promise<DashboardData> => {
  const response = await axios.get<DashboardData>(`${BASE_URL}/smartfactory/dashboardSettings/${userId}`);
  return response.data;
};