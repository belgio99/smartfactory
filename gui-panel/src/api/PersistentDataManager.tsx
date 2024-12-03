//in this file we store the temporary memory the data loaded from json and save to json the files for persistency
import {KPI, Machine} from "./DataStructures";
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
        return jsonData.map(decoder);
    } catch (error) {
        console.error(`Error loading or decoding data from ${filePath}:`, error);
        throw error; // Re-throw error to handle it in the caller if necessary
    }
}

let KpiList: KPI[] = await loadFromLocal('/mockData/kpis.json', KPI.decode);
let MachineList: Machine[] = await loadFromLocal('/mockData/machines.json', Machine.decode)

export function getKpiList(): KPI[] {
    return KpiList;
}

export function getMachineList(): Machine[] {
    return MachineList;
}

export function encodeToJson<T>(instance: T, encode: (instance: T) => Record<string, any>): Record<string, any> {
    return encode(instance)
}



