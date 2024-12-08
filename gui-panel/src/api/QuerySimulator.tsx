import PersistentDataManager from "./PersistentDataManager";
import {KPI, Machine} from "./DataStructures";
import {Filter} from "../components/Selectors/FilterOptions";
import {TimeFrame} from "../components/Selectors/TimeSelect";

const dataManager = PersistentDataManager.getInstance();
const smoothData = (data: number[], alpha: number = 0.3): number[] => {
    const ema = [];
    ema[0] = data[0]; // Start with the first data point
    for (let i = 1; i < data.length; i++) {
        ema[i] = (alpha * data[i] + (1 - alpha) * ema[i - 1]); // Exponential smoothing
    }
    return ema;
};
export const simulateChartData = async (
    kpi: KPI,
    timeFrame: TimeFrame,
    type: string = "line",
    filters?: Filter
): Promise<any[]> => {
    console.log("Fetching data with:", {kpi, timeFrame, type, filters});
    let query = constructQuery(type, kpi, timeFrame, filters);
    console.log("Constructed query json: ", query);
    console.log("Constructed query: ", convertJsonToSql(query));
    const unfilteredData = dataManager.getMachineList();
    let filteredData: Machine[];
    // Apply filters
    if (filters && filters.machineIds?.length) {
        filteredData = unfilteredData.filter((data) =>
            filters.machineIds?.includes(data.machineId)
        );
    } else if (filters && filters.machineType !== "All") {
        // Filter by machineType only if no machineIds are provided
        filteredData = unfilteredData.filter((data) => data.type === filters.machineType);
    } else {
        // Fetch all data when no filters are applied
        filteredData = unfilteredData
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
    } else if (timeUnit === 'week') {
        const endDate = timeFrame.to;
        let currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            timePeriods.push(currentDate.toISOString());
            currentDate.setDate(currentDate.getDate() + 7); // Increment by 7 days for each week
        }
    } else if (timeUnit === 'month') {
        const endDate = timeFrame.to;
        let currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            timePeriods.push(currentDate.toISOString());
            currentDate.setMonth(currentDate.getMonth() + 1); // Increment by 1 month
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

///////////////////////////////////////////////////////////////
const constructQuery = (
    graph_type: string,
    kpi: KPI,
    timeFrame: TimeFrame,
    filters?: Filter
): object => {
    // Get the list of machines from filters or default to all available
    const machineList: string[] = filters?.machineIds
        ? filters.machineIds
        : dataManager.getMachineList().map(machine => machine.machineId);

    const timeFrameCopy: TimeFrame = {
        from: new Date(timeFrame.from),
        to: new Date(timeFrame.to),
        aggregation: timeFrame.aggregation,
    }
    // set the month of the timeframe to be betweeen 3 and 10, try to keep the same difference if possible
    const diff = timeFrame.to.getMonth() - timeFrame.from.getMonth();
    timeFrameCopy.from.setMonth(3);
    timeFrameCopy.to.setMonth(Math.min(3 + diff, 10));

    timeFrame = timeFrameCopy;
    // Format dates to `yyyy-mm-dd`
    const from: string = timeFrame.from.toISOString().split('T')[0];
    const to: string = timeFrame.to.toISOString().split('T')[0];

    // Calculate the duration of the timeframe in days
    const durationInDays = Math.ceil(
        (timeFrame.to.getTime() - timeFrame.from.getTime()) / (1000 * 60 * 60 * 24)
    );

    // Dynamically determine time grouping based on duration
    let timeGrouping: string = "day"; // Default to day
    if (durationInDays <= 1) {
        timeGrouping = "hour"; // For a single day, group by hour
    } else if (durationInDays <= 31) {
        timeGrouping = "day"; // For up to a month, group by day
    } else if (durationInDays <= 365) {
        timeGrouping = "month"; // For up to a year, group by month
    } else {
        timeGrouping = "year"; // For periods longer than a year, group by year
    }

    // Define grouping logic based on graph type
    let groupBy: { time: string | null; category: string | null } = {time: null, category: null};
    switch (graph_type) {
        case "line":
        case "scatter":
        case "area":
            groupBy.time = timeGrouping; // Use dynamically determined time grouping
            break;

        case "barv":
        case "barh":
        case "stacked_bar":
            groupBy.time = timeGrouping; // Use dynamically determined time grouping
            break;

        case "hist":
        case "pie":
        case "donut":
            groupBy.time = null; // No time grouping for pie/donut charts
            break;

        default:
            throw new Error(`Unsupported graph type: ${graph_type}`);
    }

    // Construct the query JSON
    return {
        kpi: kpi.id, // Use the KPI ID
        timeframe: {
            start_date: from,
            end_date: to,
        },
        machines: machineList, // List of machine IDs
        group_by: timeGrouping, // Grouping logic
    };
};

const convertJsonToSql = (query: any): string => {
    // Destructure the query object
    const {kpi, timeframe, machines, group_by} = query;

    const getKpiAndAggregationMethod = (kpi: string) => {
        // Define the list of known aggregation methods
        const aggregationMethods = ['avg', 'sum', 'max'];

        // Check if the kpi ends with one of the aggregation methods
        for (const method of aggregationMethods) {
            if (kpi.endsWith(`_${method}`)) {
                // If it ends with one of the aggregation methods, split at the last underscore
                const kpiName = kpi.substring(0, kpi.lastIndexOf(`_${method}`));
                return {kpiName, aggMethod: method};
            }
        }

        // If no aggregation method is found, return the kpi as is and undefined for aggMethod
        return {kpiName: kpi, aggMethod: undefined};
    };

    const {kpiName, aggMethod} = getKpiAndAggregationMethod(kpi);

    // Base SELECT statement
    let sql = `SELECT `;

    // Add time grouping if specified
    if (group_by.time) {
        sql += `DATE_TRUNC('${group_by.time}', __time) AS time_period, `;
    }

    // Add grouping by machine name
    sql += `name, `;


    // Add aggregation field with alias (e.g., consumption_avg -> consumption_avg)
    if (aggMethod) {
        sql += `SUM("${aggMethod}") AS ${kpi}`;
    }

    // FROM clause
    sql += ` FROM "timeseries"`;

    // WHERE conditions
    const whereConditions = [];
    if (timeframe.start_date && timeframe.end_date) {
        whereConditions.push(
            `__time BETWEEN '${timeframe.start_date}' AND '${timeframe.end_date}'`
        );
    }
    if (machines && machines.length > 0) {
        whereConditions.push(`name IN ('${machines.join("', '")}')`);
    }
    if (kpi) {
        whereConditions.push(`kpi = '${kpiName || ""}'`);
    }

    if (whereConditions.length > 0) {
        sql += ` WHERE ` + whereConditions.join(" AND ");
    }

    // GROUP BY clause
    const groupByFields = [];
    if (group_by) {
        groupByFields.push(`DATE_TRUNC('${group_by}', __time)`);
    }

    groupByFields.push(group_by.category);

    if (groupByFields.length > 0) {
        sql += ` GROUP BY ` + groupByFields.join(", ");
    }

    // Add ORDER BY clause for time series
    if (group_by.time) {
        sql += ` ORDER BY time_period`;
    }

    // Return the constructed SQL query
    return sql;
};
