import {useParams} from 'react-router-dom';
import React, {useEffect, useState} from "react";
import {DashboardEntry, DashboardLayout} from "../../api/DataStructures";
import Chart from "../Chart/Chart";
import {fetchData} from "../../api/DataFetcher";
import FilterOptionsV2, {Filter} from "../Selectors/FilterOptions";
import TimeSelector, {TimeFrame} from "../Selectors/TimeSelect";
import PersistentDataManager from "../../api/DataManager";

const Dashboard: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const {dashboardId, dashboardPath} = useParams<{ dashboardId: string, dashboardPath: string }>();
    const [dashboardData, setDashboardData] = useState<DashboardLayout>(new DashboardLayout("", "", []));
    const [loading, setLoading] = useState(true);
    const [chartData, setChartData] = useState<any[][]>([]);
    const kpiList = dataManager.getKpiList(); // Cache KPI list once
    const [filters, setFilters] = useState(new Filter("All", []));
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({from: new Date(2024, 9, 10), to: new Date(2024, 9, 19), aggregation: 'day'});
    const [isRollbackTime, setIsRollbackTime] = useState(false);

    function handleTimeAdjustments() {
        if (isRollbackTime) {
            console.log("TimeFrame before rollback:", timeFrame);

            const lastDate = new Date(2024, 9, 19); // 19 October 2024
            const databaseStartDate = new Date(2024, 2, 1); // 1 March 2024
            const fromDate = new Date(timeFrame.from);
            const toDate = new Date(timeFrame.to);

            // Validate input dates
            if (isNaN(fromDate.getTime()) || isNaN(toDate.getTime())) {
                throw new Error("Invalid timeFrame dates");
            }

            // Calculate the difference in milliseconds
            const diff = toDate.getTime() - fromDate.getTime();

            // Adjust the 'from' and 'to' dates for rollback
            const newTo = new Date(lastDate); // End date is fixed to 19 October 2024
            const newFrom = new Date(newTo.getTime() - diff); // Shift the range backward

            // Validate 'newFrom' against the database start date
            if (newFrom < databaseStartDate) {
                console.warn("New 'from' date exceeds database start date. Adjusting...");
                // Calculate the difference between the database start date and the adjusted 'from' date
                const adjustedDiff = newTo.getTime() - databaseStartDate.getTime();

                // Adjust the 'to' date by the same difference (i.e., keep the range consistent)
                return {
                    from: databaseStartDate,
                    to: new Date(databaseStartDate.getTime() + adjustedDiff),
                    aggregation: timeFrame.aggregation,
                };
            }

            console.log("TimeFrame after rollback:", {from: newFrom, to: newTo, aggregation: timeFrame.aggregation});
            return {
                from: newFrom,
                to: newTo,
                aggregation: timeFrame.aggregation,
            };
        }
        console.log("TimeFrame without rollback:", timeFrame);

        // No rollback, return original time frame
        return timeFrame;
    }

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

                let timeframe = handleTimeAdjustments();

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
                let timeframe = handleTimeAdjustments();
                return await fetchData(kpi, timeframe, entry.graph_type, filters); // Add appropriate filters
            });

            const resolvedChartData = await Promise.all(chartDataPromises);
            setChartData(resolvedChartData);
        };

        // Avoid fetching during initial loading
        if (!loading) {
            fetchChartData();
        }
    }, [filters, timeFrame, isRollbackTime]);


    if (loading) {
        return <div className="flex justify-center items-center h-screen">
            <div className="text-lg text-gray-600">Loading...</div>
        </div>;
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
};

export default Dashboard;
