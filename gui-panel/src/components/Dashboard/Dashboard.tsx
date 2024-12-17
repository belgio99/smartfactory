import {useParams} from 'react-router-dom';
import React, {useEffect, useState} from "react";
import {DashboardEntry, DashboardLayout} from "../../api/DataStructures";
import Chart from "../Chart/Chart";
import {fetchData} from "../../api/DataFetcher";
import FilterOptionsV2, {Filter} from "../Selectors/FilterOptions";
import TimeSelector, {TimeFrame} from "../Selectors/TimeSelect";
import PersistentDataManager from "../../api/DataManager";
import {handleTimeAdjustments} from "../../utils/chartUtil";

const Dashboard: React.FC = () => {
        const dataManager = PersistentDataManager.getInstance();
        const {dashboardId, dashboardPath} = useParams<{ dashboardId: string, dashboardPath: string }>();
        const [dashboardData, setDashboardData] = useState<DashboardLayout>(new DashboardLayout("", "", []));
        const [loading, setLoading] = useState(true);
        const [refreshing, setRefreshing] = useState(false);
        const [chartData, setChartData] = useState<any[][]>([]);
        const kpiList = dataManager.getKpiList(); // Cache KPI list once
        const [filters, setFilters] = useState(new Filter("All", []));
        const [timeFrame, setTimeFrame] = useState<TimeFrame>({
            from: new Date(2024, 9, 16),
            to: new Date(2024, 9, 19),
            aggregation: 'day'
        });
        const [isRollbackTime, setIsRollbackTime] = useState(false);

        //on first data load
        useEffect(() => {
            const fetchDashboardDataAndCharts = async () => {
                try {
                    setLoading(true);
                    setFilters(new Filter("All", [])); // Reset filters

                    await dataManager.waitUntilInitialized(); // Ensure initialization
                    // Fetch dashboard data by id
                    let dash = dataManager.findDashboardById(`${dashboardId}`, `${dashboardPath}`);

                    setDashboardData(dash);

                    let timeframe = handleTimeAdjustments(timeFrame, isRollbackTime);

                    // Fetch chart data for each view
                    const chartDataPromises = dash.views.map(async (entry: DashboardEntry) => {
                        const kpi = kpiList.find(k => k.id === entry.kpi);
                        if (!kpi) {
                            console.error(`KPI with ID ${entry.kpi} not found.`);
                            return [];
                        }
                        return await fetchData(kpi, timeframe, entry.graph_type, undefined); // Add appropriate filters
                    });

                    const resolvedChartData = await Promise.all(chartDataPromises);
                    setChartData(resolvedChartData);
                } catch (error) {
                    console.error("Error fetching dashboard or chart data:", error);
                } finally {
                    setLoading(false);
                }
            };

            fetchDashboardDataAndCharts();
        }, [dashboardId, kpiList]);

        useEffect(() => {
                const fetchChartData = async () => {
                    // Ensure promises are created dynamically based on latest dependencies
                    const chartDataPromises = dashboardData.views.map(async (entry: DashboardEntry) => {
                        const kpi = kpiList.find(k => k.id === entry.kpi);
                        if (!kpi) {
                            console.error(`KPI with ID ${entry.kpi} not found.`);
                            return [];
                        }
                        let timeframe = handleTimeAdjustments(timeFrame, isRollbackTime);
                        return await fetchData(kpi, timeframe, entry.graph_type, filters); // Add appropriate filters
                    });
                    setRefreshing(true);
                    try {
                        const resolvedChartData = await Promise.all(chartDataPromises);
                        setChartData(resolvedChartData);
                    } catch (error) {
                        console.error("Error fetching chart data:", error);
                    } finally {
                        setRefreshing(false);
                    }
                };

                // Avoid re-fetching during initial loading
                if (!loading) {
                    fetchChartData();
                }
            }, [filters, timeFrame, isRollbackTime]
        );


        if (loading) {
            return <div className="flex flex-col justify-center items-center h-screen">
                <div className="text-lg text-gray-600">Loading...</div>
                <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-gray-500"></div>
            </div>

        }
        return <div className="p-8 space-y-8 bg-gray-50 min-h-screen">

            {/* Dashboard Title */}
            <h1 className="text-3xl font-extrabold text-center text-gray-800">{dashboardData.name}</h1>
            <div className="flex space-x-4">
                <div><FilterOptionsV2 filter={filters} onChange={setFilters}/></div>
                <div><TimeSelector timeFrame={timeFrame} setTimeFrame={setTimeFrame}/></div>
                <div>
                    <label htmlFor="timeRollback" className="text-gray-700">Back to last data available</label>
                    <input
                        type="checkbox"
                        id="timeRollback"
                        name="timeRollback"
                        checked={isRollbackTime}
                        onChange={() => setIsRollbackTime(!isRollbackTime)}
                        className="ml-2"
                    />
                </div>
            </div>
            {/* Refreshing indicator */}
            {refreshing && (
                <div className="fixed inset-0 bg-gray-800 bg-opacity-50 flex justify-center items-center">
                    <div className="flex flex-col items-center bg-white p-8 rounded-lg shadow-lg">
                        <div className="text-lg text-gray-800 mb-4">Updating Charts...</div>
                        <div
                            className="flex justify-center items-center animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-gray-500"></div>
                    </div>
                </div>
            )}
            {/* Grid Layout */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 items-center w-f">
                {dashboardData.views.map((entry: DashboardEntry, index: number) => {
                    let kpi = kpiList.find(k => k.id === entry.kpi);
                    if (!kpi) {
                        console.error(`KPI with ID ${entry.kpi} not found.`);
                        return null;
                    }

                    // Determine grid layout based on chart type
                    const isSmallCard = entry.graph_type === 'pie' || entry.graph_type === 'donut';

                    // Dynamic grid class
                    const gridClass = isSmallCard
                        ? 'sm:col-span-1 lg:col-span-1' // Small cards fit three in a row
                        : 'col-span-auto '; // Bar and Pie charts share rows;

                    return <div
                        key={index}
                        className={`bg-white shadow-lg rounded-xl p-6 border border-gray-200 hover:shadow-xl transition-shadow ${gridClass}`}
                    >
                        {/* KPI Title */}
                        <h3 className="text-xl font-semibold text-gray-700 mb-6 text-center">
                            {kpi?.name}
                        </h3>

                        {/* Chart */}
                        <div className="flex items-center justify-center">
                            <Chart
                                data={chartData[index]} // Pass the fetched chart data
                                graphType={entry.graph_type}
                                kpi={kpi}
                                timeUnit={timeFrame.aggregation}
                            />
                        </div>
                    </div>;
                })}
            </div>
        </div>;
    }
;

export default Dashboard;
