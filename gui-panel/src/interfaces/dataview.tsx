export interface TimeFrame {
    from: string;
    to: string;
    aggregation?: string;
}

export interface JsonObject {
    data_type: string;
    visual: string;
    kpi: string;
    machines: number[];
    time_frame: TimeFrame;
}
