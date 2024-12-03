import React, { useState } from 'react';
import {TimeFrameSelectorProps} from "./TimeSelector";
const TimeFrameSelector: React.FC<TimeFrameSelectorProps> = ({ timeFrame, setTimeFrame }) => {
    const [startDate, setStartDate] = useState<string>(timeFrame.from.toISOString().split('T')[0]); // Initialize with `from`
    const [endDate, setEndDate] = useState<string>(timeFrame.to.toISOString().split('T')[0]); // Initialize with `to`

    const updateAggregation = (from: Date, to: Date): string => {
        const diffInMs = to.getTime() - from.getTime();
        const diffInDays = diffInMs / (1000 * 60 * 60 * 24);

        if (diffInDays > 90) return 'month';
        if (diffInDays > 30) return 'day';
        return 'hour';
    };

    const handleStartDateChange = (newStartDate: string) => {
        const from = new Date(newStartDate);
        const to = new Date(endDate);

        // Adjust `to` if `from` is after it
        if (from >= to) {
            to.setDate(from.getDate() + 1); // Set `to` to one day after `from`
            setEndDate(to.toISOString().split('T')[0]);
        }

        const aggregation = updateAggregation(from, to);
        setTimeFrame({ from, to, aggregation });
        setStartDate(newStartDate);
    };

    const handleEndDateChange = (newEndDate: string) => {
        const from = new Date(startDate);
        const to = new Date(newEndDate);

        // Adjust `from` if `to` is before it
        if (to <= from) {
            from.setDate(to.getDate() - 1); // Set `from` to one day before `to`
            setStartDate(from.toISOString().split('T')[0]);
        }

        const aggregation = updateAggregation(from, to);
        setTimeFrame({ from, to, aggregation });
        setEndDate(newEndDate);
    };

    return (
        <div className="max-h-fit max-w-fit">
            <div className="flex-col justify-center items-center mb-4">
                {/* Label */}
                <label className="text-base font-medium text-gray-700">Timeframe</label>
                <div className="text-sm text-gray-500 font-normal">Select Timeframe</div>
            </div>

            <div className="flex flex-col space-y-4 font-normal">
                <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium text-gray-700">Start Date:</label>
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => handleStartDateChange(e.target.value)}
                        className="block w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                    />
                </div>

                <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium text-gray-700">End Date:</label>
                    <input
                        type="date"
                        value={endDate}
                        onChange={(e) => handleEndDateChange(e.target.value)}
                        className="block w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                    />
                </div>
            </div>
        </div>
    );
};

export default TimeFrameSelector;
