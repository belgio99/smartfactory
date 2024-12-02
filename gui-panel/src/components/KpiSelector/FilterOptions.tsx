import React, {useState, useMemo} from 'react';
import {getMachineList} from "../../api/PersistentDataManager";
import MachineFilterModal from './MachineFilter';

interface FilterOptionsProps {
    filter: Filter;
    onChange: (filters: Filter) => void;
}

export class Filter {
    machineType: string;
    machineIds: string[];

    constructor(machineType: string, machineIds: string[]) {
        this.machineType = machineType;
        this.machineIds = machineIds;
    }
}

const FilterOptions: React.FC<FilterOptionsProps> = ({filter, onChange}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedMachineIds, setSelectedMachineIds] = useState(filter.machineIds);

    // Memoize compatible machine types to avoid re-filtering on each render
    const compatibleMachineTypes = useMemo(() => {
        const machineTypes = getMachineList().map((data) => data.type);
        return ['All', 'Custom Machine Set', ...new Set(machineTypes)];
    }, []);

    // Filter machines based on the selected machine type
    const filteredMachines = useMemo(() => {
        if (filter.machineType === 'All') {
            return getMachineList(); // Show all machines if 'All' is selected
        } else if (filter.machineType === 'Custom Machine Set') {
            return []; // We'll handle custom machines separately via modal
        } else {
            return getMachineList().filter((machine) => machine.type === filter.machineType);
        }
    }, [filter.machineType]);

    const handleModalSave = (machineIds: string[]) => {
        setSelectedMachineIds(machineIds);
        onChange({...filter, machineIds});
    };

    return (
        <div className="max-h-fit max-w-fit">
            <div className="flex justify-between items-center mb-4">
                <div className="text-sm font-semibold text-gray-700">Filtering Options</div>
            </div>

            <div className="flex items-center mb-4 space-x-4 font-normal">
                <div className="flex items-center space-x-4">
                    <label className="text-sm font-medium text-gray-700">Machine Type:</label>
                    <select
                        className="block w-full px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 sm:text-sm"
                        value={filter.machineType}
                        onChange={(e) => onChange({...filter, machineType: e.target.value})}
                    >
                        {compatibleMachineTypes.map((type, index) => (
                            <option key={`${type}-${index}`} value={type}>
                                {type}
                            </option>
                        ))}
                    </select>
                </div>

                {filter.machineType === 'Custom Machine Set' && (
                    <div className="flex items-center space-x-4">
                        <button
                            className="ml-4 bg-blue-500 text-white py-1 px-4 rounded-md hover:bg-blue-600 focus:outline-none"
                            onClick={() => setIsModalOpen(true)}
                        >
                            Edit Machines
                        </button>
                        <div className="flex items-center ml-2 text-sm text-gray-600 font-semibold">{selectedMachineIds.length} Machines Selected
                        </div>
                    </div>
                )}
            </div>

            {/* Modal Component */}
            <MachineFilterModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSave={handleModalSave}
                initialMachineIds={selectedMachineIds}
                machineType={filter.machineType}
            />
        </div>
    );
};

export default FilterOptions;
