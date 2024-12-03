import React, {useState} from "react";
import {Machine} from "../../api/DataStructures";
import {ProductionLine} from "./ProductionLineManager";

interface ProductionLineEditorProps {
    productionLine: ProductionLine;
    onSave: (line: ProductionLine) => void;
    onCancel: () => void;
    machines: Machine[];
}

const ProductionLineEditor: React.FC<ProductionLineEditorProps> = ({
                                                                       productionLine,
                                                                       onSave,
                                                                       onCancel,
                                                                       machines,
                                                                   }) => {
    const [name, setName] = useState(productionLine.name);
    const [site, setSite] = useState(productionLine.site);
    const [selectedMachines, setSelectedMachines] = useState<Machine[]>(
        productionLine.machines
    );

    // Filter machines by the selected site
    const filteredMachines = site
        ? machines.filter((machine) => machine.site === site)
        : [];

    const handleAddMachine = (machine: Machine) => {
        if (selectedMachines.some((m) => m.machineId === machine.machineId)) return;
        setSelectedMachines((prev) => [...prev, machine]);
    };


    const handleRemoveMachine = (machineId: string) => {
        setSelectedMachines((prev) =>
            prev.filter((machine) => machine.machineId !== machineId)
        );
    };

    const handleSave = () => {
        onSave({
            ...productionLine,
            name,
            site,
            machines: selectedMachines,
        });
    };
    return (
        <div>

            <div>
                <h2 className="text-xl font-bold mb-4">Editing Production Line: {name}</h2>

                {/* Name Input and Site Selector */}
                <div className="flex flex-wrap gap-4 mb-4 justify-center">
                    {/* Line Name */}
                    <div className="flex flex-col sm:flex-row items-center gap-2">
                        <label className="text-sm font-medium text-gray-700 min-w-[100px]">
                            Line Name
                        </label>
                        <input
                            type="text"
                            className="mt-1 sm:mt-0 w-full sm:w-auto flex-1 p-2 border border-gray-300 rounded-md shadow-sm"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>

                    {/* Site Selector */}
                    <div className="flex flex-col sm:flex-row items-center gap-2">
                        <label className="text-sm font-medium text-gray-700 min-w-[100px]">
                            Site
                        </label>
                        <select
                            className="mt-1 sm:mt-0 w-full sm:w-auto flex-1 p-2 border border-gray-300 rounded-md shadow-sm"
                            value={site || ""}
                            onChange={(e) => setSite(e.target.value)}
                        >
                            <option value="" disabled>
                                Select a Site
                            </option>
                            {[...new Set(machines.map((machine) => machine.site))].map(
                                (siteOption) => (
                                    <option key={siteOption} value={siteOption}>
                                        {siteOption}
                                    </option>
                                )
                            )}
                        </select>
                    </div>
                </div>
            </div>

            {/* Machine List and Selected Machines */}
            {site ? (
                <div className="flex gap-8">
                    {/* Available Machines */}
                    <div className="flex-1">
                        <h3 className="text-lg font-medium mb-2">Available Machines</h3>
                        <ul className="border border-gray-300 rounded-md max-h-60 overflow-y-auto">
                            {filteredMachines.map((machine) => (
                                <li
                                    key={machine.machineId}
                                    className="flex justify-between items-center px-4 py-2 border-b"
                                >
                                    <span>{machine.machineId} - {machine.type || "Unknown Type"}</span>
                                    <button
                                        className={`text-white px-3 py-1 rounded ${
                                            selectedMachines.some((m) => m.machineId === machine.machineId)
                                                ? "bg-blue-500" : "bg-green-500 hover:bg-green-600"}`}
                                        onClick={() => handleAddMachine(machine)}
                                    >
                                        {selectedMachines.some(
                                            (m) => m.machineId === machine.machineId
                                        )
                                            ? "Added"
                                            : "Add"}
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Selected Machines */}
                    <div className="flex-1">
                        <h3 className="text-lg font-medium mb-2">Selected Machines</h3>
                        <ul className="border border-gray-300 rounded-md max-h-60 overflow-y-auto">
                            {selectedMachines.map((machine) => (
                                <li
                                    key={machine.machineId}
                                    className="flex justify-between items-center px-4 py-2 border-b"
                                >
                                    <span>{machine.machineId} - {machine.type || "Unknown Type"}</span>
                                    <button
                                        className="bg-red-500 text-white px-3 py-1 rounded"
                                        onClick={() => handleRemoveMachine(machine.machineId)}
                                    >
                                        Remove
                                    </button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            ) : (
                <p className="text-gray-500 text-sm">
                    Please select a site to see available machines.
                </p>
            )}

            {/* Save and Cancel Buttons */}
            <div className="mt-4 flex justify-end gap-4">
                <button
                    className="bg-red-500 text-white px-4 py-2 rounded"
                    onClick={onCancel}
                >
                    Cancel
                </button>
                <button
                    className={`px-4 py-2 rounded ${
                        !site || !name || selectedMachines.length === 0
                            ? "bg-gray-300 cursor-not-allowed"
                            : "bg-green-500 text-white hover:bg-green-600"
                    }`}
                    onClick={handleSave}
                    disabled={!site || !name || selectedMachines.length === 0}
                >
                    Save Line
                </button>
            </div>
        </div>
    );
};

export default ProductionLineEditor;