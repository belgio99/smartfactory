import React from "react";
import {Line, LineChart, ResponsiveContainer} from "recharts";
import {KPI} from "../../api/DataStructures";

interface TrendProps {
    data: { timestamp: string; value: number }[]; // Time-series data
    kpiName?: KPI; // Name of the KPI (e.g., "Energy Cost")
    timeFrameLabel?: string; // Label for the timeframe (e.g., "Week", "Month")
}

const Trend: React.FC<TrendProps> = ({data, kpiName, timeFrameLabel = "Time Frame"}) => {
    if (!data || data.length < 2) {
        return (
            <p className="text-gray-500 text-center">
                No sufficient data available to compute trends.
            </p>
        );
    }

    // Calculate the current and previous time frame sums/averages
    const currentValue = data[data.length - 1].value;
    const previousValue = data[data.length - 2].value;

    // Calculate the percentage change
    const percentageChange = ((currentValue - previousValue) / previousValue) * 100;
    const isRising = percentageChange > 0;

    // Format percentage
    const formattedPercentage = `${isRising ? "+" : ""}${percentageChange.toFixed(2)}%`;

    return (
        <div className="p-4 border border-gray-300 rounded-lg shadow-sm text-center">
            <h3 className="text-lg font-medium text-gray-700"> Trend</h3>
            <p className="mt-2">
                <span
                    className={`font-bold ${
                        isRising ? "text-green-600" : "text-red-600"
                    }`}
                >
                    {formattedPercentage}
                </span>{" "}
                {isRising ? (
                    <span className="text-green-600">↑ Rising</span>
                ) : (
                    <span className="text-red-600">↓ Falling</span>
                )}
            </p>
            <p className="text-sm text-gray-500 mt-1">Compared to previous {timeFrameLabel}</p>
            {/* Mini line chart as a sparkline */}
            <div className="mt-4">
                <ResponsiveContainer width="100%" height={50}>
                    <LineChart data={data}>
                        <Line
                            type="monotone"
                            dataKey="value"
                            stroke={isRising ? "rgb(34, 197, 94)" : "rgb(239, 68, 68)"}
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Trend;
