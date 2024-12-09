import React, {useEffect, useState} from 'react';
import Chart from '../Chart/Chart';
import {KPI} from "../../api/DataStructures";
import {simulateChartData} from "../../api/QuerySimulator";
import FilterOptions, {Filter} from "../Selectors/FilterOptions";
import {TimeFrame} from "../Selectors/TimeSelect"
import PersistentDataManager from "../../api/PersistentDataManager";
import KpiSelect from "../Selectors/KpiSelect";
import GraphTypeSelector from "../Selectors/GraphTypeSelector";
import AdvancedTimeSelect from "../Selectors/AdvancedTimeSelect";


const KpiSelector: React.FC<{
    kpi: KPI;
    setKpi: (value: KPI) => void;
    timeFrame: TimeFrame;
    setTimeFrame: (value: TimeFrame) => void;
    graphType: string;
    setGraphType: (value: string) => void;
    filters: Filter;
    setFilters: (filters: Filter) => void;
    onGenerate: () => void;
    dataManager: PersistentDataManager;
}> = ({kpi, setKpi, timeFrame, setTimeFrame, graphType, setGraphType, filters, setFilters, onGenerate, dataManager}) => {
    useEffect(() => {
        onGenerate();
    }, [kpi, timeFrame, graphType, filters]); // Dependencies to listen for changes
    return (
        <section className="p-6 mx-auto space-y-10 bg-white shadow-md rounded-lg">
            {/* KPI, Time Frame and Graph Type Selectors in one line */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* KPI Selector */}
                <KpiSelect
                    label="KPI"
                    description={`Select the KPI you want to visualize`}
                    value={kpi}
                    options={dataManager.getKpiList()}
                    onChange={setKpi}
                />

                {/* Time Frame Selector */}
                <AdvancedTimeSelect timeFrame={timeFrame} setTimeFrame={setTimeFrame}/>


                {/* Graph Type Selector */}
                <div className="flex items-center justify-center">
                    <GraphTypeSelector value={graphType} onChange={setGraphType}/>
                </div>
            </div>

            {/* Filters Section */}
            <FilterOptions filter={filters} onChange={setFilters}/>

            {/* Generate Button */}
            <div className="text-center">
                <button
                    onClick={onGenerate}
                    className="bg-blue-500 text-white px-6 py-2 rounded shadow hover:bg-blue-600 transition"
                >
                    Generate Chart
                </button>
            </div>
        </section>
    );
};

const DataView: React.FC = () => {
    const dataManager = PersistentDataManager.getInstance();
    const [kpi, setKpi] = useState<KPI>(dataManager.getKpiList()[0]);
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({
        from: new Date(2024, 3, 1),
        to: new Date(2024, 10, 19),
        aggregation: "month"
    });
    const [graphType, setGraphType] = useState('pie');
    const [filters, setFilters] = useState<Filter>(new Filter('All', []));
    const [chartData, setChartData] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    // Function to fetch chart data with applied filters

    const fetchChartData = async () => {
        try {
            setLoading(true);
            const data = await simulateChartData(kpi, timeFrame, graphType, filters);
            setChartData(data);
        } catch (e) {
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex-1 flex-col w-full h-full space-y-5 p-6 items-center">
            {/* KPI Selector and Generate Button */}
            <KpiSelector
                kpi={kpi}
                setKpi={setKpi}
                timeFrame={timeFrame}
                setTimeFrame={setTimeFrame}
                graphType={graphType}
                setGraphType={setGraphType}
                filters={filters}
                setFilters={setFilters}
                onGenerate={fetchChartData} // Fetch chart data when "Generate" button is clicked
                dataManager={dataManager}
            />

            {/* Chart Section */}

            {loading ? <p>Loading...</p> :
                <div className={` shadow-md p-5 bg-white flex w-auto`}>
                    <Chart data={chartData} graphType={graphType} kpi={kpi} timeUnit={timeFrame.aggregation}/>
                </div>
            }
        </div>
    );
};

export default DataView;