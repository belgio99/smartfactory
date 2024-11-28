import React, { useState } from 'react';

// Funzione per ottenere i data type
const getDataTypes = (): string[] => {
    return ['dashboard', 'data_view'];
};

const getKPIs = (): string[] => {
    return ['energy_consumption', 'energy_cost', 'energy_production', 'energy_saving', 'energy_efficiency'];
}

interface TimeFrame {
    from: string;
    to: string;
    aggregation?: string;
}

interface JsonObject {
    data_type: string;
    visual: string;
    kpi: string;
    machines: number[];
    time_frame: TimeFrame;
}

const JsonBuilderComponent: React.FC = () => {
    const [dataType, setDataType] = useState('');
    const [visual, setVisual] = useState('');
    const [kpi, setKpi] = useState('');
    const [machines, setMachines] = useState<number[]>([]);
    const [timeFrame, setTimeFrame] = useState<TimeFrame>({ from: '', to: '', aggregation: '' });

    const handleAddMachine = (id: string) => {
        const machineId = parseInt(id);
        if (!isNaN(machineId) && !machines.includes(machineId)) {
            setMachines([...machines, machineId]);
        }
    };

    const handleRemoveMachine = (id: number) => {
        setMachines(machines.filter(machine => machine !== id));
    };

    const handleSubmit = () => {
        const jsonObject: JsonObject = {
            data_type: dataType,
            visual: visual,
            kpi: kpi,
            machines: machines,
            time_frame: timeFrame,
        };

        console.log('Generated JSON:', JSON.stringify(jsonObject, null, 2));
    };

    return (
        <div className="p-6 max-w-md mx-auto bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-semibold mb-4">Crea il tuo oggetto JSON</h2>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Data Type</label>
                <select
                    value={dataType}
                    onChange={(e) => setDataType(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                >
                    {getDataTypes().map((type) => (
                        <option key={type} value={type}>
                            {type}
                        </option>
                    ))}
                </select>
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Visual</label>
                <select
                    value={visual}
                    onChange={(e) => setVisual(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                >
                    <option value="">Seleziona una visualizzazione</option>
                    <option value="grafico">Grafico</option>
                    <option value="tabella">Tabella</option>
                    <option value="mappa">Mappa</option>
                </select>
            </div>

            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">KPI</label>
                <select
                    value={kpi}
                    onChange={(e) => setKpi(e.target.value)}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                >
                    {getKPIs().map((type) => (
                        <option key={type} value={type}>
                            {type}
                        </option>
                    ))}
                </select>
            </div>

            {/* Campo per le macchine */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Machines</label>
                <input
                    type="text"
                    placeholder="Inserisci un ID macchina e premi invio"
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            handleAddMachine(e.currentTarget.value);
                            e.currentTarget.value = '';
                        }
                    }}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                />
                <div className="mt-2 flex flex-wrap gap-2">
                    {machines.map((id) => (
                        <span key={id} className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full">
              {id}
                            <button onClick={() => handleRemoveMachine(id)} className="ml-2 text-red-500">&times;</button>
            </span>
                    ))}
                </div>
            </div>

            {/* Campo per il time frame */}
            <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700">Time Frame</label>
                <input
                    type="date"
                    value={timeFrame.from}
                    onChange={(e) => setTimeFrame({ ...timeFrame, from: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                    placeholder="Da"
                />
                <input
                    type="date"
                    value={timeFrame.to}
                    onChange={(e) => setTimeFrame({ ...timeFrame, to: e.target.value })}
                    className="mt-2 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                    placeholder="A"
                />
                <input
                    type="text"
                    value={timeFrame.aggregation}
                    onChange={(e) => setTimeFrame({ ...timeFrame, aggregation: e.target.value })}
                    className="mt-2 block w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-opacity-50 focus:ring-indigo-300"
                    placeholder="Aggregazione (opzionale)"
                />
            </div>

            <button
                onClick={handleSubmit}
                className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition"
            >
                Genera JSON
            </button>
        </div>
    );
};

export default JsonBuilderComponent;
