import {getMachineList} from "./PersistentDataManager";
import {KPI} from "./DataStructures";
import {Filter} from "../components/KpiSelector/FilterOptionsV2";
import {TimeFrame} from "../components/KpiSelector/TimeSelector";

const smoothData = (data: number[], alpha: number = 0.3): number[] => {
    const ema = [];
    ema[0] = data[0]; // Start with the first data point
    for (let i = 1; i < data.length; i++) {
        ema[i] = (alpha * data[i] + (1 - alpha) * ema[i - 1]); // Exponential smoothing
    }
    return ema;
};

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
            const from = timeFrame ? timeFrame.from : new Date(); // Default to the current date if not set
            const to = timeFrame ? timeFrame.to : new Date(); // Default to the current date if not set
            const aggregation = timeFrame?.aggregation || 'hours'; // Default aggregation to 'hours' if not specified
            // Helper function to add time units to a date
            const addTimeUnit = (date: Date, unit: string, value: number): Date => {
                const newDate = new Date(date);
                if (unit === 'days') newDate.setDate(newDate.getDate() + value);
                if (unit === 'months') newDate.setMonth(newDate.getMonth() + value);
                if (unit === 'hours') newDate.setHours(newDate.getHours() + value);
                return newDate;
            };
            const timeSeriesData = Array.from({length: 20}, (_, index) => {
                let timestamp = addTimeUnit(from, aggregation, index); // Calculate timestamp based on aggregation

                const entry: any = {timestamp: timestamp.toISOString()}; // Use the generated timestamp
                const rawData = filteredData.map(() => Math.random() * 50); // Simulate random data

                // Apply smoothing to the randomly generated data
                const smoothedData = smoothData(rawData);

                filteredData.forEach((machine, idx) => {
                    entry[machine.machineId] = smoothedData[idx]; // Apply smoothed values
                });

                return entry;
            });

            // Sort the time series data by timestamp
            return timeSeriesData.sort(
                (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
            );
        default: // Generate categorical data with applied filters
            const categoricalData = filteredData.map((data) => ({
                name: data.machineId,
                value: Math.round(Math.random() * 100),
            }));

            return (categoricalData);
    }
};

export const simulateChartData2 = async (
    kpi: KPI,
    timeFrame: TimeFrame,
    type: string = "line",
    filters?: Filter
): Promise<any[]> => {
    console.log("Fetching data with:", {kpi, timeFrame, type, filters});

    let filteredData = getMachineList();

    // Apply filters
    if (filters && filters.machineIds?.length) {
        filteredData = filteredData.filter((data) =>
            filters.machineIds?.includes(data.machineId)
        );
    } else if (filters && filters.machineType !== "All") {
        // Filter by machineType only if no machineIds are provided
        filteredData = filteredData.filter((data) => data.type === filters.machineType);
    } else {
        // Fetch all data when no filters are applied
        filteredData = getMachineList();
    }
    const timePeriods: string[] = [];

    const timeUnit = timeFrame.aggregation || getTimePeriodUnit(timeFrame);

    let startDate = new Date(timeFrame.from);
    if (timeUnit === 'hour') {
        // Split data by hours if the time frame is a single day
        for (let i = 0; i < timeFrame.to.getHours(); i++) {
            startDate.setHours(i, 0, 0, 0); // set to the hour of the day
            timePeriods.push(startDate.toISOString());
        }
    } else if (timeUnit === 'day') {
        // Split by days for week/month timeframes
        const endDate = timeFrame.to;
        while (startDate <= endDate) {
            timePeriods.push(startDate.toISOString());
            startDate.setDate(startDate.getDate() + 1);
        }
    } else if (timeUnit === 'month') {
        // Split by months for a year-long time period
        for (let i = 0; i < timeFrame.to.getMonth(); i++) {
            const period = new Date(startDate);
            period.setMonth(i);
            timePeriods.push(period.toISOString());
        }
    }

    switch (type) {
        case "line":
        case "scatter":
        case 'area': // Generate time-series data with applied filters
            // Default aggregation to 'hour' if not specified
            return timePeriods.map((period, index) => {
                const entry: any = {timestamp: period};

                // Simulate raw data
                const rawData = filteredData.map(() => Math.random() * 50);

                // Apply smoothing to the randomly generated data
                const smoothedData = smoothData(rawData);

                filteredData.forEach((machine, idx) => {
                    entry[machine.machineId] = smoothedData[idx]; // Apply smoothed values
                });

                return entry;
            });
        case "barv":
        case "barh":
        case "pie":
            // Generate categorical data
            return filteredData.map((data) => ({
                name: data.machineId,
                value: Math.round(Math.random() * 100),
            }));

        case "donut":
            // Generate categorical data, and add the total for the donut chart
            const donutData = filteredData.map((data) => ({
                name: data.machineId,
                value: Math.round(Math.random() * 100),
            }));
            donutData.push({name: "Total", value: donutData.reduce((acc, cur) => acc + cur.value, 0)});
            return donutData;
        case "heatmap":
        case "stacked_bar":
            // Generate periods based on the timeframe
            return timePeriods.map((period) => {
                const entry: any = {timestamp: period};
                filteredData.forEach((machine) => {
                    entry[machine.machineId] = Math.round(Math.random() * 100); // Random value for each machine
                });
                return entry;
            });

        case "hist":
            // Generate histogram bins using sturges's formula
            const binSize = Math.ceil(Math.log2(filteredData.length) + 1);
            return Array.from({length: 10}, (_, i) => ({
                bin: `${i * binSize}-${(i + 1) * binSize}`,
                value: Math.round(Math.random() * 50),
            }));
        /*
    case "scatter":
        const timeSeries = Array.from({length: 20}, (_, index) => {
            return new Date(timeFrame ? timeFrame.from : Date.now() - index * 3600 * 1000).toISOString();
        });

        // Scatter data will include values over time for each machine
        return filteredData.flatMap((machine) =>
            timeSeries.map((timestamp) => ({
                timestamp,                  // Time for this data point
                machineId: machine.machineId, // Machine associated with the data point
                value: Math.random() * 100, // Random value
            }))
        );

    case "heatmap":
        if (filters?.machineType !== "All" && filters?.machineType) {
            // Group by machine type
            const machineTypeData = filteredData
                .filter((machine) => machine.type === filters.machineType)
                .reduce((acc: any, machine) => {
                    for (let i = 0; i < 10; i++) {
                        const timeSlot = `Hour ${i + 1}`;
                        acc[timeSlot] = acc[timeSlot] || {time: timeSlot};
                        acc[timeSlot][machine.type] = (acc[timeSlot][machine.type] || 0) +
                            Math.round(Math.random() * 100);
                    }
                    return acc;
                }, {});

            return Object.values(machineTypeData); // Return grouped data
        } else {
            // Group KPI values by machine and time
            const timeSlots = Array.from({length: 10}, (_, i) => `Hour ${i + 1}`);
            return filteredData.flatMap((machine) =>
                timeSlots.map((timeSlot) => ({
                    machine: machine.machineId,
                    time: timeSlot,
                    value: Math.round(Math.random() * 100),
                }))
            );
        }*/

        default:
            throw new Error(`Unsupported chart type: ${type}`);
    }
};


// Function to get time unit (hours, days, months) based on TimeFrame's `from` and `to` values
const getTimePeriodUnit = (timeFrame: TimeFrame): string => {
    const diffTime = timeFrame.to.getTime() - timeFrame.from.getTime(); // Difference in milliseconds
    const diffDays = diffTime / (1000 * 3600 * 24); // Convert to days

    if (diffDays < 1) {
        return 'hours'; // If less than a day, group by hours
    } else if (diffDays < 7) {
        return 'days'; // If within a week, group by days
    } else if (diffDays < 30) {
        return 'days'; // If within a month, group by days
    } else {
        return 'months'; // If more than a month, group by months
    }
};


