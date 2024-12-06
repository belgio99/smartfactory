import React from 'react';

interface SelectProps {
    label: string;
    description?: string; // Made optional
    value: string;
    options: string[];
    iconSrc?: string; // Made optional
    onChange: (value: string) => void;
}

const Select: React.FC<SelectProps> = ({ label, description, value, options, iconSrc, onChange }) => {
    return (
        <div className="flex flex-col items-start space-y-1">
            {/* Label */}
            <label className="text-base font-medium text-gray-700">{label}</label>

            {/* Optional Description */}
            {description && <p className="text-sm text-gray-500 font-normal">{description}</p>}

            {/* Select Wrapper */}
            <div className="relative max-w-52 font-normal"> {/* Adjust the width */}
                <select
                    className="block w-full p-2.5 pl-10 pr-4 text-sm text-gray-700 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                >
                    {options.map((option, index) => (
                        <option key={index} value={option}>
                            {option}
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
        </div>
    );
};

export default Select;
