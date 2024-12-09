//in this file we store the temporary memory the data loaded from json and save to json the files for persistency
import {DashboardFolder, DashboardLayout, KPI, Machine} from "./DataStructures";
import axios from "axios";
import EventEmitter from "events";

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

type DataManagerChangeCallback = () => void;

// DataManager.ts
class DataManager {
    static instance: DataManager | null = null;

    private kpiList: KPI[] = [];
    private machineList: Machine[] = [];
    private dashboards: (DashboardFolder | DashboardLayout)[] = [];
    events = new EventEmitter();

    private constructor() {
    } // Prevent external instantiation

    static getInstance(): DataManager {
        if (!DataManager.instance) {
            DataManager.instance = new DataManager();
        }
        return DataManager.instance;
    }

    async initialize(): Promise<void> {
        try {
            this.kpiList = await loadFromLocal('/mockData/kpis.json', KPI.decodeGroups).then(
                kpiToUnwrap => kpiToUnwrap[0] || [],
                error => {
                    console.error("Error loading kpis:", error);
                    return [];
                }
            );

            this.machineList = await loadFromLocal('/mockData/machines.json', Machine.decodeGroups).then(
                kpiToUnwrap => kpiToUnwrap[0] || [],
                error => {
                    console.error("Error loading kpis:", error);
                    return [];
                }
            );

            this.dashboards = await loadFromLocal('/mockData/dashboards.json', DashboardFolder.decode).then(
                dashboards => dashboards[0]?.children || [],
                error => {
                    console.error("Error loading dashboards:", error);
                    return [];
                }
            );
        } catch (error) {
            console.error("Error during initialization:", error);
            throw error;
        }
    }

    getKpiList(): KPI[] {
        return this.kpiList;
    }

    getMachineList(): Machine[] {
        return this.machineList;
    }

    getDashboards(): (DashboardFolder | DashboardLayout)[] {
        return this.dashboards;
    }

    subscribe(callback: DataManagerChangeCallback) {
        this.events.on('change', callback);
    }

    unsubscribe(callback: DataManagerChangeCallback) {
        this.events.off('change', callback);
    }

    /**
     * Invalidates all data caches by re-initializing the data manager.
     */
    invalidateCaches(): void {
        // make a copy of the current instance
        let instance = DataManager.instance;
        this.initialize().then(r => console.log("Data caches invalidated."), e => {
            console.error("Error invalidating caches:", e);
            console.error("Reverting to previous instance.");
            DataManager.instance = instance;
        });
    }

    /**
     * Finds a dashboard by its ID, optionally within a specific folder.
     *
     * @param {string} dashboardId - The ID of the dashboard to find.
     * @param {string} [folderId] - The optional ID of the folder to search within.
     * @returns {DashboardLayout} - The found dashboard layout or a new empty dashboard layout if not found.
     */
    findDashboardById(dashboardId: string, folderId?: string): DashboardLayout {

        console.log("Finding dashboard with id: ", dashboardId, "Folder: ", folderId);
        /*
        If folderId is provided and not equal to 'undefined', iterate through the Dashboards array.
        For each item, if it is an instance of DashboardFolder and its ID matches folderId, it further iterates through its children.
        If a child is an instance of DashboardLayout and its ID matches dashboardId, it returns that dashboard.
         */
        if (folderId !== 'undefined') {
            for (let folder of this.dashboards) {
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
            let dashboard = this.dashboards.find((d) => d instanceof DashboardLayout && d.id === dashboardId);
            if (dashboard instanceof DashboardLayout)
                return dashboard
        }

        // Return a new empty dashboard layout if not found
        return new DashboardLayout("notFound", "Error Layout", []);
    }

    /**
     * Adds a new dashboard to the data manager.
     * @param dashboard
     * @param dashboardFolder
     */
    addDashboard(dashboard: DashboardLayout, dashboardFolder: DashboardFolder): void {
        // locate the folder
        const folder = this.dashboards.find((d) => d.id === dashboardFolder.id);

        // if the folder is found, add the dashboard to its children
        if (folder instanceof DashboardFolder) {
            folder.children.push(dashboard);
        } else {
            // otherwise, add the new folder to the root level
            dashboardFolder.children.push(dashboard);
            this.dashboards.push(dashboardFolder);
        }

        console.log("Dashboard added: ", dashboard, dashboardFolder);
        console.log("New dashboard tree: ", this.dashboards);
        // api call to save the new dashboard tree structure
        const json = DashboardFolder.encodeTree(this.dashboards);

        this.events.emit('change');
    }

}

export default DataManager;



