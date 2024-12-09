import React, {useState} from "react";
import PersistentDataManager from "../../api/PersistentDataManager";

const KpiViewer = () => {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const [expanded, setExpanded] = useState<string | null>(null);

    const toggleAccordion = (id: string) => {
        setExpanded((prev) => (prev === id ? null : id));
    };

    const kpiList = PersistentDataManager.getInstance().getKpiList();

    const filteredAndSortedKpis = kpiList
        .filter((kpi) =>
            kpi.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            kpi.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
            kpi.description.toLowerCase().includes(searchTerm.toLowerCase())
        );

    return (
        <div className="KpiViewer max-w-4xl mx-auto p-6 bg-gray-25 rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Your KPIs</h1>
            <h2 className="text-sm font-semibold mb-4 text-gray-800">
                Here you can view all the KPIs you have available.
                If you want to add a new KPI, please ask to the AI Chat Assistant.
            </h2>
            <div className="mb-4 flex-1 sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                <input
                    type="text"
                    placeholder="Search KPI by name, type, or description..."
                    className="p-2 border border-gray-300 rounded-lg shadow-sm w-full sm:w-1/2"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            <div className="space-y-4">
                {filteredAndSortedKpis.map((kpi) => (
                    <div
                        key={kpi.id}
                        className="bg-white border border-gray-200 rounded-lg shadow-sm"
                    >
                        <div
                            className="flex items-center justify-between p-4 cursor-pointer"
                            onClick={() => toggleAccordion(kpi.id)}
                        >
                            <div className="flex items-center">
                                <span className="font-medium text-gray-800">{kpi.name}</span>
                                {kpi.forecastable && (
                                    <img
                                        src="/icons/forecast.svg"
                                        alt="Forecasting Icon"
                                        className="ml-2 w-4 h-4" // Aggiusta le dimensioni e il margine a tuo piacimento
                                    />
                                )}
                            </div>
                            <span className="text-gray-600 text-sm">{kpi.type}</span>
                        </div>
                        {expanded === kpi.id && (
                            <div className="p-4  text-start border-t border-gray-200 font-semibold">
                                <p className="mb-2 text-base ">{kpi.description}</p>
                                <p className="text-sm text-gray-500">
                                    Metric Used: {kpi.unit}
                                </p>
                                <p className="text-sm text-gray-500">
                                    {kpi.forecastable ? "This KPI supports Forecasting features" : "Forecasting features are not available for this KPI"}
                                </p>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default KpiViewer;
