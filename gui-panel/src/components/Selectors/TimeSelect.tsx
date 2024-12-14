import React from "react";

// TimeFrame interface with `from` and `to` as Date objects
export interface TimeFrame {
    from: Date;
    to: Date;
    aggregation?: string;
    key?: string;
}

export interface TimeFrameSelectorProps {
    timeFrame: TimeFrame;
    setTimeFrame: (value: TimeFrame) => void;
}

const TimeFrameSelector: React.FC<TimeFrameSelectorProps> = ({timeFrame, setTimeFrame}) => {
    const getTodayTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today.setHours(0, 0, 0, 0)); // Set to midnight
        const to = new Date(); // Current time
        return {from, to, aggregation: 'hour', key: 'today'};
    };

    const getRecentDays = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today.setDate(today.getDate() - 4)); // 4 days ago
        const to = new Date(); // Current time
        return {from, to, aggregation: 'day', key: 'last3Days'};
    }

    const getThisWeekTimeFrame = (): TimeFrame => {
        const today = new Date();
        const from = new Date(today.setDate(today.getDate() - 6)); // First day of the week
        const to = new Date(); // Current time
        return {from, to, aggregation: 'day', key: 'thisWeek'};
    }

    const getThisMonthTimeFrame = (): TimeFrame => {
        const today = new Date();

        let from = new Date(today.getFullYear(), today.getMonth(), 1); // First day of the current month
        let to = today;

        if (today.getDate() === 1) {
            to = new Date(today.getFullYear(), today.getMonth(), 0); // Last day of the previous month
            from = new Date(today.getFullYear(), today.getMonth() - 1, 1); // First day of the previous month
            return {
                from, // First day of the previous month
                to,   // Last day of the previous month
                aggregation: 'day', key: 'thisMonth'
            };
        }

        return {from, to, aggregation: 'day', key: 'thisMonth'}; // Otherwise, use current month
    };

    const getThisYearTimeFrame = (): TimeFrame => {
        const today = new Date();
        let from = new Date(today.getFullYear(), 0, 1); // First day of the current year
        let to = today;

        if (today.getMonth() === 0 && today.getDate() === 1) {
            // If today is the 1st of January, set the time frame to the previous year
            return {
                from: new Date(today.getFullYear() - 1, 0, 1), // First day of the previous year
                to: new Date(today.getFullYear() - 1, 11, 31), // Last day of the previous year
                aggregation: 'month', key: 'thisYear'
            };
        }

        return {from, to, aggregation: 'month', key: 'thisYear'}; // Otherwise, use current year
    };

    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const value = event.target.value;
        console.log("Selected Timeframe:", value);
        console.log("Old Timeframe:", timeFrame);
        if (value === "today") {
            setTimeFrame(getTodayTimeFrame());
        } else
        if (value === "last3Days") {
            setTimeFrame(getRecentDays());
        } else if (value === "thisWeek") {
            setTimeFrame(getThisWeekTimeFrame());
        } else if (value === "thisMonth") {
            setTimeFrame(getThisMonthTimeFrame());
        } else if (value === "thisYear") {
            setTimeFrame(getThisYearTimeFrame());
        }
    };

    return (
        <div className="max-h-fit max-w-fit">
            <div className="flex justify-between items-center mb-4">
                <div className="text-sm font-semibold text-gray-700">Select Timeframe</div>
            </div>

            <div className="flex items-center mb-4 space-x-4 font-normal">
                <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium text-gray-700">Time Period:</label>
                    <select
                        className="block w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                        onChange={handleChange}
                        value={timeFrame ? timeFrame.key : ''}
                    >
                        <option value="last3Days">Last 3 days</option>
                        <option value="thisWeek">This Week</option>
                        <option value="thisMonth">This Month</option>
                        <option value="thisYear">This Year</option>
                    </select>
                </div>
            </div>
        </div>
    );
};
export default TimeFrameSelector;
