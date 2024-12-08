import axios from 'axios';

const BASE_URL = '/api'; // API URL
//const BASE_URL = 'http://0.0.0.0:10040'; // API URL
const API_KEY = '111c50cc-6b03-4c01-9d2f-aac6b661b716'; // API KEY


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

/**
 * Interface ScheduleRequest
 * @param userId string - The ID of the user scheduling the report
 * @param params ScheduleParams - Additional parameters for the report
 * @param period number - The scheduling frequency
 * @param startDate string - The start date of the report
 * @param email string - The email of the report
 * @param kpis string[] - The KPIs of the report
 * @param machines string[] - The machines of the report
 */
interface ScheduleParams {
    id: string;
    status: boolean;
    name: string;
    recurrence: string;  // es: "Daily", "Weekly", ecc.
    startDate: string;   // es: "2024-12-10T00:00:00Z"
    email: string;
    kpis: string[];
    machines: string[];
}

/**
 * Interface ScheduleRequest
 * @param user_id string - The ID of the user scheduling the report
 * @param params ScheduleParams - Additional parameters for the report
 */
interface ScheduleRequest {
    user_id?: string;
    params: ScheduleParams;
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
): Promise<UserInfo> => {
    try {
        console.log('Sending login request to:', `${BASE_URL}/smartfactory/login`);
        console.log('Payload:', {user, isEmail, password});
        console.log('Headers:', {"x-api-key": API_KEY});

        const response = await axios.post<UserInfo>(
            `${BASE_URL}/smartfactory/login`,
            {
                user,
                isEmail,
                password,
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );

        console.log('Login response:', response.data);
        return response.data;
    } catch (error: any) {
        console.error('Login API error:', error.response || error.message);
        throw new Error(error.response?.data?.message || 'Login failed, couldn\'t reach the server');
    }
};


/**
 * API POST used to register a new user
 * @param username string - Username of the user
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
): Promise<UserInfo> => {
    try {
        const response = await axios.post<UserInfo>(
            `${BASE_URL}/smartfactory/register`,
            {
                username,
                email,
                password,
                role,
                site,
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data;
    } catch (error: any) {
        console.error('Register API error:', error);
        throw new Error(error.response?.data?.message || "Couldn't reach the server");
    }
};

/**
 * API POST used to change the password of the user
 * @param userId string - The user ID
 * @param oldPassword string - The old password of the user
 * @param newPassword string - The new password of the user
 * @returns UserInfo - The user information
 */
export const changePassword = async (
    userId: string,
    oldPassword: string,
    newPassword: string
): Promise<UserInfo> => {
    try {
        const response = await axios.put<UserInfo>(
            `${BASE_URL}/smartfactory/user/${userId}`,
            {
                old_password: oldPassword,
                new_password: newPassword
            },
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                }
            }
        );
        return response.data;
    } catch (error: any) {
        console.error('Change Password API error:', error);
        throw new Error(error.response?.data?.message || 'Change Password failed');
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
                params: {userId},
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
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
 * @param query string - Json to be converted into a query on the api layer
 * @returns Promise will return the requested historical data from the database
 */
export const getHistoricalData = async (query: string): Promise<HistoricalDataResponse> => {
    try {
        const response = await axios.get<{ data: HistoricalDataResponse }>(
            `${BASE_URL}/smartfactory/historical`,
            {
                params: {query},
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
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
                params: {userId},
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
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
        await axios.post(
            `${BASE_URL}/smartfactory/settings/${userId}`,
            settings,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
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
            `${BASE_URL}/smartfactory/settings/${userId}`,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
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
            `${BASE_URL}/smartfactory/alerts/${userId}`,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data.data;
    } catch (error: any) {
        console.error('Get Alerts API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to retrieve alerts');
    }
};

/**
 * API POST used to take the response of the AI
 * @param userId string - The user ID
 * @param userInput string - The user input
 * @returns Promise will return the AI response
 */
export const interactWithAgent = async (userId: string, userInput: string): Promise<{
    textResponse: string;
    textExplanation: string,
    data?: string,
    label?: string
}> => {
    try {
        const response = await axios.post(
            `${BASE_URL}/smartfactory/agent/${userId}`,
            {userInput},
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data;
    } catch (error: any) {
        console.error('Interact With Agent API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to interact with agent');
    }
};

/**
 * API POST used to get the KPIs
 * @returns KPIObject - Promise will return the KPIs
 */
export const retrieveKPIs = async (): Promise<KPIObject[]> => {
    try {
        const response = await axios.get<{ kpis: KPIObject[] }>(
            `${BASE_URL}/smartfactory/kpi`,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data.kpis;
    } catch (error: any) {
        console.error('Retrieve KPIs API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to retrieve KPIs');
    }
};

/**
 * API GET used to calculate the KPI value
 * @param kpiId string - The KPI ID
 * @param machineId string (optional) - The machine ID
 * @param startTime string (optional) - The start time
 * @param endTime string (optional) - The end time
 * @returns KPIValue - The KPI value
 */
export const calculateKPIValue = async (
    kpiId: string,
    machineId?: string,
    startTime?: string,
    endTime?: string
): Promise<KPIValue> => {
    try {
        const response = await axios.get<KPIValue>(
            `${BASE_URL}/smartfactory/${kpiId}/calculate`,
            {
                params: {machineId, startTime, endTime},
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data;
    } catch (error: any) {
        console.error('Calculate KPI Value API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to calculate KPI value');
    }
};

/**
 * API POST used to insert the KPI
 * @param kpi KPI - The KPI to insert
 * @returns string - Promise will return the KPI ID
 */
export const insertKPI = async (kpi: Omit<KPIObject, 'id'>): Promise<string> => {
    try {
        const response = await axios.post<{ kpiId: string }>(
            `${BASE_URL}/smartfactory/kpi`,
            {kpi},
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data.kpiId;
    } catch (error: any) {
        console.error('Insert KPI API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to insert KPI');
    }
};

/**
 * API POST used to update the Dashboard settings
 * @param userId string - The user ID
 * @param settings DashboardData - The dashboard settings
 * @returns Promise will return void
 */
export const postDashboardSettings = async (userId: string, settings: DashboardData): Promise<void> => {
    try {
        await axios.post(
            `${BASE_URL}/smartfactory/dashboardSettings/${userId}`,
            settings,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
    } catch (error: any) {
        console.error('Post Dashboard Settings API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to post dashboard settings');
    }
};

/**
 * API GET used to retrieve the Dashboard settings
 * @param userId string - The user ID
 * @returns Promise will return the dashboard settings
 */
export const retrieveDashboardSettings = async (userId: string): Promise<DashboardData> => {
    try {
        const response = await axios.get<DashboardData>(
            `${BASE_URL}/smartfactory/dashboardSettings/${userId}`,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
        return response.data;
    } catch (error: any) {
        console.error('Retrieve Dashboard Settings API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to retrieve dashboard settings');
    }
};

/**
 * API POST used to schedule a report generation.
 * @param userId string - The ID of the user scheduling the report.
 * @param params object - Additional parameters for the report (e.g., name, type, site, email, startDate, kpis, machines).
 * @param period number - The scheduling frequency (e.g., in seconds).
 * @returns Promise<void> - No specific return value, just a confirmation of scheduling.
 */
export const scheduleReport = async (requestData: ScheduleRequest): Promise<any> => {
    try {
        const response = await axios.post(
            `${BASE_URL}/smartfactory/reports/schedule`,
            requestData,
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );

        return response.data;

    } catch (error: any) {
        console.error('Error to create the schedule API:', error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'Error to create the schedule');
    }
};

/**
 * API GET used to get the scheduled reports
 * @param reportId string - The ID of the report
 * @returns Promise<Report[]> - The list of scheduled reports
 */
export const downloadReport = async (reportId: string): Promise<Blob> => {
    try {
        const response = await axios.get(`${BASE_URL}/smartfactory/reports/download/${reportId}`, {
            headers: {
                'x-api-key': API_KEY,
            },
            responseType: 'blob', // Specify the response type as Blob (binary data)
        });

        return response.data; // Return the bob for pdf file
    } catch (error: any) {
        console.error('Error downloading the report:', error.response?.data || error.message);
        throw new Error(error.response?.data?.message || 'Failed to download the report');
    }
};


/**
 * API POST used to logout
 * @param userId string - The user ID
 */
export const logout = async (userId: string): Promise<void> => {
    try {
        await axios.post(
            `${BASE_URL}/smartfactory/logout?userId=${userId}`,
            {}, // Nessun body richiesto
            {
                headers: {
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            }
        );
    } catch (error: any) {
        console.error('Logout API error:', error);
        throw new Error(error.response?.data?.message || 'Failed to logout');
    }
};