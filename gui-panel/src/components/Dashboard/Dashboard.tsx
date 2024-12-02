import {useParams} from 'react-router-dom';
import React, {useEffect, useState} from "react";
import {DashboardEntry, DashboardLayout} from "../../api/DataStructures";
import Chart from "../Chart/Chart";
import {getKpiList} from "../../api/PersistentDataManager";
import {simulateChartData} from "../../api/QuerySimulator";
import FilterOptionsV2, {Filter} from "../KpiSelector/FilterOptionsV2"; // Import your Chart component
import TimeSelector, {TimeFrame} from "../KpiSelector/TimeSelector";

const Dashboard: React.FC = () => {
    const {dashboardId} = useParams<{ dashboardId: string }>();
    const [dashboardData, setDashboardData] = useState<DashboardLayout>(new DashboardLayout("", "", []));
    const [loading, setLoading] = useState(true);
    const [chartData, setChartData] = useState<any[][]>([]);
    const kpiList = getKpiList(); // Cache KPI list once
    const [filters, setFilters] = useState(new Filter("All", []));
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({from: new Date(), to: new Date(), aggregation: 'hour'});

    //on first data load
    useEffect(() => {
        const fetchDashboardDataAndCharts = async () => {
            try {
                setLoading(true);
                setFilters(new Filter("All", [])); // Reset filters

                // Fetch dashboard layout
                const response = await fetch(`/mockData/dashboards/${dashboardId}.json`);
                const data = await response.json();
                const dash: DashboardLayout = DashboardLayout.decode(data); // Assuming you have a decode method
                setDashboardData(dash);

                // Fetch chart data for each view
                const chartDataPromises = dash.views.map(async (entry: DashboardEntry) => {
                    const kpi = kpiList.find((k) => k.id === Number(entry.kpi));
                    if (!kpi) {
                        console.error(`KPI with ID ${entry.kpi} not found.`);
                        return [];
                    }
                    return await simulateChartData(kpi, timeFrame, entry.graph_type, undefined); // Add appropriate filters
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
                const kpi = kpiList.find((k) => k.id === Number(entry.kpi));
                if (!kpi) {
                    console.error(`KPI with ID ${entry.kpi} not found.`);
                    return [];
                }
                return await simulateChartData(kpi, timeFrame, entry.graph_type, filters); // Add appropriate filters
            });

            console.log("Fetching with timeFrame:", timeFrame); // Debugging output
            const resolvedChartData = await Promise.all(chartDataPromises);
            setChartData(resolvedChartData);
        };

        // Avoid fetching during initial loading
        if (!loading) {
            fetchChartData();
        }
    }, [filters, timeFrame]);


    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="text-lg text-gray-600">Loading...</div>
            </div>
        );
    }
    return (
        <div className="p-8 space-y-8 bg-gray-50 min-h-screen">
            {/* Dashboard Title */}
            <h1 className="text-3xl font-extrabold text-center text-gray-800">{dashboardData.name}</h1>
            <div className="flex space-x-4">
                <div><FilterOptionsV2 filter={filters} onChange={setFilters}/></div>
                <div><TimeSelector timeFrame={timeFrame} setTimeFrame={setTimeFrame}/></div>
            </div>
            {/* Grid Layout */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 items-center w-f">
                {dashboardData.views.map((entry: DashboardEntry, index: number) => {
                    let kpi = kpiList.find((k) => k.id === Number(entry.kpi));
                    if (!kpi) {
                        console.error(`KPI with ID ${entry.kpi} not found.`);
                        return null;
                    }

                    // Determine grid layout based on chart type
                    const isLineChart = entry.graph_type === 'line' || entry.graph_type === 'area';
                    const isSmallCard = entry.graph_type === 'spotlight';

                    // Dynamic grid class
                    const gridClass = isLineChart
                        ? 'col-span-full' // Line/Area charts take full row
                        : isSmallCard
                            ? 'sm:col-span-1 lg:col-span-1' // Small cards fit three in a row
                            : 'col-span-auto '; // Bar and Pie charts share rows;

                    return (
                        <div
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
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default Dashboard;
