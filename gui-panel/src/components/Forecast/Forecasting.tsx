import React, {useEffect, useState} from "react";
import PersistentDataManager from "../../api/DataManager";
import {fetchData} from "../../api/DataFetcher";
import FutureTimeFrameSelector from "./FutureTimeSelector";
import {TimeFrame} from "../Selectors/TimeSelect";
import KpiSelect from "../Selectors/KpiSelect";
import {ForecastDataEx, KPI, Machine} from "../../api/DataStructures";
import MachineSelect from "../Selectors/MachineSelect";
import ForeChart from "../Chart/ForecastingChart";
import {Filter} from "../Selectors/FilterOptions";
import {getForecastData} from "../../api/ApiService";

const ForecastingPage: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<KPI>(new KPI("none", "None", "None Selected", "", "", true)); // Update to store the entire KPI object
    const [selectedMachine, setSelectedMachine] = useState<Machine>(new Machine("None Selected", "None", "None ")); // Update to store the entire Machine object
    const [forecastData, setForecastData] = useState<{ past: any[], future?: ForecastDataEx }>({past: [],});
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame; key: string } | null>(null);

    useEffect(() => {
        fetchForecastData();
    }, [timeFrame, selectedKpi, selectedMachine]);

    const fetchForecastData = async () => {
        if (selectedKpi.id !== "none" && timeFrame !== null && selectedMachine.machineId !== "None Selected") {
            setLoading(true);
            const machineFilter = new Filter(selectedMachine.type, [selectedMachine.machineId]);
            try {
                const pastData = await fetchData(selectedKpi, timeFrame.past, "line", machineFilter).catch(
                    (error) => {
                        console.error('Failed to fetch past data:', error);
                        return [];
                    }
                );
                // Difference between the two dates in days
                const numberOfDays = Math.floor((timeFrame.future.to.getTime() - timeFrame.future.from.getTime()) / (1000 * 60 * 60 * 24));
                const futureData = await getForecastData({
                    KPI_Name: selectedKpi.id,
                    Machine_Name: selectedMachine.machineId,
                    Date_prediction: numberOfDays
                }).catch((error) => {
                    console.error('Failed to fetch future data:', error);
                    return new ForecastDataEx(selectedMachine.machineId,
                        selectedKpi.id,
                        [],
                        [],
                        [],
                        [],
                        [],
                        "",
                        [],
                        true
                    );
                });
                console.log("Future data received for the next %s days: ", numberOfDays, futureData);
                setForecastData({past: pastData, future: futureData});
            } catch (error) {
                console.error('Failed to fetch forecast data:', error);
            } finally {
                setLoading(false);
            }
        } else setForecastData({past: [],});
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
                ) : (forecastData && forecastData?.future && timeFrame ? (
                    <div>
                        <p className="text-sm text-gray-700 mb-4">
                            Forecasting data
                            about <strong> {selectedKpi?.name}</strong> from {formatDate(timeFrame.future.from)}
                            {' '} to {formatDate(timeFrame.future.to)},
                            using data from {formatDate(timeFrame.past.from)}
                            {' '} to {formatDate(timeFrame.past.to)}.
                        </p>
                        <ForeChart pastData={forecastData.past}
                                   futureDataEx={forecastData.future}
                                   kpi={selectedKpi}
                                   timeUnit={timeFrame.past.aggregation}
                        />
                    </div>
                ) : (
                    <p className="text-gray-600 text-center">Select a KPI and Machine to view its forecast.</p>
                ))}
            </div>
        </div>
    );
};
export default ForecastingPage;
