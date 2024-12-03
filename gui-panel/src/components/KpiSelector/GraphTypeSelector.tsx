import React from 'react';

interface GraphTypeSelectorProps {
    value: string; // Selected graph type
    onChange: (value: string) => void; // Function to notify parent about the change
}

const GraphTypeSelector: React.FC<GraphTypeSelectorProps> = ({value, onChange}) => {
    require('./icons/graph.svg');

    const graphTypes = [
        {
            type: 'pie',
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/c4c1970484578b546624746d8daba4aa42142c6aab1ae95ef109c80298151027?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130'
        },
        {
            type: 'donut',
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/9c3b3b4f0b3d0b6f8b0d7c6f0e7f0c4b6b5f0b4'
        },
        {
            type: 'barv',
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/cc10e3abebe37695d85173fdfefb117298ad299b0e5f29e6e3821b1564a87f78?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130'
        },
        {
            type: 'barh',
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/2207bcbb65a5ea0c966aae909ab2eac60428a0dfab62d51c225a3a4cf9e62124?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130'
        },
        {type: 'line', icon: './icons/graph.svg'},
        {type: 'area', icon: ''},
        {type: 'scatter', icon: ''},
        {type: 'hist', icon: ''},
        {type: 'heatmap', icon: ''},
        {type: 'stacked_bar', icon: ''},

    ];

    return (
        <div className="flex flex-wrap sm:w-full lg:w-fit justify-start gap-2 sm:gap-4 lg:gap-5 p-2 sm:p-3">
            {graphTypes.map((graph) => (
                <div
                    key={graph.type}
                    className={`p-2 rounded cursor-pointer transition-all text-xs  border-2 border-gray hover:bg-blue-100 
            ${value === graph.type ? 'bg-blue-300 text-white' : 'bg-white text-gray-600'}`}
                    onClick={() => onChange(graph.type)}
                >
                    {graph.icon && (
                        <img
                            src={graph.icon}
                            alt={graph.type}
                            className={`w-8 h-8 mx-auto mb-1 transition-all ${value === graph.type ? 'opacity-100' : 'opacity-60'}`}
                        />
                    )}
                    <div className="text-center">{graph.type.replace(/\b\w/g, char => char.toUpperCase()) // Capitalize
                    }</div>
                </div>
            ))}
        </div>
    );
};

export default GraphTypeSelector;
