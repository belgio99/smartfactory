import {TimeFrame} from "../Selectors/TimeSelect";
import React from "react";

export interface FutureTimeFrameSelectorProps {
    timeFrame: { past: TimeFrame; future: TimeFrame } | null;
    setTimeFrame: ({past, future}: { past: TimeFrame; future: TimeFrame }) => void;
}

const FutureTimeFrameSelector: React.FC<FutureTimeFrameSelectorProps> = ({timeFrame, setTimeFrame}) => {
    const getPastWeekTimeFrame = (): TimeFrame => {
        const today = new Date();
        const to = new Date(today);
        const from = new Date(today.setDate(today.getDate() - 7)); // 7 days ago
        console.log("Past week:", from, to);
        return {from, to, aggregation: 'day'};
    };

    const getFutureWeekTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today);
        const to = new Date(today.setDate(today.getDate() + 6)); // End of the next week
        console.log("Future week:", from, to);
        return {from, to, aggregation: 'day'};
    };

    const getPastMonthTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today.getFullYear(), today.getMonth() - 1, 1); // First day of last month
        const to = today;
        console.log("Past month:", from, to);
        return {from, to, aggregation: 'week'};
    };

    const getFutureMonthTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = today;
        const to = new Date(today.getFullYear(), today.getMonth() + 1, 0); // Last day of next month
        console.log("Future month:", from, to);
        return {from, to, aggregation: 'week'};
    };

    const getPastYearTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today.getFullYear(), 0, 1); // First day of last year
        const to = today;
        return {from, to, aggregation: 'month'};
    };

    const getFutureYearTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = today;
        const to = new Date(today.getFullYear() + 1, today.getMonth(), 31); // Last day of this month of next year
        return {from, to, aggregation: 'month'};
    };

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const value = event.target.value;

        if (value === "nextWeek") {
            setTimeFrame({past: getPastWeekTimeFrame(), future: getFutureWeekTimeFrame()});
        } else if (value === "nextMonth") {
            setTimeFrame({past: getPastMonthTimeFrame(), future: getFutureMonthTimeFrame()});
        } else if (value === "nextYear") {
            setTimeFrame({past: getPastYearTimeFrame(), future: getFutureYearTimeFrame()});
        }
    };

    return (
        <div className="flex-1 flex-col max-w-fit items-start text-start  space-y-1">
            {/* Label */}
            <label htmlFor="kpi_selector" className="text-base font-medium text-gray-700">
                Select a TimeFrame
            </label>

            {/* Optional General Description */}
            <p className="text-sm text-gray-500 font-normal">
                Choose a time frame for the forecast.
            </p>

            <div className="flex items-center mb-4 space-x-4 font-normal">
                <select
                    className="block w-full h-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                    onChange={handleChange}
                    value={timeFrame ? timeFrame.past.aggregation === 'day' ? 'nextWeek' :
                        timeFrame.past.aggregation === 'week' ? 'nextMonth' : 'nextYear' : 'none'}
                >
                    {!timeFrame && <option value="none">-- Select --</option>}
                    <option value="nextWeek">Next Week</option>
                    <option value="nextMonth">Next Month</option>
                    <option value="nextYear">Next Year</option>
                </select>
            </div>
        </div>
    );
};

export default FutureTimeFrameSelector;