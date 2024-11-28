import React from 'react';
import Select from './Select';
import GraphTypeSelector from './GraphTypeSelector';
import FilterOptions from './FilterOptions';
import {getKpiList} from "../../api/PersistentDataManager";
import {KPI} from "../../api/DataStructures";
import KpiSelect from "./KpiSelect";

const chevronDownIcon = "https://cdn.builder.io/api/v1/image/assets/TEMP/ee28ffec5ddc59d7906d5950c4861da7e441f40e4f9a912ad0c4390bc360c6bf?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130";

const KpiSelector: React.FC<{
    kpi: KPI;
    setKpi: (value: KPI) => void;
    timeFrame: string;
    setTimeFrame: (value: string) => void;
    graphType: string;
    setGraphType: (value: string) => void;
    filters: { site: string; productionLine: string; machines: string };
    setFilters: (filters: { site: string; productionLine: string; machines: string }) => void;
    onGenerate: () => void;
}> = ({kpi, setKpi, timeFrame, setTimeFrame, graphType, setGraphType, filters, setFilters, onGenerate}) => {
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
                <Select
                    label="Time Frame"
                    description={`Select the time frame for the data`}
                    value={timeFrame}
                    options={['Day', 'Week', 'Month', 'Year']}
                    onChange={setTimeFrame}
                    iconSrc="https://cdn.builder.io/api/v1/image/assets/TEMP/a3a12f953c8d7c08ea7ca4c1596e4951f443f7d15290e7a565bbdc4fe81127a6?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130"
                />

                {/* Graph Type Selector */}
                <div className="flex items-center justify-center">
                    <GraphTypeSelector value={graphType} onChange={setGraphType}/>
                </div>
            </div>

            {/* Filters Section */}
            <FilterOptions filters={filters} onChange={setFilters}/>

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