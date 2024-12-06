import React, {useEffect, useState} from "react";
import PersistentDataManager from "../../api/PersistentDataManager";
import {simulateChartData} from "../../api/QuerySimulator";
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

const ForecastingPage: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<KPI>(new KPI("none", "None", "None Selected", "", "")); // Update to store the entire KPI object
    const [selectedMachine, setSelectedMachine] = useState<Machine>(new Machine("None Selected", "None", "None ")); // Update to store the entire Machine object
    const [forecastData, setForecastData] = useState<ForecastData[]>([]);
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame } | null>(null);

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
            const pastData = await simulateChartData(selectedKpi, timeFrame.past, "line", machineFilter);
            const futureData = await simulateChartData(selectedKpi, timeFrame.future, "line", machineFilter);
            // Add default confidence value to each data point
            const combinedData = [...pastData, ...futureData].map(dataPoint => ({
                ...dataPoint,
                confidence: 80, // Default confidence value
            }));
            setForecastData(combinedData);
            setLoading(false);
        } else setForecastData([])
    };


    const formatDate = (date: Date) => date.toISOString().split('T')[0]; // Format date as YYYY-MM-DD

    const kpis = dataManager.getKpiList();
    const machines = dataManager.getMachineList();
    return (
        <div className="ForecastingPage max-w-4xl mx-auto p-6 bg-gray-100">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">KPI Forecasting</h1>
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

            <div className="bg-white p-6 rounded-lg shadow-md">
                {loading ? (
                    <p className="text-gray-600 text-center">Loading forecast data...</p>
                ) : (forecastData.length > 0 && timeFrame ? (
                    <div>
                        <p className="text-sm text-gray-700 mb-4">
                            Forecasting data
                            about <strong> {selectedKpi?.name}</strong> from {formatDate(timeFrame.future.from)}
                            {' '} to {formatDate(timeFrame.future.to)},
                            using data from {formatDate(timeFrame.past.from)}
                            {' '} to {formatDate(timeFrame.past.to)}.
                        </p>
                        <ForeChart data={forecastData}
                                   kpi={selectedKpi}
                                   timeUnit={timeFrame.past.aggregation}
                                   explanationData={getDummyExplanationData(forecastData)}
                        />
                    </div>
                ) : (
                    <p className="text-gray-600 text-center">Select a KPI to view its forecast.</p>
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
            {feature: "Feature 2", importance:  (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 3", importance:  (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 4", importance:  (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 5", importance:  (Math.random() * 2 - 1).toFixed(2)},
            {feature: "Feature 6", importance:  (Math.random() * 2 - 1).toFixed(2)},
        ];
    });

}

export default ForecastingPage;
