import React, {useEffect} from 'react';
import Select from './Select';
import GraphTypeSelector from './GraphTypeSelector';
import FilterOptions from './FilterOptions';
import {getKpiList} from "../../api/PersistentDataManager";
import {KPI} from "../../api/DataStructures";
import KpiSelect from "./KpiSelect";
import FilterOptionsV2, {Filter} from "./FilterOptionsV2";
import {TimeFrame} from "./TimeSelector";
import TimeFrameSelector from "./TimeSelectorAdvanced"

const chevronDownIcon = "https://cdn.builder.io/api/v1/image/assets/TEMP/ee28ffec5ddc59d7906d5950c4861da7e441f40e4f9a912ad0c4390bc360c6bf?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130";

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
}> = ({kpi, setKpi, timeFrame, setTimeFrame, graphType, setGraphType, filters, setFilters, onGenerate}) => {
    useEffect(() => {
        onGenerate();
    }, [kpi, timeFrame, graphType]); // Dependencies to listen for changes

    return (
        <section className="p-6 mx-auto space-y-10 bg-white shadow-md rounded-lg">
            {/* KPI, Time Frame and Graph Type Selectors in one line */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* KPI Selector */}
                <KpiSelect
                    label="KPI"
                    description={`Select the KPI you want to visualize`}
                    value={kpi}
                    options={getKpiList()}
                    onChange={setKpi}
                    iconSrc={chevronDownIcon}
                />

                {/* Time Frame Selector */}
                <TimeFrameSelector timeFrame={timeFrame} setTimeFrame={setTimeFrame} />


                {/* Graph Type Selector */}
                <div className="flex items-center justify-center">
                    <GraphTypeSelector value={graphType} onChange={setGraphType}/>
                </div>
            </div>

            {/* Filters Section */}
            <FilterOptionsV2 filter={filters} onChange={setFilters}/>

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

export default KpiSelector;