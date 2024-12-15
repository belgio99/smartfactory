import {TimeFrame} from "../Selectors/TimeSelect";
import React from "react";

export interface FutureTimeFrameSelectorProps {
    timeFrame: { past: TimeFrame; future: TimeFrame; key: string } | null;
    setTimeFrame: ({past, future}: { past: TimeFrame; future: TimeFrame; key: string }) => void;
}

const FutureTimeFrameSelector: React.FC<FutureTimeFrameSelectorProps> = ({timeFrame, setTimeFrame}) => {

    const getFutureTimeFrame = (days: number): TimeFrame => {
        const today = new Date(2024,9,19);
        const from = new Date(today);
        const to = new Date(today.setDate(today.getDate() + days)); // After `days` days
        console.log("Future period:", from, to);
        return {from, to, aggregation: 'day'};
    }

    const getPastTimeFrame = (days: number): TimeFrame => {
        const today = new Date(2024,9,19);
        const to = new Date(today);
        const from = new Date(today.setDate(today.getDate() - days)); // `days` days ago
        console.log("Past period:", from, to);
        return {from, to, aggregation: 'day'};
    }

    const getPastMonthTimeFrame = (): TimeFrame => {
        const today = new Date(2024,9,19);
        const from = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate()); // First day of last month
        const to = today;
        console.log("Past month:", from, to);
        return {from, to, aggregation: 'week'};
    };

    const getFutureMonthTimeFrame = (): TimeFrame => {
        const today = new Date(2024,9,19);
        const from = today;
        const to = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate()); // Same day of next month
        console.log("Future month:", from, to);
        return {from, to, aggregation: 'week'};
    };

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const value = event.target.value;

        if (value === "tomorrow") {
            setTimeFrame({past: getPastTimeFrame(5), future: getFutureTimeFrame(1), key: value});
        } else if (value === "3days") {
            setTimeFrame({past: getPastTimeFrame(5), future: getFutureTimeFrame(3), key: value});
        } else if (value === "5days") {
            setTimeFrame({past: getPastTimeFrame(5), future: getFutureTimeFrame(5), key: value});
        } else if (value === "nextWeek") {
            setTimeFrame({past: getPastTimeFrame(7), future: getFutureTimeFrame(7), key: value});
        } else if (value === "next2Week") {
            setTimeFrame({past: getPastTimeFrame(14), future: getFutureTimeFrame(14), key: value});
        } else if (value === "next3Week") {
            setTimeFrame({past: getPastTimeFrame(21), future: getFutureTimeFrame(21), key: value});
        } else if (value === "nextMonth") {
            setTimeFrame({past: getPastMonthTimeFrame(), future: getFutureMonthTimeFrame(), key: value});
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
                    value={timeFrame ? timeFrame.key : 'none'}
                >
                    {!timeFrame && <option value="none">-- Select --</option>}
                    <option value="tomorrow">Tomorrow</option>
                    <option value="3days">Next 3 Days</option>
                    <option value="5days">Next 5 Days</option>
                    <option value="nextWeek">Next Week</option>
                    <option value="next2Week">Next 2 Weeks</option>
                    <option value="next3Week">Next 3 Weeks</option>
                    <option value="nextMonth">Next Month</option>
                </select>
            </div>
        </div>
    );
};

export default FutureTimeFrameSelector;