import React, {useEffect, useState} from "react";
import {getMachineList} from "../../api/PersistentDataManager";
import {Machine} from "../../api/DataStructures";
import ProductionLineEditor from "./ProductionLineEditor";

export interface ProductionLine {
    lineId: string;
    name: string;
    site: string;
    machines: Machine[];
}

const ProductionLineManager = () => {
    const [productionLines, setProductionLines] = useState<ProductionLine[]>([]);
    const [editingLine, setEditingLine] = useState<ProductionLine | null>(null);
    const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
    const [machines, setMachines] = useState<Machine[]>([]);
    const [newLineId, setNewLineId] = useState<string | null>(null);

    // Fetch machines on component mount
    useEffect(() => {
        const fetchedMachines = getMachineList();
        setMachines(fetchedMachines);

        // Initialize production lines based on machines
        const initializedLines: ProductionLine[] = [];

        fetchedMachines.forEach((machine) => {
            // Find or create a production line for the machine's line
            let line = initializedLines.find((line) => line.lineId === machine.line);
            if (!line && machine.line) {
                // Create new production line if not found
                line = {
                    lineId: machine.line!,
                    name: `${machine.line}`, // Optionally set a more meaningful name
                    site: machine.site,
                    machines: [],
                };
                initializedLines.push(line);
            }

            // Add machine to the corresponding production line
            if (line) {
                line.machines.push(machine);
            }
        });

        setProductionLines(initializedLines);
    }, []);

    const handleAddLine = () => {
        const newLine: ProductionLine = {
            lineId: Math.random().toString(36).substr(2, 9),
            name: `New Line ${productionLines.length + 1}`,
            site: "",
            machines: [],
        };
        setProductionLines((prev) => [...prev, newLine]);
        setEditingLine(newLine);
        setIsModalOpen(true);
        setNewLineId(newLine.lineId); // Track the newly created line
    };

    const handleCancel = () => {
        if (newLineId) {
            // If a new line was created and the modal is canceled, remove it
            setProductionLines((prev) => prev.filter((line) => line.lineId !== newLineId));
            setNewLineId(null); // Reset newLineId
        }
        setIsModalOpen(false);
    };

    const handleDeleteLine = (lineId: string) => {
        setProductionLines((prev) => prev.filter((line) => line.lineId !== lineId));
    };

    const handleSaveLine = (updatedLine: ProductionLine) => {
        if (editingLine) {
            // Update existing production line
            const updatedLines = productionLines.map((line) =>
                line.lineId === editingLine.lineId ? updatedLine : line
            );
            setProductionLines(updatedLines);
        } else {
            // Add new production line
            setProductionLines([...productionLines, updatedLine]);
        }
        setIsModalOpen(false);
    };
    const handleEditLine = (line: ProductionLine) => {
        setEditingLine(line);
        setIsModalOpen(true);
    };

    return (
        <div className="p-6 bg-gray-50 max-w-5xl mx-auto">
            <h1 className="text-2xl font-bold mb-4">Production Line Manager</h1>
            <button
                className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
                onClick={handleAddLine}
            >
                Add Production Line
            </button>

            <div className="space-y-4 ">
                {productionLines.map((line) => (
                    <div
                        key={line.lineId}
                        className="flex justify-between items-center bg-white p-4 rounded shadow"
                    >
                        <div>
                            <p className="font-bold">{line.name}</p>
                            <p className="text-sm text-gray-500">Site: {line.site || "Unassigned"}</p>
                            <p className="text-sm text-gray-500">
                                Machines: {line.machines.length || 0}
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <button
                                className="bg-green-500 text-white px-3 py-1 rounded"
                                onClick={() => handleEditLine(line)}
                            >
                                Edit
                            </button>
                            <button
                                className="bg-red-500 text-white px-3 py-1 rounded"
                                onClick={() => handleDeleteLine(line.lineId)}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            {editingLine && (
                <Modal isOpen={isModalOpen} onClose={handleCancel}>
                    <ProductionLineEditor
                        productionLine={editingLine}
                        onSave={handleSaveLine}
                        onCancel={handleCancel} // Call handleCancel here
                        machines={machines}
                    />
                </Modal>
            )}

        </div>
    );
};

interface ModalProps {
    isOpen: boolean; // Controls whether the modal is visible
    onClose: () => void; // Callback to close the modal
    children: React.ReactNode; // Content to display inside the modal
}

const Modal = ({isOpen, onClose, children}: ModalProps) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 flex justify-center items-center z-50 bg-black bg-opacity-50">
            <div className="bg-white w-full max-w-5xl rounded-lg shadow-lg relative p-6">
                {/* Close Button */}
                <button
                    className="absolute top-4 right-4 text-gray-500 hover:text-gray-900 text-xl font-bold"
                    onClick={onClose}
                    aria-label="Close Modal"
                >
                    ×
                </button>

                {/* Modal Content */}
                <div className="max-h-[80vh] overflow-y-auto">
                    {children}
                </div>
            </div>
        </div>
    );
};


export default ProductionLineManager;