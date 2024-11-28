import React, {useState} from "react";
import {getKpiList} from "../../api/PersistentDataManager";
import Chart from "../Chart/Chart";
import {simulateChartData, TimeFrame} from "../../api/QuerySimulator";
import {KPI} from "../../api/DataStructures";

//TODO Adapt to use QuerySimulator format, or adapt QuerySimulator to use this format
type ForecastData = {
    date: string;
    value: number;
};

const ForecastingPage: React.FC = () => {

    const [selectedKpi, setSelectedKpi] = useState<number | null>(null);
    const [forecastData, setForecastData] = useState<ForecastData[]>([]);

    const handleKpiChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
        const kpiId = parseInt(e.target.value, 10);
        let kpi: KPI | undefined;
        if (!isNaN(kpiId)) {
            kpi = getKpiList().find((k) => k.id === kpiId);
            if (!kpi) {
                console.error(`KPI with ID ${kpiId} not found.`);
                return;
            }
            const now = new Date();
            const before = new Date();
            before.setMonth(now.getMonth() - 1);
            const data = await simulateChartData(kpi, new TimeFrame(before, now), "line");
            setSelectedKpi(kpiId);
            setForecastData(data);
        } else {
            setSelectedKpi(null);
            setForecastData([]);
        }
    };

    const kpis = getKpiList();

    return (
        <div className="ForecastingPage max-w-4xl mx-auto p-6 bg-gray-100 ">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">KPI Forecasting</h1>
            <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2" htmlFor="kpi-select">
                    Select a KPI
                </label>
                <select
                    id="kpi-select"
                    className="w-full p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
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

            <div className="bg-white p-6 rounded-lg shadow-md">
                {forecastData.length > 0 ? (

                    <p><h2 className="text-lg font-semibold mb-4">
                        Forecast for: {kpis.find((kpi) => kpi.id === selectedKpi)?.name}
                    </h2><Chart data={forecastData} graphType='line'
                                kpi={kpis.find((kpi) => kpi.id === selectedKpi)}/></p>

                ) : (
                    <p className="text-gray-600 text-center">Select a KPI to view its forecast.</p>
                )}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
                <p className="text-gray-600 text-center">This is the forecast explanation.</p>
            </div>
        </div>

    );
};

export default ForecastingPage;
