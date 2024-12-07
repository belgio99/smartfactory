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
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';
import {KPI} from "../../api/DataStructures";
import Trend from "./Trend";
import {COLORS, formatTimeFrame, getColor} from "../../utils/chartUtil";

interface ChartProps {
    data: any[],
    graphType: string,
    kpi?: KPI,
    timeUnit?: string
    timeThreshold?: boolean
}

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
                        <XAxis
                            dataKey="name"
                            tick={{fill: '#666', fontSize: 14}}
                            angle={-30} // Rotate the labels by -30 degrees
                            textAnchor="end" // Align text at the end of each label
                            height={80} // Add space for the tilted labels
                        />
                        <YAxis tick={{fill: '#666'}}/>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
                        <Bar dataKey="value" fill="#8884d8" radius={[10, 10, 0, 0]}/>
                    </BarChart>
                </ResponsiveContainer>
            );
        case 'barh': // Horizontal Bar Chart
            return (
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={data} layout='vertical' margin={{left: 25}}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0"/>
                        <XAxis type="number" tick={{fill: '#666'}}/>
                        <YAxis type="category" dataKey="name" tick={{fill: '#666', fontSize: 14, textAnchor: 'end'}}/>
                        <Tooltip content={<DrillDownTooltip kpi={kpi}/>}/>
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
                        <Legend
                            content={(props) => (
                                <ul style={{padding: 0, margin: 0}}>
                                    {props.payload && props.payload.map((entry, index) => (
                                        <li key={index} style={{display: 'inline-block', marginRight: 10}}>
                                            <span style={{color: entry.color}}>●</span> {entry.value.substring(0, 5)}...
                                        </li>
                                    ))}
                                </ul>
                            )}
                        /> {Object.keys(data[0] || {})
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
                        <Legend
                            content={(props) => (
                                <ul style={{padding: 0, margin: 0}}>
                                    {props.payload && props.payload.map((entry, index) => (
                                        <li key={index} style={{display: 'inline-block', marginRight: 10}}>
                                            <span style={{color: entry.color}}>●</span> {entry.value.substring(0, 5)}...
                                        </li>
                                    ))}
                                </ul>
                            )}
                        />
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
                        <Legend
                            content={(props) => (
                                <ul style={{padding: 0, margin: 0}}>
                                    {props.payload && props.payload.map((entry, index) => (
                                        <li key={index} style={{display: 'inline-block', marginRight: 10}}>
                                            <span style={{color: entry.color}}>●</span> {entry.value.substring(0, 5)}...
                                        </li>
                                    ))}
                                </ul>
                            )}
                        />
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
