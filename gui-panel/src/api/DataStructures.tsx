//in this file we define the data structures and their json encode/decode methods for persistency and api communication

export class Machine {
    machineId: string;
    line?: string;
    site: string;
    type: string;

    constructor(machineId: string, site: string, type: string, line?: string) {
        this.machineId = machineId;
        this.site = site;
        if (line) this.line = line;
        this.type = type;
    }

    static encode(instance: Machine): Record<string, any> {
        return {
            machineId: instance.machineId,
            site: instance.site,
            type: instance.type,
            productionLine: instance.line,
        };
    }

    static decode(json: Record<string, any>): Machine {
        if (
            typeof json.machineId !== "string" ||
            typeof json.site !== "string" ||
            typeof json.type !== "string" ||
            (json.productionLine && typeof json.productionLine !== "string")
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for Machine");
        }
        return new Machine(json.machineId, json.site, json.type, json.productionLine);
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

export class DashboardPointer{
    id: string; // id for the internal path
    name: string; //displayed name in breadcrumb

    constructor(id: string, name: string) {
        this.id = id;
        this.name = name;
    }

    static encode(instance: DashboardPointer): Record<string, any> {
        return {
            id: instance.id,
            name: instance.name,
        };
    }

    static decode(json: Record<string, any>): DashboardPointer {
        if (
            typeof json.id !== "string" ||
            typeof json.name !== "string"
        ) {
            console.log(json);
            throw new Error("Invalid JSON structure for DashboardPointer");
        }
        return new DashboardPointer(json.id, json.name);
    }
}

export class DashboardFolder {
    id: string; // id for the internal path
    name: string; //displayed name in breadcrumb
    children: (DashboardFolder | DashboardPointer)[] //another folder or the pointer to the layout to load

    constructor(id: string, name: string, children: (DashboardFolder | DashboardPointer)[]) {
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
                    return DashboardPointer.encode(child); // Encode DashboardLayout id
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
                return DashboardPointer.decode(childJson); // Decode DashboardPointer
            } else {
                return DashboardFolder.decode(childJson); // Decode DashboardFolder
            }
        });

        return new DashboardFolder(json.id, json.name, children);
    }

}