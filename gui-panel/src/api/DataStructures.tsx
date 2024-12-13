//in this file we define the data structures and their json encode/decode methods for persistency and api communication

export class Machine {
    machineId: string;
    line?: string;
    site?: string;
    type: string;
    description?: string;

    constructor(machineId: string, type: string, description: string, site?: string, line?: string) {
        this.machineId = machineId;
        if (line) this.site = site;
        if (line) this.line = line;
        this.type = type;
    }

    static encode(instance: Machine): Record<string, any> {
        return {
            machineId: instance.machineId,
            type: instance.type,
            description: instance.description,
        };
    }

    static decode(json: Record<string, any>): Machine {
        if (
            typeof json.id !== "string" ||
            typeof json.type !== "string" ||
            typeof json.description !== "string"
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for Machine");
        }
        return new Machine(json.id, json.type, json.description);
    }

    static decodeGroups(groups: Record<string, Record<string, any>>): Machine[] {
        const machines: Machine[] = [];

        Object.entries(groups).forEach(([groupName, machinesInGroup]) => {
            Object.entries(machinesInGroup).forEach(([machineName, machineData]) => {
                if (
                    typeof machineData.id !== "string" ||
                    typeof machineData.type !== "string" ||
                    typeof machineData.description !== "string"
                ) {
                    throw new Error(`Invalid machine structure in group ${groupName}, machine ${machineName}`);
                }

                // Reformat machine name with regex
                // Split by Machine, for example "MachineA" -> "Machine A"
                const machineType: string = machineData.type.replace(/([a-z])([A-Z])/g, '$1 $2');

                // Add machine object to the result array
                machines.push({
                    machineId: machineData.id,
                    type: machineType, // Type is directly provided in the new format
                    description: machineData.description
                });
            });
        });

        return machines;
    }
}


export class KPI {
    id: string; // internal id
    type: string; // category
    name: string; // displayed name
    description: string; // description
    unit: string;
    forecastable: boolean;

    constructor(id: string, type: string, name: string, value: string, unit: string, forecastable: boolean) {
        this.id = id;
        this.type = type;
        this.name = name;
        this.description = value;
        this.unit = unit;
        this.forecastable = forecastable;
    }

    static encode(instance: KPI): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            description: instance.description,
            unit: instance.unit,
            forecastable: instance.forecastable,
        };
    }

    static decode(json: Record<string, any>): KPI {
        if (
            typeof json.id !== "string" ||
            typeof json.type !== "string" ||
            typeof json.name !== "string" ||
            typeof json.description !== "string" ||
            typeof json.unit !== "string" ||
            typeof json.forecastable !== "boolean"
        ) {
            throw new Error("Invalid JSON structure for KPI");
        }
        return new KPI(json.id, json.type, json.name, json.description, json.unit, json.forecastable);
    }

    static decodeGroups(groups: Record<string, Record<string, any>>): KPI[] {
        const kpis: KPI[] = [];
        Object.entries(groups).forEach(([groupName, metrics]) => {
            Object.entries(metrics).forEach(([metricName, metricData]) => {
                if (
                    typeof metricData.id !== "string" ||
                    typeof metricData.description !== "string" ||
                    typeof metricData.unit_measure !== "string" ||
                    typeof metricData.type !== "string" ||
                    (metricData.forecastable && typeof metricData.forecastable !== "boolean")
                ) {
                    throw new Error(`Invalid KPI structure in group ${groupName}, metric ${metricName}`);
                }

                // reformat kpi name with regex
                // if followed by _avg, _min, _max, _sum, _med change it to (Avg), (Min), (Max), (Sum), (Med)
                // replace _ with space and capitalize first letter of each word

                metricName = metricName.replace(/_avg/g, " (Avg)")
                    .replace(/_min/g, " (Min)")
                    .replace(/_max/g, " (Max)")
                    .replace(/_sum/g, " (Sum)")
                    .replace(/_med/g, " (Med)")
                    .replace(/_std/g, " (Std)")
                    .replace(/_/g, " ")
                    .replace(/\b\w/g, (char) => char.toUpperCase());

                // metric type reformatted to have the "KPI" suffix divided by a space
                // EnergyKPI -> Energy KPI
                metricData.type = metricData.type.replace(/([a-z])([A-Z])/g, '$1 $2');

                const kpi = new KPI(
                    metricData.id,
                    metricData.type, // The type is now directly provided in the JSON
                    metricName, // Metric name as the display name
                    metricData.description,
                    metricData.unit_measure, // Use unit_measure for unit
                    metricData.forecastable ? metricData.forecastable : false // Forecastable flag
                );
                kpis.push(kpi);
            });
        });

        return kpis;
    }
}

export class Schedule {
    id: number;
    name: string;
    recurrence: string; // Daily, Weekly, Monthly
    status: "Active" | "Inactive";
    email: string;
    startDate: string;
    kpis: string[]; // List of selected KPIs
    machines: string[]; // List of selected machines
    machineType?: string; // All, Custom Machine Set, or a specific machine type

    constructor(
        id: number,
        name: string,
        recurrence: string,
        status: "Active" | "Inactive",
        email: string,
        startDate: string,
        kpis: string[],
        machines: string[],
        machineType?: string
    ) {
        this.id = id;
        this.name = name;
        this.recurrence = recurrence;
        this.status = status;
        this.email = email;
        this.startDate = startDate;
        this.kpis = kpis;
        this.machines = machines;
        this.machineType = machineType;
    }

    static encode(instance: Schedule): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            recurrence: instance.recurrence,
            status: instance.status === "Active",
            email: instance.email,
            startDate: instance.startDate,
            kpis: instance.kpis,
            machines: instance.machines,
        };
    }

    static decode(json: Record<string, any>): Schedule {
        if (
            typeof json.id !== "number" ||
            typeof json.name !== "string" ||
            typeof json.recurrence !== "string" ||
            typeof json.status !== "boolean" ||
            typeof json.email !== "string" ||
            typeof json.startDate !== "string" ||
            !Array.isArray(json.kpis) ||
            !Array.isArray(json.machines)
        ) {
            throw new Error("Invalid JSON structure for Schedule");
        }
        return new Schedule(
            json.id,
            json.name,
            json.recurrence,
            json.status ? "Active" : "Inactive",
            json.email,
            json.startDate,
            json.kpis,
            json.machines,
            "Custom Machine Set"
        );
    }
}

const supportedGraphTypes = ["line", "area", "barv", "barh", "pie", "donut", "scatter", "hist", "stacked_bar"];

export class DashboardEntry {
    kpi: string;
    graph_type: string;

    constructor(kpi: string, graph_type: string) {
        this.kpi = kpi;
        this.graph_type = graph_type;
    }

    static encode(instance: DashboardEntry): Record<string, any> {
        return {
            kpi: instance.kpi,
            graph_type: instance.graph_type
        }
    }

    static decode(json: Record<string, any>): DashboardEntry {
        if (typeof json.kpi !== "string" ||
            typeof json.graph_type !== "string") {
            throw new Error("Invalid JSON structure for DashboardEntry");
        }
        if (!supportedGraphTypes.includes(json.graph_type)) {
            throw new Error("Unsupported graph type for DashboardEntry");
        }
        return new DashboardEntry(json.kpi, json.graph_type)
    }

    static decodeChat(json: Record<string, any>): DashboardEntry {
        // decode a json onbject like
        // "bar_chart": "power_consumption_efficiency"
        // into a DashboardEntry object

        // Extract the graph_type name from the key
        let graph_type = Object.keys(json)[0];
        const kpi = json[graph_type];

        console.log("Decoding chat json", json, "into", kpi, graph_type);
        // remove _chart from the graph_type
        graph_type = graph_type.replace(/_chart/g, "");

        if (!supportedGraphTypes.includes(graph_type)) {
            console.log("Unsupported graph type for DashboardEntry, defaulting to Line", graph_type);
            graph_type = "line";
        }
        if (typeof kpi !== "string") {
            throw new Error("Invalid JSON structure for DashboardEntry : KPI name is not a string");
        }
        return new DashboardEntry(kpi, graph_type);
    }
}

export class DashboardLayout {
    id: string; // id for the internal path
    name: string; //displayed name in breadcrumb
    views: DashboardEntry[]

    constructor(id: string, name: string, views: DashboardEntry[]) {
        this.id = id;
        this.name = name;
        this.views = views;
    }

    // Encode a DashboardLayout instance to a JSON object
    static encode(instance: DashboardLayout): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            views: instance.views.map((view) => DashboardEntry.encode(view)), // Encode each DashboardEntry
        };
    }

    // Decode a JSON object to a DashboardLayout instance
    static decode(json: Record<string, any>): DashboardLayout {
        if (
            typeof json.id !== "string" ||
            typeof json.name !== "string" ||
            !Array.isArray(json.views)
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for DashboardLayout");
        }

        // Decode each view in the views array
        const views = json.views.map((viewJson) => DashboardEntry.decode(viewJson));

        return new DashboardLayout(json.id, json.name, views);
    }

}

export class DashboardFolder {
    id: string; // id for the internal path
    name: string; //displayed name in breadcrumb
    children: (DashboardFolder | DashboardLayout)[] //another folder or the pointer to the layout to load

    constructor(id: string, name: string, children: (DashboardFolder | DashboardLayout)[]) {
        this.id = id;
        this.name = name;
        this.children = children;
    }

    // Encode a DashboardFolder instance to a JSON object
    static encode(instance: DashboardFolder): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            children: instance.children.map((child) => {
                if (child instanceof DashboardFolder) {
                    return DashboardFolder.encode(child); // Encode DashboardFolder
                } else {
                    return DashboardLayout.encode(child); // Encode DashboardLayout id
                }
            }),
        };
    }

    /**
     * Decode a JSON object to a DashboardFolder instance
     * @param json - JSON object to decode
     * @returns - Decoded DashboardFolder instance
     **/
    static decode(json: Record<string, any>): DashboardFolder {
        if (
            typeof json.id !== "string" ||
            typeof json.name !== "string" ||
            !Array.isArray(json.children)
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for DashboardFolder");
        }

        // Decode each child in the children array
        const children = json.children.map((childJson) => {
            if (!childJson.children) {
                return DashboardLayout.decode(childJson); // Decode DashboardPointer
            } else {
                return DashboardFolder.decode(childJson); // Decode DashboardFolder
            }
        });

        return new DashboardFolder(json.id, json.name, children);
    }

    /**
     * Encode a list of DashboardFolder and DashboardLayout objects into a JSON object wrapped in a root node
     * @param dashboards - List of DashboardFolder and DashboardLayout objects
     * @returns - Encoded JSON object
     **/
    static encodeTree(dashboards: (DashboardFolder | DashboardLayout)[]): Record<string, any> {
        // create a json object with the root node as the key
        // and the children as the value
        let root = new DashboardFolder("root", "root", dashboards);
        return DashboardFolder.encode(root);
    }
}