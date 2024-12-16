import React, {useState} from "react";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ReferenceLine,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from "recharts";
import {ForecastDataEx, KPI} from "../../api/DataStructures";
import {COLORS, formatTimeFrame} from "../../utils/chartUtil";

const ForecastTooltip = ({active, payload, label, kpi}: any) => {
    if (active && payload && payload.length) {
        // Variable to store the confidence value (which is the same for all three lines)
        let confidence: number = payload[0].payload.confidenceScore;
        if (confidence) {
            // Remove the confidence value from the payload
            confidence *= 100; // Convert to percentage
        }
        return <div
            style={{
                backgroundColor: '#fff',
                border: '1px solid #ccc',
                padding: '10px',
                borderRadius: '4px',
                boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
            }}
        >
            <p style={{margin: 0, fontWeight: 'bold'}}>{formatTimeFrame(label)}</p>

            {/* Display the machine data (predicted, upper, and lower bounds) */}
            {payload.map((entry: any, index: number) => {
                return <p
                    key={`tooltip-${index}`}
                    style={{
                        margin: 0,
                        color: entry.stroke, // Match the line's color
                    }}
                >
                    {`${entry.name}: ${entry.value.toFixed(2)} ${kpi?.unit || ''}`}
                </p>;
            })}

            {/* Show the confidence value only once */}
            {confidence && <div style={{marginTop: '10px', fontStyle: 'italic', color: '#666'}}>
                <p>{`Confidence: ${confidence.toFixed(2)}%`}</p>
            </div>}
        </div>;
    }
    return null;
};

interface ForeChartProps {
    pastData: any[];
    futureDataEx: ForecastDataEx;
    kpi: KPI | null;
    timeUnit?: string;
    timeThreshold?: number;
}

const ForeChart: React.FC<ForeChartProps> = ({
                                                 pastData,
                                                 futureDataEx,
                                                 kpi,
                                                 timeUnit = "day",
                                             }) => {
    const [selectedPoint, setSelectedPoint] = useState<number | null>(null);

    const explanationData = futureDataEx?.limeExplanation;
    const futureData = futureDataEx?.toChartData() || [];

    // remaps historical data to match the chart data format
    function transformPastData(
        pastData: any[],
        machineName: string
    ): { timestamp: string; value: number; }[] {
        return pastData.map((entry) => {
            const value = entry[machineName];
            return {
                timestamp: entry.timestamp,
                value: value,
            };
        });
    }

    const machineKey = futureDataEx?.machineName || "Machine";
    pastData = transformPastData(pastData, machineKey);
    const data = [...pastData, ...futureData];

    if (!data || data.length === 0) {
        return <p style={{textAlign: "center", marginTop: "20px", color: "#555"}}>
            No data available. Please select options and click "Generate Chart".
        </p>;
    }

    const handleLineClick = (pointIndex: number) => {
        setSelectedPoint(pointIndex - breakpoint);
    };

    const selectedExplanationData =
        selectedPoint !== null && explanationData && explanationData[selectedPoint]
            ? explanationData[selectedPoint]
            : null;

    const maxAbsValue = selectedExplanationData ? Math.max(
        ...selectedExplanationData.map((d: { feature: string; importance: number; }) => Math.abs(d.importance))
    ) : 0;

    const breakpoint = pastData.length; // point to the last past data point
    return <div>
        {/* Forecasting Chart */}
        <ResponsiveContainer width="100%" height={400}>
            <LineChart
                data={data}
                onClick={(e: any) => {
                    if (e && e.activeTooltipIndex !== undefined) {
                        handleLineClick(e.activeTooltipIndex);
                    }
                }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                <XAxis
                    dataKey="timestamp"
                    tick={{fill: "#666"}}
                    tickFormatter={d => formatTimeFrame(d, timeUnit)}
                />
                <YAxis tick={{fill: "#666"}}/>
                <Tooltip content={<ForecastTooltip kpi={kpi}/>} trigger={"hover"}/>
                {data.length > 0 && <ReferenceLine
                    x={data[breakpoint-1].timestamp}
                    stroke="red"
                    label="Today"
                />}
                <Legend/>
                {/* Main Line for the Machine */}
                <Line
                    key={machineKey}
                    type="monotone"
                    dataKey={"value"}
                    stroke={COLORS[0]} // Assuming only one machine, use the first color
                    strokeWidth={2}
                    dot={{r: 5}}
                    activeDot={{r: 8}}
                    name={machineKey}
                />

                {/* Upper Bound Line */}
                <Line
                    key={`UpperBound`}
                    type="monotone"
                    dataKey={`upperBound`}
                    stroke="#82ca9d"
                    strokeWidth={1.5}
                    strokeDasharray="5 5"
                    name={`Upper Bound`}
                />

                {/* Lower Bound Line */}
                <Line
                    key={`LowerBound`}
                    type="monotone"
                    dataKey={`lowerBound`}
                    stroke="#8884d8"
                    strokeWidth={1.5}
                    strokeDasharray="5 5"
                    name={`Lower Bound`}
                /> </LineChart>
        </ResponsiveContainer>
        {/* Explanation Chart */}
        {selectedExplanationData && selectedPoint !== null ? <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-800">
                    Explanation of prediction for date: {formatTimeFrame(data[selectedPoint + breakpoint].timestamp,)}
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart
                        data={selectedExplanationData}
                        layout="vertical"
                        margin={{top: 20, right: 20, left: 20, bottom: 20}}
                    >
                        <CartesianGrid strokeDasharray="3 3"/>
                        <XAxis
                            type="number"
                            tick={{fill: "#666"}}
                            domain={[-maxAbsValue * 1.1, maxAbsValue * 1.1]} // Adds 10% padding
                        />
                        <ReferenceLine x={0} stroke="#000"/>

                        <YAxis
                            type="category"
                            dataKey="feature"
                            tick={{fill: "#666"}}
                            width={150}
                        />
                        <Tooltip/>
                        <Legend/>
                        <Bar
                            dataKey="importance"
                            fill={COLORS[0]}
                            isAnimationActive={false}
                            name="Importance"
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
            :
            <div>
                {/* Prompt the user to click on a predicted point to see the explanation */}
                <div className="mt-4 text-center text-gray-600">
                    <p className="text-base">Click on a predicted point to see the
                        explanation. </p>
                    <p className="text-base">Hover to see the forecasted values, bounds and
                        confidence. </p>
                </div>
            </div>}
    </div>;
};

export default ForeChart;
