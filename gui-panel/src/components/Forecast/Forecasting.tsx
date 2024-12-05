import React, {useEffect, useState} from "react";
import PersistentDataManager from "../../api/PersistentDataManager";
import Chart from "../Chart/Chart";
import {simulateChartData} from "../../api/QuerySimulator";
import FutureTimeFrameSelector from "./FutureTimeSelector";
import {TimeFrame} from "../KpiSelector/TimeSelector";
import KpiSelect from "../KpiSelector/KpiSelect";
import {KPI} from "../../api/DataStructures";

type ForecastData = {
    date: string;
    value: number;
};

const ForecastingPage: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<KPI | undefined>(); // Update to store the entire KPI object
    const [forecastData, setForecastData] = useState<ForecastData[]>([]);
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame } | null>(null);

    useEffect(() => {
        console.log("Timeframe changed:", timeFrame);
        fetchForecastData();
    }, [timeFrame]);

    const fetchForecastData = async () => {
        if (selectedKpi && timeFrame !== null) {
            setLoading(true);

            const pastData = await simulateChartData(selectedKpi, timeFrame.past, "line");
            const futureData = await simulateChartData(selectedKpi, timeFrame.future, "line");

            setForecastData([...pastData, ...futureData]);
            setLoading(false);
        }else setForecastData([])
    };
    useEffect(() => {
        fetchForecastData();
    }, [selectedKpi]);

    const formatDate = (date: Date) => date.toISOString().split('T')[0]; // Format date as YYYY-MM-DD

    const kpis = dataManager.getKpiList();
    return (
        <div className="ForecastingPage max-w-4xl mx-auto p-6 bg-gray-100">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">KPI Forecasting</h1>
            <div className="flex items-center space-x-4 mb-6">
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
                        <Chart data={forecastData}
                               graphType="line"
                               kpi={selectedKpi}
                               timeUnit={timeFrame.past.aggregation}
                               timeThreshold={true}
                        />
                    </div>
                ) : (
                    <p className="text-gray-600 text-center">Select a KPI to view its forecast.</p>
                ))}
            </div>
        </div>
    );
};

export default ForecastingPage;
