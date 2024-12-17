import {formatTimeFrame} from "../../utils/chartUtil";
import React from "react";

export const DrillDownTooltip = ({active, payload, label, kpi}: any) => {
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
                }}>{`${name}: ${payload[0].value ? (payload[0].value >= 1 ? payload[0].value.toFixed(2) : payload[0].value.toExponential(2)) : 'N/A'} ${kpi?.unit || ''}`}</p>
            </div>
        );
    }
    return null;
};
export const ScatterTooltip = ({active, payload, kpi}: any) => {
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
                    {`${dataPoint.machineId}: ${dataPoint.y >= 1 ? dataPoint.y.toFixed(2) : dataPoint.y.toExponential(2)} ${
                        kpi?.unit || ''
                    }`}
                </p>
            </div>
        );
    }
    return null;
};
export const LineTooltip = ({active, payload, label, kpi}: any) => {
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
                        {`${entry.name}: ${entry.value >= 1 ? entry.value.toFixed(2) : entry.value.toExponential(2)} ${kpi?.unit || ''}`}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};