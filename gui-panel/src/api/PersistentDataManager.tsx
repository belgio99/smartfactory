//in this file we store the temporary memory the data loaded from json and save to json the files for persistency
import {KPI, Machine} from "./DataStructures";

export async function loadFrom<T>(filePath: string, decoder: (json: Record<string, any>) => T): Promise<T[]> {
    try {
        // Fetch the file (works in the frontend if the file is in the public folder)
        const response = await fetch(filePath);
        if (!response.ok) {
            throw new Error(`Failed to load file: ${filePath}`);
        }

        // Parse the JSON content
        const jsonData: Record<string, any>[] = await response.json();

        // Decode the JSON into instances of T
        return jsonData.map(decoder);
    } catch (error) {
        console.error(`Error loading or decoding data from ${filePath}:`, error);
        throw error; // Re-throw error to handle it in the caller if necessary
    }
}

let KpiList: KPI[] = await loadFrom('/mockData/kpis.json', KPI.decode);
let MachineList: Machine[] = await loadFrom('/mockData/machines.json', Machine.decode)

export function getKpiList(): KPI[] {
    return KpiList;
}
export function getMachineList(): Machine[] {
    return MachineList;
}

export function encodeToJson<T>(instance: T, encode: (instance: T) => Record<string, any>): Record<string, any> {
    return encode(instance)
}



