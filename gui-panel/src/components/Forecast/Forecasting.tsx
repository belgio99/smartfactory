import React, {useEffect, useState} from "react";
import {getKpiList} from "../../api/PersistentDataManager";
import Chart from "../Chart/Chart";
import {simulateChartData} from "../../api/QuerySimulator";
import FutureTimeFrameSelector from "./FutureTimeSelector";
import {TimeFrame} from "../KpiSelector/TimeSelector";

type ForecastData = {
    date: string;
    value: number;
};

const ForecastingPage: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<number | null>(null);
    const [forecastData, setForecastData] = useState<ForecastData[]>([]);
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame } | null>(null);

    useEffect(() => {
        console.log("Timeframe changed:", timeFrame);
        fetchForecastData();
    }, [timeFrame]);

    const fetchForecastData = async () => {
        if (selectedKpi !== null && timeFrame !== null) {
            setLoading(true);
            const kpi = getKpiList().find((k) => k.id === selectedKpi);
            if (!kpi) {
                console.error(`KPI with ID ${selectedKpi} not found.`);
                setLoading(false);
                return;
            }

            const pastData = await simulateChartData(kpi, timeFrame.past, "line");
            const futureData = await simulateChartData(kpi, timeFrame.future, "line");

            setForecastData([...pastData, ...futureData]);
            setLoading(false);
        }
    };

    const handleKpiChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const kpiId = parseInt(e.target.value, 10);

        if (!isNaN(kpiId)) {
            setSelectedKpi(kpiId);
        } else {
            setSelectedKpi(null);
            setForecastData([]);
        }
    };

    useEffect(() => {
        fetchForecastData();
    }, [selectedKpi]); // Recompute data when selected KPI changes.

    const formatDate = (date: Date) => date.toISOString().split('T')[0]; // Format date as YYYY-MM-DD

    const kpis = getKpiList();
    return (
        <div className="ForecastingPage max-w-4xl mx-auto p-6 bg-gray-100">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">KPI Forecasting</h1>
            <div className="flex items-center space-x-4 mb-6">
                <div className="w-1/2">
                    <label className="block text-gray-700 font-medium mb-2" htmlFor="kpi-select">
                        Select a KPI
                    </label>
                    <select
                        id="kpi-select"
                        className="w-full font-normal  p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        onChange={handleKpiChange}
                    >
                        <option value="">-- Select KPI --</option>
                        {kpis.map((kpi) => (
                            <option key={kpi.id} value={kpi.id}>
                                {kpi.name}
                            </option>
                        ))}
                    </select>
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
                            about <strong> {kpis.find((kpi) => kpi.id === selectedKpi)?.name}</strong> from {formatDate(timeFrame.future.from)}
                            {' '} to {formatDate(timeFrame.future.to)},
                            using data from {formatDate(timeFrame.past.from)}
                            {' '} to {formatDate(timeFrame.past.to)}.
                        </p>
                        <Chart data={forecastData}
                               graphType="line"
                               kpi={kpis.find((kpi) => kpi.id === selectedKpi)}
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
