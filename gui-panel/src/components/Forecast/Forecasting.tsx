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
import {getForecastData, trainAllModels, getForecastData_extra} from "../../api/ApiService";

const ForecastingPage: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [loading, setLoading] = useState(false);
    const [selectedKpi, setSelectedKpi] = useState<KPI>(new KPI("none", "None", "None Selected", "", "", true)); // Update to store the entire KPI object
    const [selectedKpi2, setSelectedKpi2] = useState<KPI>(new KPI("none", "None", "None Selected", "", "", true));
    const [operation, setOperation] = useState<string>("sum");
    const [selectedMachine, setSelectedMachine] = useState<Machine>(new Machine("None Selected", "None", "None ")); // Update to store the entire Machine object
    const [forecastData, setForecastData] = useState<{ past: any[], future?: ForecastDataEx }>({past: [],});
    const [timeFrame, setTimeFrame] = useState<{ past: TimeFrame; future: TimeFrame; key: string } | null>(null);
    const [timeFrame_ex, setTimeFrame_ex] = useState<TimeFrame>({
        from: new Date(2024, 2, 2),
        to: new Date(2024, 9, 19),
        aggregation: "day"
    });
    
    // useEffect(() => {
    //     fetchForecastData();
    // }, [timeFrame, selectedKpi, selectedMachine]);
    const handleButton3Click = async () => {
        fetchForecastData();
    }
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
    
    const handleButton1Click = async () => {
        console.log("Train All Models button clicked!");
        try {
            setLoading(true);
            const result = await trainAllModels();
            console.log("Train All Models result:", result); // should be 0 if successful
            // Optionally display a success message or update state
        } catch (err) {
            console.error("Error training all models:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleButton2Click = async () => {
        console.log("Predict new KPI button clicked!");
        // Similar to fetchForecastData, but calling getForecastData_extra()
        if (timeFrame !== null && selectedMachine.machineId !== "None Selected") {
            setLoading(true);
            try {
                const machineFilter = new Filter(selectedMachine.type, [selectedMachine.machineId]);

                const pastData_one = await fetchData(selectedKpi, timeFrame_ex, "line", machineFilter).catch(
                    (error) => {
                        console.error('Failed to fetch past data:', error);
                        return [];
                    }
                );

                const pastData_two = await fetchData(selectedKpi2, timeFrame_ex, "line", machineFilter).catch(
                    (error) => {
                        console.error('Failed to fetch past data_2:', error);
                        return [];
                    }
                );
                const dates = pastData_one.map(obj => obj.timestamp);
                // const dataOne = pastData_one.map(obj => obj[selectedKpi.id] ?? 0);
                const dataOne = pastData_one.map(obj => {
                    console.log("Checking object:", obj);
                    console.log("Value found:", obj[selectedMachine.machineId]);
                    console.log("selectedkpi.id", selectedMachine.machineId)
                    return obj[selectedMachine.machineId] ?? 0;
                });
                const dataTwo = pastData_two.map(obj => obj[selectedMachine.machineId] ?? 0);                
                let combinedData: number[] = [];
                if (operation === "sum") {
                    // element-wise sum
                    combinedData = dataOne.map((val, i) => val + dataTwo[i]);
                  } else {
                    // element-wise diff
                    combinedData = dataOne.map((val, i) => val - dataTwo[i]);
                  }
                const pastData_New = pastData_one.map((obj, i) => ({
                    ...obj, // Keep other properties unchanged
                    value: combinedData[i] // Update only the specific KPI value
                }));
                console.log("DATES")
                console.log(dates)
                console.log("Combined Data")
                console.log(combinedData) 
                console.log("past data one")
                console.log(dataOne)
                console.log("past data two")
                console.log(dataTwo)
                // const pastData = pastData_one + pastData_two
                const numberOfDays = Math.floor((timeFrame.future.to.getTime() - timeFrame.future.from.getTime()) / (1000 * 60 * 60 * 24));
                const futureData = await getForecastData_extra({
                    KPI_Name: selectedKpi.id,
                    Machine_Name: selectedMachine.machineId,
                    Date_prediction: numberOfDays,
                    Time_series: combinedData,
                    Time_series_dates: dates
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
                console.log("showing last 10 elements:")
                console.log(pastData_New.slice(-10))
                console.log(combinedData.slice(-10))
                console.log(futureData)
                setForecastData({past: pastData_New.slice(-10), future: futureData});    
            } catch (error) {
                console.error("Error predicting new KPI:", error);
            } finally {
                setLoading(false);
            }
            console.log("finished!")
        } else {
            console.log("Cannot predict new KPI - missing machine or KPI selection.");
        }
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
            <div className="flex items-center text-start space-x-4 mb-6">
                <div className="w-1/3">
                    <KpiSelect
                        label="Select a KPI"
                        description="Choose a KPI from the list"
                        value={selectedKpi2 || ({} as KPI)} // Pass the selected KPI, or an empty object if null
                        options={kpis}
                        onChange={setSelectedKpi2}
                    />
                </div>

                <div className="w-1/3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Operation
                    </label>
                    <select
                        className="border border-gray-300 rounded px-2 py-1 w-full"
                        value={operation}
                        onChange={(e) => setOperation(e.target.value)}
                    >
                        <option value="sum">Sum</option>
                        <option value="diff">Diff</option>
                    </select>
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

            <div className="flex justify-center mt-6 space-x-4">
                <button
                    className="px-4 py-2 bg-blue-500 text-white rounded-md shadow-md hover:bg-blue-600"
                    onClick={handleButton1Click}
                >
                    Train All Models
                </button>
                <button
                    className="px-4 py-2 bg-green-500 text-white rounded-md shadow-md hover:bg-green-600"
                    onClick={handleButton2Click}
                >
                    Predict new KPI
                </button>
                <button
                    className="px-4 py-2 bg-purple-500 text-white rounded-md shadow-md hover:bg-green-600"
                    onClick={handleButton3Click}
                >
                    Predict standard KPI
                </button>
            </div>
        </div>
    );
};
export default ForecastingPage;
