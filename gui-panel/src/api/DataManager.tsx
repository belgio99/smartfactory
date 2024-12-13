//in this file we store the temporary memory the data loaded from json and save to json the files for persistency
import {DashboardFolder, DashboardLayout, KPI, Machine} from "./DataStructures";
import axios from "axios";
import EventEmitter from "events";
import {dummyCheck, retrieveKPIs, retrieveMachines} from "./ApiService";

// API
import {postDashboardSettings} from "./ApiService";
import {retrieveDashboardSettings} from "./ApiService";

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
    private userId: string | null = null;

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

    setUserId(userId: string): void {
        this.userId = userId;
    }

    async initialize(): Promise<void> {
        let ping = true;
        try {
            //try to connect  to dummy, if it fails, load from local
            await dummyCheck();
            console.log("Ping to dummy successful.");
        } catch (error) {
            console.error("Error connecting to dummy:", error);
            ping = false;
        }
        try {
            // Load local dashboards
            let localDashboards = await loadFromLocal('/mockData/dashboards.json', DashboardFolder.decode).then(
                dashboards => dashboards[0]?.children || [],
                error => {
                    console.error("Error loading local dashboards:", error);
                    return [];
                }
            );

            if (ping) {
                this.kpiList = await retrieveKPIs();
                this.machineList = await retrieveMachines();
                // Load user-specific dashboards from the API
                // Check if the user is logged in
                if (this.userId) {
                    console.log("User logged in: retrieving user dashboards from server...");
                    try {
                        const serverData = await retrieveDashboardSettings(this.userId);
                        const serverDashboards = serverData.dashboards || [];

                        // Merge local and server dashboards
                        const mergedDashboards = mergeDashboards(localDashboards, serverDashboards);
                        this.dashboards = mergedDashboards;
                        console.log("Merged dashboards:", mergedDashboards);
                    } catch (error) {
                        console.error("Error retrieving user dashboards from server:", error);
                        // If there is an error, use only local dashboards
                        this.dashboards = localDashboards;
                    }
                } else {
                    // No user logged in: use only local dashboards
                    this.dashboards = localDashboards;
                }
            } else {

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
            }

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
     * Set the unique ID for a dashboard.
     * @param dashboardId string - The ID of the dashboard to check.
     * @returns string - The unique ID for the dashboard.
     * @note Function to get if that dashboard id exists:
     *          -   If yes return the same id with _1 appended or more if needed;
     *          -   If not return the same id;
     */
    getUniqueDashboardId(dashboardId: string): string {
        let newId = dashboardId;
        let i = 1;

        // Controlla se l'ID esiste già tra le dashboard
        while (this.dashboards.some((d) => d.id === newId)) {
            newId = `${dashboardId}_${i}`; // Aggiunge un suffisso numerico
            i++;
        }

        return newId;
    }

    /**
     * Search a Dashboard folder with same name in the dashboard list.
     * If found return the folder, otherwise return null.
     */
    findDashboardFolderByName(name: string): DashboardFolder | null {
        return this.dashboards.find((d) => d instanceof DashboardFolder && d.name === name) as DashboardFolder || null;
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

    /** Take all dashoboards folder and return a list of this folders
     * @returns DashboardFolder[] - The list of dashboard folders.
     */
    getDashboardFolders(): DashboardFolder[] {
        return this.dashboards.filter((d) => d instanceof DashboardFolder) as DashboardFolder[];
    }

    /**
     * Add a new dashboard folder to the data manager.
     * @param name string - The name of the new folder.
     * @note The new folder is added to the root level of the dashboard tree.
     */
    addDashboardFolder(name: string): void {
        // Create a new folder
        const newFolder = new DashboardFolder(this.getUniqueDashboardId(name), name, []);
        // Add the folder to the root level
        this.dashboards.push(newFolder);

        console.log("Folder added: ", newFolder);
        console.log("New dashboard tree: ", this.dashboards);
        // API call to save the new dashboard
        const json = DashboardFolder.encodeTree(this.dashboards);
        // If the user is logged in, save the dashboard to the server
        if (this.userId) {
            postDashboardSettings(this.userId, json);
        }
        this.events.emit('change');
    }

    /**
     * Adds a new dashboard to the data manager.
     * @param dashboard DashboardLayout - The dashboard to add.
     * @param dashboardFolder DashboardFolder - The folder to add the dashboard to.
     * @param userId string - The ID of the user who owns the dashboard.
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
        // API call to save the new dashboard
        const json = DashboardFolder.encodeTree(this.dashboards);
        // If the user is logged in, save the dashboard to the server
        if (this.userId) {
            postDashboardSettings(this.userId, json);
        }
        this.events.emit('change');
    }

}

// POLICY FOR MERGING DASHBOARDS
////////////////////////////////////////////////////////////////////////////////
//////////////////////////
/**
 * This function merges local and server dashboards, giving priority to the server version in case of conflicts.
 * @param localDashboards DashboardFolder[] | DashboardLayout[] - The local dashboards to merge.
 * @param serverDashboards DashboardFolder[] | DashboardLayout[] - The server dashboards to merge.
 * @returns (DashboardFolder | DashboardLayout)[] - The merged dashboards.
 */
function mergeDashboards(
    localDashboards: (DashboardFolder | DashboardLayout)[],
    serverDashboards: (DashboardFolder | DashboardLayout)[]): (DashboardFolder | DashboardLayout)[] {

    // Convert the arrays to maps for easier lookup
    const localMap = new Map(localDashboards.map(d => [d.id, d]));
    const serverMap = new Map(serverDashboards.map(d => [d.id, d]));

    const merged: (DashboardFolder | DashboardLayout)[] = [];

    // Merge the two maps by Key (ID)
    const allIds = new Set([...localMap.keys(), ...serverMap.keys()]);

    for (const id of allIds) {
        const localItem = localMap.get(id);
        const serverItem = serverMap.get(id);

        if (serverItem && localItem) {
            // If both are present, merge them giving priority to the server version
            merged.push(mergeSingleItem(localItem, serverItem));
        } else if (serverItem && !localItem) {
            // Only server
            merged.push(serverItem);
        } else if (!serverItem && localItem) {
            // Only local
            merged.push(localItem);
        }
    }

    // Sort the merged array by name
    // merged.sort((a,b)=>a.name.localeCompare(b.name));

    return merged;
}

/**
 * This function merges a single dashboard or layout, giving priority to the server version in case of conflicts.
 * @param localItem DashboardFolder | DashboardLayout - The local dashboard or layout to merge.
 * @param serverItem DashboardFolder | DashboardLayout - The server dashboard or layout to merge.
 * @returns serverItem DashboardFolder | DashboardLayout - The merged item.
 */
function mergeSingleItem(
    localItem: DashboardFolder | DashboardLayout,
    serverItem: DashboardFolder | DashboardLayout): DashboardFolder | DashboardLayout {
    // If both are folders, merge recursively the children
    if (localItem instanceof DashboardFolder && serverItem instanceof DashboardFolder) {
        // Merge children
        const mergedChildren = mergeDashboards(localItem.children, serverItem.children);
        return new DashboardFolder(serverItem.id, serverItem.name, mergedChildren);
    }

    // If both are layouts, return the server layout
    return serverItem;
}

export default DataManager;



