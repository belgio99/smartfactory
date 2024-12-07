import React, {useState} from "react";
import {
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ReferenceLine,
    BarChart,
    Bar
} from "recharts";
import {KPI} from "../../api/DataStructures";
import {COLORS, formatTimeFrame} from "../../utils/chartUtil";

const ForecastTooltip = ({active, payload, label, kpi}: any) => {
    if (active && payload && payload.length) {
        // Variable to store the confidence value (which is the same for all three lines)
        let confidence: number = payload[0].payload.confidence;
        console.log(payload[0].payload, payload[0].payload.confidence);
        console.log("Confidence: ", confidence);
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
            {<div style={{marginTop: '10px', fontStyle: 'italic', color: '#666'}}>
                <p>{`Confidence: ${confidence.toFixed(2)}%`}</p>
            </div>}
        </div>;
    }
    return null;
};

interface ForeChartProps {
    data: any[];
    kpi: KPI | null;
    timeUnit?: string;
    timeThreshold?: number;
    explanationData?: any[];
}

const ForeChart: React.FC<ForeChartProps> = ({
                                                 data,
                                                 kpi,
                                                 timeUnit = "day",
                                                 explanationData,
                                             }) => {
    const [selectedPoint, setSelectedPoint] = useState<number | null>(null);

    if (!data || data.length === 0) {
        return <p style={{textAlign: "center", marginTop: "20px", color: "#555"}}>
            No data available. Please select options and click "Generate Chart".
        </p>;
    }

    const handleLineClick = (pointIndex: number) => {
        setSelectedPoint(pointIndex);
    };

    const selectedExplanationData =
        selectedPoint !== null && explanationData && explanationData[selectedPoint]
            ? explanationData[selectedPoint]
            : null;

    const maxAbsValue = selectedExplanationData ? Math.max(
        ...selectedExplanationData.map((d: { feature: string; importance: number; }) => Math.abs(d.importance))
    ) : 0;

    const halfLength = Math.floor(data.length / 2);
    const dataWithBounds = data.map((point, index) => {
        const newPoint = {...point};

        // Loop through each machine in the point
        Object.keys(point).forEach(key => {
            if (key !== "timestamp" && key !== "confidence") {
                const machineValue = point[key];
                // Apply ±20% margin for the bounds starting from the second half
                newPoint[`${key} UpperBound`] = index >= halfLength ? machineValue * 1.2 : null;
                newPoint[`${key} LowerBound`] = index >= halfLength ? machineValue * 0.8 : null;
            }
        });

        return newPoint;
    });

    return <div>
        {/* Forecasting Chart */}
        <ResponsiveContainer width="100%" height={400}>
            <LineChart
                data={dataWithBounds}
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
                    x={data[halfLength].timestamp}
                    stroke="red"
                    label="Today"
                />}
                <Legend/>
                {Object.keys(data[0] || {})
                    .filter(key => key !== "timestamp" && key !== "confidence") // Exclude the timestamp key
                    .map((machine, index) => <Line
                        key={machine}
                        type="monotone"
                        dataKey={machine}
                        stroke={COLORS[index % COLORS.length]}
                        strokeWidth={2}
                        dot={{r: 5}}
                        activeDot={{r: 8}}
                        name={machine}
                    />)}

                {/* Upper Bound Line */}
                {/* Upper Bound Lines for Each Machine */}
                {Object.keys(data[0] || {}).map((key, index) => {
                    if (key !== "timestamp" && key !== "confidence") {
                        return <Line
                            key={`${key}UpperBound`}
                            type="monotone"
                            dataKey={`${key} UpperBound`}
                            stroke="#82ca9d"
                            strokeWidth={1.5}
                            strokeDasharray="5 5"
                            name={`${key} Upper Bound`}
                        />;
                    }
                    return null;
                })}

                {/* Lower Bound Lines for Each Machine */}
                {Object.keys(data[0] || {}).map((key, index) => {
                    if (key !== "timestamp" && key !== "confidence") {
                        return <Line
                            key={`${key}LowerBound`}
                            type="monotone"
                            dataKey={`${key} LowerBound`}
                            stroke="#8884d8"
                            strokeWidth={1.5}
                            strokeDasharray="5 5"
                            name={`${key} Lower Bound`}
                        />;
                    }
                    return null;
                })}
            </LineChart>
        </ResponsiveContainer>
        {/* Explanation Chart */}
        {selectedExplanationData && <div className="mt-4">
            <h3 className="text-lg font-semibold mb-2 text-gray-800">
                Explanation for Selected Point
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
        </div>}
    </div>;
};

export default ForeChart;
