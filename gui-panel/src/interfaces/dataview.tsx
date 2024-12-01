import {TimeFrame} from "../components/KpiSelector/TimeSelector";

export interface JsonObject {
    data_type: string;
    visual: string;
    kpi: string;
    machines: number[];
    time_frame: TimeFrame;
}
