//in this file we store the temporary memory the data loaded from json and save to json the files for persistency
import {KPI, Machine, DashboardFolder, DashboardLayout} from "./DataStructures";
import axios from "axios";


export async function loadFromApi<T>(apiEndpoint: string, decoder: (json: Record<string, any>) => T): Promise<T[]> {
    try {
        const response = await axios.get(apiEndpoint);
        const jsonData: Record<string, any>[] = response.data;
        return jsonData.map(decoder);
    } catch (error) {
        console.error(`Error fetching or decoding data from ${apiEndpoint}:`, error);
        throw error;
    }
}

export async function sendToApi<T>(apiEndpoint: string, instance: T, encode: (instance: T) => Record<string, any>, method: 'POST' | 'PUT' = 'POST'
): Promise<void> {
    try {
        const json = encode(instance);
        if (method === 'PUT')
            await axios.put(apiEndpoint, json);
        else
            await axios.post(apiEndpoint, json);
    } catch (error) {
        console.error(`Error sending data to ${apiEndpoint}:`, error);
        throw error;
    }
}

export async function loadFromLocal<T>(filePath: string, decoder: (json: Record<string, any>) => T): Promise<T[]> {
    try {
        // Fetch the file (works in the frontend if the file is in the public folder)
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`Failed to load file: ${filePath}`);
        }

        // Parse the JSON content
        const jsonData: Record<string, any>[] = await response.json();
        // Decode the JSON into instances of T
        if (Array.isArray(jsonData)) {
            return jsonData.map(decoder);
        } else {
            return [decoder(jsonData)];
        }
    } catch (error) {
        console.error(`Error loading or decoding data from ${filePath}:`, error);
        throw error; // Re-throw error to handle it in the caller if necessary
    }
}

let KpiList: KPI[] = await loadFromLocal('/mockData/mock_kpi.json', KPI.decode);
let MachineList: Machine[] = await loadFromLocal('/mockData/machines.json', Machine.decode)
let Dashboards: (DashboardFolder | DashboardLayout)[] = await loadFromLocal('/mockData/dashboards.json', DashboardFolder.decode).then((dashboards) => {
        //extract root
        return dashboards[0].children;
    }
    , (error) => {
        console.error("Error loading dashboards", error);
        return [];
    });

export function getKpiList(): KPI[] {
    return KpiList;
}

export function getMachineList(): Machine[] {
    return MachineList;
}

export function encodeToJson<T>(instance: T, encode: (instance: T) => Record<string, any>): Record<string, any> {
    return encode(instance)
}

export function getDashboardList(): (DashboardFolder | DashboardLayout)[] {
    return Dashboards;
}

/**
 * Finds a dashboard by its ID, optionally within a specific folder.
 *
 * @param {string} dashboardId - The ID of the dashboard to find.
 * @param {string} [folderId] - The optional ID of the folder to search within.
 * @returns {DashboardLayout} - The found dashboard layout or a new empty dashboard layout if not found.
 */


export function findDashboardById(dashboardId: string, folderId?: string): DashboardLayout {

    console.log("Finding dashboard with id: ", dashboardId, "Folder: ", folderId);
    /*
    If folderId is provided and not equal to 'undefined', iterate through the Dashboards array.
    For each item, if it is an instance of DashboardFolder and its ID matches folderId, it further iterates through its children.
    If a child is an instance of DashboardLayout and its ID matches dashboardId, it returns that dashboard.
     */
    if (folderId !== 'undefined') {
        for (let folder of Dashboards) {
            if (folder instanceof DashboardFolder && folder.id === folderId) {
                for (let dashboard of folder.children) {
                    if (dashboard instanceof DashboardLayout && dashboard.id === dashboardId) {
                        return dashboard;
                    }
                }
            }
        }
    } else
    /*
    No Folder ID: If folderId is not provided or is 'undefined':
    It searches the Dashboards array for an item that is an instance of DashboardLayout and its ID matches dashboardId.
    If found, it returns that dashboard.
    */
    {
        let dashboard = Dashboards.find((d) => d instanceof DashboardLayout && d.id === dashboardId);
        if (dashboard instanceof DashboardLayout)
            return dashboard
    }

    // Return a new empty dashboard layout if not found
    return new DashboardLayout("notFound", "Error Layout", []);
}



