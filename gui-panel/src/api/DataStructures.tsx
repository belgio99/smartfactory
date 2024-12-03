//in this file we define the data structures and their json encode/decode methods for persistency and api communication

export class Machine {
    machineId: string;
    line?: string;
    site?: string;
    type: string;

    constructor(machineId: string, type: string, site?: string, line?: string) {
        this.machineId = machineId;
        if (line) this.site = site;
        if (line) this.line = line;
        this.type = type;
    }

    static encode(instance: Machine): Record<string, any> {
        return {
            machineId: instance.machineId,
            type: instance.type,
            site: instance?.site,
            productionLine: instance?.line,
        };
    }

    static decode(json: Record<string, any>): Machine {
        if (
            typeof json.machineId !== "string" ||
            (json.site && typeof json.site !== "string") ||
            typeof json.type !== "string" ||
            (json.productionLine && typeof json.productionLine !== "string")
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for Machine");
        }
        return new Machine(json.machineId, json.type, json.site, json.productionLine);
    }

}


export class KPI {
    id: number; // internal id
    type: string; // category
    name: string; // displayed name
    description: string; // description
    unit: string;

    constructor(id: number, type: string, name: string, value: string, unit: string) {
        this.id = id;
        this.type = type;
        this.name = name;
        this.description = value;
        this.unit = unit;
    }

    static encode(instance: KPI): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            description: instance.description,
            unit: instance.unit,
        };
    }

    static decode(json: Record<string, any>): KPI {
        if (
            typeof json.id !== "number" ||
            typeof json.type !== "string" ||
            typeof json.name !== "string" ||
            typeof json.description !== "string" ||
            typeof json.unit !== "string"
        ) {
            throw new Error("Invalid JSON structure for KPI");
        }
        return new KPI(json.id, json.type, json.name, json.description, json.unit);
    }

}

export class KPIGroup {
    category: string; // Top-level category (e.g., Energy)
    subcategory: string; // Subcategory name (e.g., Consumption)
    unit: string; // Unit of measurement for this group
    metrics: KPIOptions[]; // Array of detailed metric options

    constructor(category: string, subcategory: string, unit: string, metrics: KPIOptions[]) {
        this.category = category;
        this.subcategory = subcategory;
        this.unit = unit;
        this.metrics = metrics;
    }

    static encode(instance: KPIGroup): Record<string, any> {
        return {
            category: instance.category,
            subcategory: instance.subcategory,
            unit: instance.unit,
            metrics: instance.metrics.map(KPIOptions.encode),
        };
    }

    static decode(json: Record<string, any>): KPIGroup {
        if (
            typeof json.category !== "string" ||
            typeof json.subcategory !== "string" ||
            typeof json.unit !== "string" ||
            !Array.isArray(json.metrics)
        ) {
            throw new Error("Invalid JSON structure for KPIGroup");
        }

        const metrics = json.metrics.map(KPIOptions.decode);
        return new KPIGroup(json.category, json.subcategory, json.unit, metrics);
    }
}
export class KPIOptions {
    id: string; // Unique identifier for the metric
    name: string; // Metric name (e.g., avg, min, max)
    description: string; // Detailed description of the metric
    forecastable: boolean; // Indicates if the metric is forecastable

    constructor(id: string, name: string, description: string, forecastable: boolean) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.forecastable = forecastable;
    }

    static encode(instance: KPIOptions): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
            description: instance.description,
            forecastable: instance.forecastable,
        };
    }

    static decode(json: Record<string, any>): KPIOptions {
        if (
            typeof json.id !== "string" ||
            typeof json.name !== "string" ||
            typeof json.description !== "string" ||
            typeof json.forecastable !== "boolean"
        ) {
            throw new Error("Invalid JSON structure for KPIOptions");
        }

        return new KPIOptions(json.id, json.name, json.description, json.forecastable);
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
    kpi: number;
    graph_type: string;

    constructor(kpi: number, graph_type: string) {
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
        if (
            typeof json.graph_type !== "string") {
            throw new Error("Invalid JSON structure for DashboardEntry");
        }
        if (!supportedGraphTypes.includes(json.graph_type)) {
            throw new Error("Unsupported graph type for DashboardEntry");
        }
        return new DashboardEntry(json.kpi, json.graph_type)
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

    // Decode a JSON object to a DashboardFolder instance
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

}