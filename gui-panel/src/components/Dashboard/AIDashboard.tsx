import {useLocation} from "react-router-dom";
import {DashboardEntry, DashboardFolder, DashboardLayout} from "../../api/DataStructures";
import React, {useEffect, useState} from "react";
import Chart from "../Chart/Chart";
import {simulateChartData} from "../../api/QuerySimulator";
import FilterOptionsV2, {Filter} from "../Selectors/FilterOptions";
import TimeSelector, {TimeFrame} from "../Selectors/TimeSelect";
import PersistentDataManager from "../../api/PersistentDataManager";

class TemporaryLayout {

    charts: DashboardEntry[]

    constructor(charts: DashboardEntry[]) {
        this.charts = charts;
    }

    // add decoding from Chat
    static fromChat(json: Record<string, any>): TemporaryLayout {
        // the json received is a list of json DashboardEntry objects to decode with the DashboardEntry.decodeChat
        console.log(json);
        const entries: DashboardEntry[] = json.map((entry: Record<string, any>) => DashboardEntry.decodeChat(entry));
        return new TemporaryLayout(entries);
    }

    /**
     * This method saves the layout to a DashboardLayout object
     * @param layout TemporaryLayout - the layout to be saved
     * @param name string - the name of the layout
     * @returns DashboardLayout - the layout to be saved
     */
    static saveToLayout(layout: TemporaryLayout, name: string): DashboardLayout {
        return new DashboardLayout(name.trim().toLowerCase(), name, layout.charts);
    }

}

const AIDashboard: React.FC<{userId: string}> = ({userId}) => {
    const location = useLocation();
    const metadata = location.state?.metadata;

    const dataManager = PersistentDataManager.getInstance();
    const [dashboardData, setDashboardData] = useState<TemporaryLayout>(new TemporaryLayout([]));
    const [loading, setLoading] = useState(true);
    const [chartData, setChartData] = useState<any[][]>([]);
    const kpiList = dataManager.getKpiList(); // Cache KPI list once
    const [filters, setFilters] = useState(new Filter("All", []));
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({from: new Date(), to: new Date(), aggregation: 'hour'});
    const [temporaryName, setTemporaryName] = useState<string>("");
    const [selectedFolder, setSelectedFolder] = useState<string>("");
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    // Set the user ID for the API calls
    dataManager.setUserId(userId);

    //on first data load
    useEffect(() => {
        const fetchDashboardDataAndCharts = async () => {
            try {
                setLoading(true);
                setFilters(new Filter("All", [])); // Reset filters

                // Fetch dashboard data by id
                let dash = TemporaryLayout.fromChat(metadata);

                setDashboardData(dash);

                // Fetch chart data for each view
                const chartDataPromises = dash.charts.map(async (entry: DashboardEntry) => {
                    const kpi = kpiList.find(k => k.id === entry.kpi);
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
    }, [metadata, kpiList]);

    useEffect(() => {
        const fetchChartData = async () => {
            // Ensure promises are created dynamically based on latest dependencies
            const chartDataPromises = dashboardData.charts.map(async (entry: DashboardEntry) => {
                const kpi = kpiList.find(k => k.id === entry.kpi);
                if (!kpi) {
                    console.error(`KPI with ID ${entry.kpi} not found.`);
                    return [];
                }
                return await simulateChartData(kpi, timeFrame, entry.graph_type, filters); // Add appropriate filters
            });

            const resolvedChartData = await Promise.all(chartDataPromises);
            setChartData(resolvedChartData);
        };

        // Avoid fetching during initial loading
        if (!loading) {
            fetchChartData();
        }
    }, [filters, timeFrame]);


    if (loading) {
        return <div className="flex justify-center items-center h-screen">
            <div className="text-lg text-gray-600">Loading...</div>
        </div>;
    }
    return <div className="p-8 space-y-8 bg-gray-50 min-h-screen">
        {/* Disclaimer */}
        <p className="text-base text-gray-500">This is dashboard layout was created with the help of our AI. It will
            need
            to be recreated if not
            saved.</p>

        <div className="flex gap-5 w-fit h-fit">
            {/* Input field for giving the dashboard a name*/}
            <input
                type="text"
                placeholder="Dashboard Name"
                className="flex-grow p-2 border border-gray-200 rounded-lg"
                onChange={(e) => setTemporaryName(e.target.value)}
            />
            {/*Add select for choose the Dashboard folder where to save it*/}
            <select
                className="flex-grow p-2 border border-gray-200 rounded-lg"
                onChange={(e) => setSelectedFolder(e.target.value)}
            >
                {dataManager.getDashboardFolders().map((folder) => (
                    <option key={folder.id} value={folder.id}>
                        {folder.name}
                    </option>
                ))}
            </select>
            {/* Save button */}
            <button
                className="w-fit p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                onClick={
                    () => {

                        // set the dashboard id to a unique id
                        const dashboardTemporaryId = dataManager.getUniqueDashboardId(temporaryName.trim().toLowerCase());
                        const dashboardFolder =  selectedFolder ? dataManager.findDashboardFolderByName(selectedFolder) : null;
                        // Check if the dashboard pointer is null
                        if (!dashboardFolder) {
                            console.error("Dashboard folder not found");
                            setErrorMessage("Dashboard folder not found");
                            return;
                        }
                        // Create a new dashboard layout with (name, id, charts)
                        dataManager.addDashboard(TemporaryLayout.saveToLayout(dashboardData, temporaryName), dashboardFolder);
                        //
                        console.log("Dashboard saved with name:", temporaryName + " and id: " + dashboardTemporaryId);
                    }
                }
            >
                Save Dashboard
            </button>
            {errorMessage && (
                <p className="text-red-500 text-sm mb-2">{errorMessage}</p>
            )}
        </div>

        <h1 className="text-3xl font-extrabold text-center text-gray-800">{temporaryName}</h1>
        <div className="flex space-x-4">
            <div><FilterOptionsV2 filter={filters} onChange={setFilters}/></div>
            <div><TimeSelector timeFrame={timeFrame} setTimeFrame={setTimeFrame}/></div>
        </div>
        {/* Grid Layout */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 items-center w-f">
            {dashboardData.charts.map((entry: DashboardEntry, index: number) => {
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
        <p className="text-base">Note: While the layout is AI-generated from your prompt, data is fetched from the
            database.</p>
    </div>;
};

export default AIDashboard;
