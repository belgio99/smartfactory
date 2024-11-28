import {getMachineList} from "./PersistentDataManager";
import {KPI} from "./DataStructures";

const smoothData = (data: number[], alpha: number = 0.3): number[] => {
    const ema = [];
    ema[0] = data[0]; // Start with the first data point
    for (let i = 1; i < data.length; i++) {
        ema[i] = alpha * data[i] + (1 - alpha) * ema[i - 1]; // Exponential smoothing
    }
    return ema;
};

export class TimeFrame {
    from: Date;
    to: Date;

    constructor(from: Date, to: Date) {
        this.from = from;
        this.to = to;
    }

}

export const simulateChartData = async (kpi: KPI, timeFrame?: TimeFrame, type: string = "line", filters?: {
                                            site: string;
                                            productionLine: string;
                                            machines: string
                                        }
): Promise<any[]> => {
    console.log('Fetching data with:', {kpi, timeFrame, type, filters});

    let filteredData = getMachineList();

    if (filters) {
        // Apply site filter
        if (filters.site !== 'All') {
            filteredData = filteredData.filter((data) => data.site === filters.site);
        }

        // Apply production line filter
        if (filters.productionLine !== 'All') {
            filteredData = filteredData.filter((data) => data.line === filters.productionLine);
        }

        // Apply machine filter
        if (filters.machines !== 'All') {
            filteredData = filteredData.filter((data) => data.machineId === filters.machines);
        }
    }

    switch (type) {
        case 'radar':
            return filteredData.map((machine) => ({
                name: machine.machineId, // Label for the radar chart
                kpi1: Math.random() * 100,
                kpi2: Math.random() * 100,
                kpi3: Math.random() * 100,
                kpi4: Math.random() * 100,
            }));
        case 'line':
        case 'area': // Generate time-series data with applied filters
            const timeSeriesData = Array.from({length: 20}, (_, index) => {
                const timestamp = new Date(timeFrame ? timeFrame.from : Date.now() - index * 3600 * 1000).toISOString();
                const entry: any = {timestamp};
                const rawData = filteredData.map(() => Math.random() * 50);

                // Apply smoothing to the randomly generated data
                const smoothedData = smoothData(rawData);

                filteredData.forEach((machine, idx) => {
                    entry[machine.machineId] = smoothedData[idx]; // Apply smoothed values
                });
                return entry;
            });

            // Sort the time series data by timestamp
            const sortedTimeSeriesData = timeSeriesData.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

            return (sortedTimeSeriesData);
        default: // Generate categorical data with applied filters
            const categoricalData = filteredData.map((data) => ({
                name: data.machineId,
                value: Math.round(Math.random() * 100),
            }));

            return (categoricalData);
    }
};

