import React from 'react';
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer, Scatter, ScatterChart,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';
import {KPI} from "../../api/DataStructures";
import Trend from "./Trend";

const getColor = (value: number, min: number, max: number) => {
    // Define a simple color gradient from blue to red based on value
    const ratio = (value - min) / (max - min);
    const r = Math.round(255 * ratio);
    const g = Math.round(255 * (1 - ratio));
    const b = 255 - r;

    return `rgb(${r},${g},${b})`;
};

interface ChartProps {
    data: any[],
    graphType: string,
    kpi?: KPI,
    timeUnit?: string
}

//various colors for the charts
const COLORS = ['#8884d8', '#83a6ed', '#8dd1e1', '#82ca9d',
    '#a4de6c', '#d0ed57', '#ffc658', '#ffc658',
    '#ff9e58', '#ff6058', '#ff58b2', 'rgba(193,8,253,0.87)'];

// Helper function to format date as 'HH:mm' for hours, 'DD' for days, 'MMM' for months
const formatTimeFrame = (timestamp: string, timeUnit?: string): string => {
    const date = new Date(timestamp);

    switch (timeUnit) {
        case 'hour':
            return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`; // HH:mm
        case 'day':
            return `${String(date.getDate()).padStart(2, '0')}`; // DD (day of the month plus month name)
        case 'month':
            return `${date.toLocaleString('default', {month: 'short'})}`; // MMM (Month abbreviation)
        default:
            return date.toLocaleString(); // fallback
    }
};

const DrillDownTooltip = ({active, payload, label, kpi}: any) => {
    if (active && payload && payload.length) {

        let name: string = payload[0].payload.name ? payload[0].payload.name : payload[0].name
        return (
            <div
                style={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    padding: '10px',
                    borderRadius: '4px',
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                }}
            >
                <p style={{
                    color: payload.fill,
                    margin: 0,
                    fontWeight: 'normal'
                }}>{`${name}: ${payload[0].value} ${kpi?.unit || ''}`}</p>
            </div>
        );
    }
    return null;
};

const ScatterTooltip = ({active, payload, kpi}: any) => {
    if (active && payload && payload.length) {
        const dataPoint = payload[0].payload; // Access the data point
        const formattedDate = new Date(dataPoint.x).toLocaleString(); // Format the date
        return (
            <div
                style={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    padding: '10px',
                    borderRadius: '4px',
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                }}
            >
                <p style={{margin: 0, fontWeight: 'bold'}}>{formattedDate}</p>
                <p
                    style={{
                        color: dataPoint.color, // Use the scatter dot color
                        margin: 0,
                    }}
                >
                    {`${dataPoint.machineId}: ${dataPoint.y.toFixed(2)} ${
                        kpi?.unit || ''
                    }`}
                </p>
            </div>
        );
    }
    return null;
};

const LineTooltip = ({active, payload, label, kpi}: any) => {
    if (active && payload && payload.length) {

        return (
            <div
                style={{
                    backgroundColor: '#fff',
                    border: '1px solid #ccc',
                    padding: '10px',
                    borderRadius: '4px',
                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
                }}
            >
                <p style={{margin: 0, fontWeight: 'bold'}}>{formatTimeFrame(label)}</p>
                {payload.map((entry: any, index: number) => (
                    <p
                        key={`tooltip-${index}`}
                        style={{
                            margin: 0,
                            color: entry.stroke, // Match the line's color
                        }}
                    >
                        {`${entry.name}: ${entry.value.toFixed(2)} ${kpi?.unit || ''}`}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

const Chart: React.FC<ChartProps> = ({data, graphType, kpi, timeUnit = 'day'}) => {
    if (!data || data.length === 0) {
        return (
            <p style={{textAlign: 'center', marginTop: '20px', color: '#555'}}>
                No data available. Please select options and click "Generate Chart".
            </p>
        );
    }

    switch (graphType) {
        case 'barv': // Vertical Bar Chart
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis dataKey="name" tick={{fill: '#666'}}/>
                        <YAxis tick={{fill: '#666'}}/>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                        <Legend/>
                        <Bar dataKey="value" fill="#8884d8" radius={[10, 10, 0, 0]}/>
                    </BarChart>
                </ResponsiveContainer>
            );
        case 'barh': // Horizontal Bar Chart
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={data} layout='vertical'>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis type="number" tick={{fill: '#666'}}/>
                        <YAxis type="category" dataKey="name" tick={{fill: '#666'}}/>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                        <Legend/>
                        <Bar dataKey="value" fill="#8884d8" radius={[0, 10, 10, 0]}/>
                    </BarChart>
                </ResponsiveContainer>
            );
        case 'line':
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            dataKey="timestamp"
                            tick={{fill: '#666'}}
                            tickFormatter={(d) => formatTimeFrame(d, timeUnit)}  // Apply the custom formatting
                        />
                        <YAxis tick={{fill: '#666'}}/>
                        <Tooltip content={<LineTooltip kpi={kpi}/>} trigger={"hover"}/>
                        <Legend/>
                        {Object.keys(data[0] || {})
                            .filter((key) => key !== 'timestamp') // Exclude the timestamp key
                            .map((machine, index) => (
                                <Line
                                    key={machine}
                                    type="monotone"
                                    dataKey={machine} // Use the machine's name as the key
                                    stroke={COLORS[index % COLORS.length]}
                                    strokeWidth={2}
                                    dot={{r: 5}}
                                    activeDot={{r: 8}}
                                    name={machine}
                                />
                            ))}
                    </LineChart>
                </ResponsiveContainer>
            );
        case 'area':
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            dataKey="timestamp"
                            tick={{fill: '#666'}}
                            tickFormatter={(d) => formatTimeFrame(d, timeUnit)}  // Apply the custom formatting
                        />
                        <YAxis tick={{fill: '#666'}}/>
                        <Tooltip content={<LineTooltip kpi={kpi}/>} trigger={"hover"}/>
                        <Legend/>
                        {Object.keys(data[0] || {}).filter((key) => key !== 'timestamp')
                            .map((machine, index) => (
                                <Area
                                    key={machine}
                                    type="monotone"
                                    dataKey={machine}
                                    stroke={COLORS[index % COLORS.length]}
                                    fill={COLORS[index % COLORS.length]}
                                    fillOpacity={0.3}
                                    name={machine}
                                />
                            ))}
                    </AreaChart>
                </ResponsiveContainer>
            );
        case 'pie':
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                        <Pie
                            data={data}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={120}
                            fill="#8884d8"
                            label={(entry) => `${entry.name}`}
                        >
                            {data.map((_entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]}/>
                            ))}
                        </Pie>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                    </PieChart>
                </ResponsiveContainer>
            );
        case 'trend':
            return (
                <Trend
                    data={data} kpiName={kpi} timeFrameLabel='Time Frame'
                />
            )
        case "hist":
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                        data={data}
                        margin={{top: 20, right: 20, bottom: 20, left: 20}}
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            dataKey="bin"
                            tick={{fill: "#666"}}
                            label={{
                                value: "Bins",
                                position: "insideBottom",
                                offset: -10,
                                fill: "#666",
                            }}
                        />
                        <YAxis
                            tick={{fill: "#666"}}
                            label={{
                                value: "Frequency",
                                angle: -90,
                                position: "insideLeft",
                                fill: "#666",
                            }}
                        />
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                        <Bar dataKey="value" fill="#8884d8" name="Frequency"/>
                    </BarChart>
                </ResponsiveContainer>
            );
        case "donut":
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                        <Pie
                            data={data.filter((entry) => entry.name !== "Total")} // Exclude "Total" from slices
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={120}
                            innerRadius={60} // Creates the donut hole
                            fill="#8884d8"
                            label={(entry) => `${entry.name}: ${entry.value}`}
                        >
                            {data.map((_entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]}/>
                            ))}
                        </Pie>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                        {/* Custom Total Label */}
                        <text
                            x="50%"
                            y="50%"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            style={{fontSize: "16px", fontWeight: "bold", fill: "#333"}}
                        >
                            {`Total: ${
                                data.find((entry) => entry.name === "Total")?.value || "N/A"
                            }`}
                        </text>
                    </PieChart>
                </ResponsiveContainer>
            );
        case "stacked_bar":
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            dataKey="timestamp"
                            tick={{fill: '#666'}}
                            tickFormatter={(d) => formatTimeFrame(d, timeUnit)}  // Apply the custom formatting
                        />
                        <YAxis tick={{fill: "#666"}}/>
                        <Tooltip content={<LineTooltip kpi={kpi}/>} trigger={"hover"}/>
                        <Legend/>
                        {data.length > 0 &&
                            Object.keys(data[0])
                                .filter((key) => key !== "timestamp")
                                .map((machine, index) => (
                                    <Bar
                                        key={machine}
                                        dataKey={machine}
                                        stackId="a"
                                        stroke={COLORS[index % COLORS.length]}
                                        fill={COLORS[index % COLORS.length]}
                                    />
                                ))}
                    </BarChart>
                </ResponsiveContainer>
            );
        case "scatter":
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart margin={{top: 20, right: 20, bottom: 20, left: 20}}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            dataKey="x"
                            type="number"
                            domain={['dataMin', 'dataMax']}
                            tick={{fill: '#666'}}
                            tickFormatter={(d) => formatTimeFrame(d, timeUnit)}  // Apply the custom formatting
                        />
                        <YAxis
                            dataKey="y"
                            type="number"
                            tick={{fill: '#666'}}
                            domain={['dataMin', 'dataMax']}
                            tickFormatter={(value) => value.toFixed(2)} // Precision limited to 2 decimal places
                        />
                        <Tooltip content={<ScatterTooltip kpi={kpi}/>}/>
                        <Legend/>
                        {Object.keys(data[0] || {})
                            .filter((key) => key !== 'timestamp') // Exclude timestamp key
                            .map((machine, index) => {
                                const machineData = data.map((entry) => ({
                                    x: new Date(entry.timestamp).getTime(), // X-axis: Timestamp
                                    y: entry[machine],                      // Y-axis: Machine value
                                    machineId: machine,                     // Additional info
                                    color: COLORS[index % COLORS.length],    // Scatter dot color
                                }));
                                return (
                                    <Scatter
                                        key={machine}
                                        name={machine}
                                        data={machineData}
                                        fill={COLORS[index % COLORS.length]}
                                        shape="circle"
                                    />
                                );
                            })}
                    </ScatterChart>
                </ResponsiveContainer>
            );
        case "heatmap":
            const timePeriods = data.map((entry) => entry.timestamp); // Extract timestamps dynamically
            const machines = Object.keys(data[0] || {}).filter((key) => key !== "timestamp"); // Extract machine IDs

            // Get the min and max values from your dataset for dynamic color scaling
            const allValues = data.flatMap((entry) => Object.values(entry).filter((value) => typeof value === 'number') as number[]);
            const minValue = Math.min(...allValues);
            const maxValue = Math.max(...allValues);

            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                        data={data}
                        layout="vertical"
                        barCategoryGap={1} // Minimize gaps between rows for grid-like effect
                    >
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis
                            type="category"
                            dataKey="timestamp" // Map X-axis to extracted timestamps
                            tickFormatter={(d) => formatTimeFrame(d)} // Custom formatting
                            tick={{fill: "#666"}}
                        />
                        <YAxis
                            type="category"
                            dataKey="machineId"
                            tick={{fill: "#666"}}
                            width={100}
                        />
                        <Tooltip
                            content={<DrillDownTooltip kpi={kpi}/>}
                        />
                        {machines.map((machine, machineIndex) => (
                            <Bar key={machine} dataKey={machine} fillOpacity={1}>
                                {data.map((entry, idx) => {
                                    const value = entry[machine];
                                    return (
                                        <Cell key={`cell-${idx}`} fill={getColor(value, minValue, maxValue)}/>
                                    );
                                })}
                            </Bar>
                        ))}
                    </BarChart>
                </ResponsiveContainer>
            );

        default:
            return (
                <p style={{textAlign: 'center', marginTop: '20px', color: '#555'}}>
                    Unsupported graph type.
                </p>
            );
    }
};

export default Chart;
