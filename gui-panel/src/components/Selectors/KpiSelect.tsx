import React from 'react';
import Select  from 'react-select';
import { KPI } from "../../api/DataStructures";
const chevronDownIcon = "https://cdn.builder.io/api/v1/image/assets/TEMP/ee28ffec5ddc59d7906d5950c4861da7e441f40e4f9a912ad0c4390bc360c6bf?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130";

interface KPISelectProps {
    label: string;
    description?: string; // General description unrelated to the KPI selected
    value: KPI; // Currently selected KPI
    options: KPI[]; // Flat list of KPI options
    onChange: (value: KPI) => void; // Change handler returns the selected KPI object
}

const KpiSelect: React.FC<KPISelectProps> = ({
                                                 label,
                                                 description,
                                                 value,
                                                 options,
                                                 onChange,
                                             }) => {

    // Define the type for grouped options
    type GroupedOption = {
        label: string;
        options: {
            label: string;
            value: KPI;
        }[];
    };

    // Transform options into grouped format
    const groupedOptions: GroupedOption[] = Object.entries(
        options.reduce((groups, kpi) => {
            if (!groups[kpi.type]) {
                groups[kpi.type] = [];
            }
            groups[kpi.type].push({
                label: kpi.name,
                value: kpi,
            });
            return groups;
        }, {} as Record<string, { label: string; value: KPI }[]>)
    ).map(([type, kpis]) => ({
        label: type,
        options: kpis,
    }));

    return (
        <div className="flex flex-col max-w-fit items-start space-y-1">
            {/* Label */}
            <label htmlFor="kpi_selector" className="text-base font-medium text-gray-700">
                {label}
            </label>

            {/* Optional General Description */}
            {description && <p className="text-sm text-gray-500 font-normal">{description}</p>}

            {/* Select Component */}
            <div className="relative flex-wrap max-w-auto font-normal w-64">
                {(
                    <img
                        loading="lazy"
                        src={chevronDownIcon}
                        alt={label}
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 z-10 pointer-events-none"
                    />
                )}
                <Select
                    id="kpi_selector"
                    options={groupedOptions}
                    value={{ label: value.name, value }}
                    onChange={(selectedOption) => {
                        if (selectedOption?.value) {
                            onChange(selectedOption.value);
                        }
                    }}
                    styles={{
                        control: (base) => ({
                            ...base,
                            paddingLeft: "2rem", // Space for icon
                            borderRadius: '0.375rem', // Tailwind `rounded` equivalent
                            borderColor: '#d1d5db', // Tailwind `border-gray-300`
                        }),
                        dropdownIndicator: (base) => ({
                            ...base,
                            display: 'none', // Hide the dropdown arrow
                        }),
                    }}
                    theme={(theme) => ({
                        ...theme,
                        borderRadius: 8,
                        colors: {
                            ...theme.colors,
                            primary25: "#dbeafe", // Light blue hover
                            primary: "#3b82f6", // Blue selection
                        },
                    })}
                />
            </div>

            {/* Selected KPI's Description */}
            {value.description && (
                <p
                    className="flex-wrap text-start text-sm text-gray-500 font-normal mt-2"
                    style={{
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word',
                        maxWidth: '80%',
                    }}
                >
                    {value.description}
                </p>
            )}
        </div>
    );
};

export default KpiSelect;
