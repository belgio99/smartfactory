import React from 'react';
import {KPI} from "../../api/DataStructures";

interface KPISelectProps {
    label: string;
    description?: string; // General description unrelated to the KPI selected
    value: KPI; // Currently selected KPI
    options: KPI[]; // List of KPI options
    iconSrc?: string;
    onChange: (value: KPI) => void; // Change handler returns the selected KPI object
}

const KpiSelect: React.FC<KPISelectProps> = ({
                                                 label,
                                                 description,
                                                 value,
                                                 options,
                                                 iconSrc,
                                                 onChange,
                                             }) => {
    return (
        <div className="flex flex-col max-w-fit items-start space-y-1">
            {/* Label */}
            <label htmlFor={'kpi_selector'} className="text-base font-medium text-gray-700">{label}</label>

            {/* Optional General Description */}
            {description && <p className="text-sm text-gray-500 font-normal">{description}</p>}

            {/* Select Wrapper */}
            <div className="relative flex-wrap max-w-fit font-normal"> {/* Adjust the width */}
                <div className="relative">
                    <select
                    className="block p-2.5 pl-10 pr-4 text-sm text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
                    value={value.id} // Use `id` as the value to track the selected KPI
                    onChange={(e) => {
                        //console.log(e.target.value);
                        const selectedKpi = options.find((kpi) => kpi.id === Number(e.target.value));
                        if (selectedKpi) {
                            //console.log("Found %s",e.target.value);
                            //console.log(selectedKpi);
                            onChange(selectedKpi); // Pass the selected KPI object
                        }
                    }}
                >
                    {options.map((option: KPI) => (
                        <option key={option.id} value={option.id}>
                            {option.name} {/* Display the KPI name */}
                        </option>
                    ))}
                </select>
                    {/* Optional Icon */}
                    {iconSrc && (
                        <img
                            loading="lazy"
                            src={iconSrc}
                            alt={label}
                            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4" // Smaller size
                        />
                    )}
                </div>

                {/* Selected KPI's Description */}
                {value.description && (
                    <p
                        className="flex-wrap text-start text-sm text-gray-500 font-normal mt-2"
                        style={{
                            wordWrap: 'break-word',
                            overflowWrap: 'break-word',
                            maxWidth: '80%',  // Ensures description doesn't exceed the select box width
                        }}
                    >
                        {value.description}
                    </p>
                )}
            </div>

        </div>
    );
};

export default KpiSelect;
