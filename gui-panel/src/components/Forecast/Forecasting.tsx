import React, {useEffect, useState} from "react";
import PersistentDataManager from "../../api/PersistentDataManager";
import {fetchData, simulateChartData} from "../../api/DataFetcher";
import FutureTimeFrameSelector from "./FutureTimeSelector";
import {TimeFrame} from "../Selectors/TimeSelect";
import KpiSelect from "../Selectors/KpiSelect";
import {KPI, Machine} from "../../api/DataStructures";
import MachineSelect from "../Selectors/MachineSelect";
import ForeChart from "../Chart/ForecastingChart";
import {Filter} from "../Selectors/FilterOptions";

type ForecastData = {
    date: string;
    value: number;
    confidence: number;
};

class LimeData {

    feature: string;
    importance: number;

    constructor(feature: string, importance: number) {
        this.feature = feature;
        this.importance = importance;
    }

    static decode(json: Record<string, any>): LimeData {
        if (typeof json.feature !== "string") {
            throw new Error("Invalid type for feature");
        }
        if (typeof json.importance !== "number") {
            throw new Error("Invalid type for importance");
        }

        return new LimeData(json.feature, json.importance);
    }

    static decodeArray(json: Record<string, any>): LimeData[] {
        return json.map(LimeData.decode);
    }
}

class ForecastDataX {
    /*
    out_dict = {
        'Machine_name': 'MACHINENAME :(',
        'KPI_name': 'KPINAME :)',
        'Predicted_value': [0,1,2,3,4,5,6,7,8,9,10],
        'Lower_bound':[1,1,1,1,1,1,1,1,1,1], #from XAI
        'Upper_bound':[0,0,0,0,0,0,0,0,0,0], #from XAI
        'Confidence_score':[9,8,7,6,5,4,3,2,1,0], #from XAI
        'Lime_explaination': list(('string',2.1),("2",2),("s",1)), #from XAI
        'Measure_unit': 'Kbps',
        'Date_prediction': [d,d,d,d,d,d,d,d,d,d],
        'Forecast' :true
}
     */
    // adjust ForecastData to decode something like this
    machineName: string
    kpiName: string
    predictedValue: number[]
    lowerBound: number[]
    upperBound: number[]
    confidenceScore: number[]
    limeExplanation: LimeData[][]
    measureUnit: string
    datePrediction: string[]
    forecast: boolean

    constructor(machineName: string, kpiName: string, predictedValue: number[], lowerBound: number[], upperBound: number[], confidenceScore: number[], limeExplanation: LimeData[][], measureUnit: string, datePrediction: string[], forecast: boolean) {
        this.machineName = machineName;
        this.kpiName = kpiName;
        this.predictedValue = predictedValue;
        this.lowerBound = lowerBound;
        this.upperBound = upperBound;
        this.confidenceScore = confidenceScore;
        this.limeExplanation = limeExplanation;
        this.measureUnit = measureUnit;
        this.datePrediction = datePrediction;
        this.forecast = forecast;
    }

    static decode(json: Record<string, any>): ForecastDataX {
        if (typeof json.Machine_name !== "string") {
            throw new Error("Invalid type for Machine_name");
        }
        if (typeof json.KPI_name !== "string") {
            throw new Error("Invalid type for KPI_name");
        }
        if (!Array.isArray(json.Predicted_value)) {
            throw new Error("Invalid type for Predicted_value");
        }
        if (!Array.isArray(json.Lower_bound)) {
            throw new Error("Invalid type for Lower_bound");
        }
        if (!Array.isArray(json.Upper_bound)) {
            throw new Error("Invalid type for Upper_bound");
        }
        if (!Array.isArray(json.Confidence_score)) {
            throw new Error("Invalid type for Confidence_score");
        }
        if (!Array.isArray(json.Lime_explaination)) {
            throw new Error("Invalid type for Lime_explaination");
        }
        if (typeof json.Measure_unit !== "string") {
            throw new Error("Invalid type for Measure_unit");
        }
        if (!Array.isArray(json.Date_prediction)) {
            throw new Error("Invalid type for Date_prediction");
        }
        if (typeof json.Forecast !== "boolean") {
            throw new Error("Invalid type for Forecast");
        }

        return new ForecastDataX(json.Machine_name, json.KPI_name, json.Predicted_value, json.Lower_bound, json.Upper_bound, json.Confidence_score, json.Lime_explaination.map(LimeData.decodeArray), json.Measure_unit, json.Date_prediction, json.Forecast);
    }
}

const ForecastingPage: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<KPI>(new KPI("none", "None", "None Selected", "", "", true)); // Update to store the entire KPI object
    const [selectedMachine, setSelectedMachine] = useState<Machine>(new Machine("None Selected", "None", "None ")); // Update to store the entire Machine object
    const [forecastData, setForecastData] = useState<{ past: any[], future: ForecastData[] }>({past: [], future: []});
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame; key: string } | null>(null);

    useEffect(() => {
        console.log("Timeframe changed:", timeFrame);
        fetchForecastData();
    }, [timeFrame]);
    useEffect(() => {
        fetchForecastData();
    }, [selectedKpi]);
    useEffect(() => {
        fetchForecastData();
    }, [selectedMachine]);

    const fetchForecastData = async () => {
        if (selectedKpi.id !== "none" && timeFrame !== null && selectedMachine.machineId !== "None Selected") {
            setLoading(true);
            const machineFilter = new Filter(selectedMachine.type, [selectedMachine.machineId]);
            const pastData = await fetchData(selectedKpi, timeFrame.past, "line", machineFilter);
            const futureData = await simulateChartData(selectedKpi, timeFrame.future, "line", machineFilter);
            // Add default confidence value to each data point
            const combinedData = futureData.map(dataPoint => ({
                ...dataPoint,
                confidence: 80, // Default confidence value
            }));
            setForecastData({past: pastData, future: combinedData});
            setLoading(false);
        } else setForecastData({past: [], future: []});
    };


    const formatDate = (date: Date) => date.toISOString().split('T')[0]; // Format date as YYYY-MM-DD

    const kpis = dataManager.getKpiList().filter(kpi => kpi.forecastable);
    const machines = dataManager.getMachineList();
    return (
        <div className="ForecastingPage max-w-4xl mx-auto p-6 bg-white shadow-md rounded-lg ">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Data Forecasting</h1>
            <div className="text-gray-800 mb-4 font-[450]">
                <p className="text-base">Forecast future data using historical data and autoregressive models.</p>
                <p className="text-base">Select the kpi and machine to view the forecast for the selected future
                    timeframe.</p>
            </div>
            <div className="flex items-center text-start space-x-4 mb-6">
                <div className="w-1/2">
                    <KpiSelect
                        label="Select a KPI"
                        description="Choose a KPI from the list"
                        value={selectedKpi || ({} as KPI)} // Pass the selected KPI, or an empty object if null
                        options={kpis}
                        onChange={setSelectedKpi}
                    />
                </div>

                <div className="w-1/2">
                    <FutureTimeFrameSelector timeFrame={timeFrame} setTimeFrame={setTimeFrame}/>
                </div>

                <div className="w-1/2">
                    <MachineSelect
                        label="Select a Machine"
                        description="Choose a Machine from the list"
                        value={selectedMachine || ({} as Machine)} // Pass the selected Machine, or an empty object if null
                        options={machines}
                        onChange={setSelectedMachine}
                    />
                </div>
            </div>

            <div className="bg-white p-6 border-2 rounded-lg shadow-md">
                {loading ? (
                    <p className="text-gray-600 text-center">Loading forecast data...</p>
                ) : (forecastData && forecastData.future.length > 0 && timeFrame ? (
                    <div>
                        <p className="text-sm text-gray-700 mb-4">
                            Forecasting data
                            about <strong> {selectedKpi?.name}</strong> from {formatDate(timeFrame.future.from)}
                            {' '} to {formatDate(timeFrame.future.to)},
                            using data from {formatDate(timeFrame.past.from)}
                            {' '} to {formatDate(timeFrame.past.to)}.
                        </p>
                        <ForeChart pastData={forecastData.past}
                                   futureData={forecastData.future}
                                   kpi={selectedKpi}
                                   timeUnit={timeFrame.past.aggregation}
                                   explanationData={getDummyExplanationData(forecastData.future)}
                        />
                    </div>
                ) : (
                    <p className="text-gray-600 text-center">Select a KPI and Machine to view its forecast.</p>
                ))}
            </div>
        </div>
    );
};

const getDummyExplanationData = (data: any[]) => {
    return data.map((point, index) => {
        // data can be positive or negative
        return [
            {feature: "Feature 1", importance: (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 2", importance: (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 3", importance: (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 4", importance: (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 5", importance: (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 6", importance: (Math.random() * 2 - 1).toFixed(2)},
        ];
    });

}

export default ForecastingPage;
