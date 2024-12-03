import React, { useState, useMemo } from 'react';
import { getMachineList } from "../../api/PersistentDataManager";

interface MachineFilterModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (machineIds: string[]) => void;
    initialMachineIds: string[];
    machineType: string;
}

const MachineFilterModal: React.FC<MachineFilterModalProps> = ({
                                                                   isOpen,
                                                                   onClose,
                                                                   onSave,
                                                                   initialMachineIds,
                                                               }) => {
    const [selectedMachines, setSelectedMachines] = useState<string[]>(initialMachineIds);
    const [selectedMachineType, setSelectedMachineType] = useState("All");
    const machines = useMemo(() => getMachineList().filter((machine) =>
        selectedMachineType === 'All' || machine.type === selectedMachineType
    ), [selectedMachineType]);

    const handleAddMachine = (machineId: string) => {
        if (!selectedMachines.includes(machineId)) {
            setSelectedMachines((prev) => [...prev, machineId]);
        }
    };

    const handleRemoveMachine = (machineId: string) => {
        setSelectedMachines((prev) => prev.filter((id) => id !== machineId));
    };

    const handleSave = () => {
        onSave(selectedMachines);
        onClose();
    };

    const handleSelectAll = () => {
        const allMachineIds = machines.map((machine) => machine.machineId);
        // Add only the machines that aren't already selected
        setSelectedMachines((prevSelected) => [
            ...new Set([...prevSelected, ...allMachineIds])
        ]);
    };

    const handleClearSelection = () => {
        setSelectedMachines([]);
    };

    return (
        isOpen ? (
            <div className="fixed inset-0 bg-gray-600 bg-opacity-50 z-50 flex justify-center items-center">
                <div className="bg-white p-6 rounded-lg shadow-lg max-w-3xl w-full">
                    <h3 className="text-lg font-semibold mb-4">Select Machines</h3>

                    {/* Machine Type Filter */}
                    <div className="mb-4">
                        <label className="text-sm font-medium text-gray-700">Machine Type:</label>
                        <select
                            className="block w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                            value={selectedMachineType}
                            onChange={(e) => setSelectedMachineType(e.target.value)}
                        >
                            {/* Dynamically populate machine types */}
                            {['All', ...new Set(getMachineList().map(machine => machine.type))].map((type) => (
                                <option key={type} value={type}>
                                    {type}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex gap-8">
                        {/* Available Machines */}
                        <div className="flex-1">
                            <h4 className="font-medium mb-2">Available Machines</h4>
                            <ul className="border border-gray-300 rounded-md max-h-60 overflow-y-auto">
                                {machines.map((machine) => (
                                    <li
                                        key={machine.machineId}
                                        className="flex justify-between items-center px-4 py-2 border-b"
                                    >
                                        <span>{machine.machineId} - {machine.type || "Unknown Type"}</span>
                                        <button
                                            className={`px-3 py-1 rounded ${selectedMachines.includes(machine.machineId) ? 'bg-blue-500 text-white' : 'bg-green-500 text-white'}`}
                                            onClick={() => {
                                                if (selectedMachines.includes(machine.machineId)) {
                                                    // Do nothing if already added
                                                } else {
                                                    handleAddMachine(machine.machineId);
                                                }
                                            }}
                                        >
                                            {selectedMachines.includes(machine.machineId) ? 'Added' : 'Add'}
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Selected Machines */}
                        <div className="flex-1">
                            <h4 className="font-medium mb-2">Added Machines</h4>
                            <ul className="border border-gray-300 rounded-md max-h-60 overflow-y-auto">
                                {selectedMachines.map((machineId) => (
                                    <li
                                        key={machineId}
                                        className="flex justify-between items-center px-4 py-2 border-b"
                                    >
                                        <span>{machineId}</span>
                                        <button
                                            className="bg-red-500 text-white px-3 py-1 rounded"
                                            onClick={() => handleRemoveMachine(machineId)}
                                        >
                                            Remove
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="mt-4 flex justify-between gap-4">
                        <button
                            className="bg-gray-300 text-gray-700 px-4 py-2 rounded"
                            onClick={onClose}
                        >
                            Close
                        </button>
                        <div className="flex gap-4">
                            <button
                                className="bg-blue-500 text-white px-4 py-2 rounded"
                                onClick={handleSelectAll}
                            >
                                Select All
                            </button>
                            <button
                                className="bg-yellow-500 text-white px-4 py-2 rounded"
                                onClick={handleClearSelection}
                            >
                                Clear Selection
                            </button>
                            <button
                                className={`px-4 py-2 rounded ${selectedMachines.length > 0 ? "bg-green-500 text-white" : "bg-gray-300 cursor-not-allowed"}`}
                                onClick={handleSave}
                                disabled={selectedMachines.length === 0}
                            >
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        ) : null
    );
};

export default MachineFilterModal;
