import React, {useEffect, useState} from "react";
import {Schedule} from "../../api/DataStructures";
import ScheduleModal from "./ScheduleModal";
import PersistentDataManager, {loadFromLocal} from "../../api/DataManager";
import {scheduleReport} from "../../api/ApiService";

interface SchedulesListProps {
    schedules: Schedule[];
    onEdit: (schedule: Schedule) => void;
    onDelete: (id: number) => void;
}

interface ScheduleProps {
    userId: string;
    username: string;
}

const SchedulesList: React.FC<SchedulesListProps> = ({schedules, onEdit, onDelete}) => {

    const dataManager = PersistentDataManager.getInstance();

    function mapKpiIdToName(kpiId: string): string {
        const kpis = dataManager.getKpiList();
        const kpi = kpis.find((kpi) => kpi.id === kpiId);
        return kpi ? kpi.name : kpiId;
    }

    return (
        <div className="space-y-4">
            {schedules.map((schedule) => (
                <div key={schedule.id} className="bg-white border border-gray-200 rounded-lg shadow-sm">
                    <div className="flex items-center justify-between p-4">
                        <div>
                            <h3 className="text-lg font-medium">{schedule.name}</h3>
                            <p className="text-sm text-gray-500">Recurrence: {schedule.recurrence}</p>
                            <p className="text-sm text-gray-500">Email: {schedule.email}</p>
                            <p className="text-sm text-gray-500">Start Date: {schedule.startDate}</p>
                            <p className="text-sm text-gray-500">KPIs: {schedule.kpis.map(mapKpiIdToName).join(", ")}</p>
                            <p className="text-sm text-gray-500">Machines: {schedule.machines.join(", ")}</p>
                        </div>
                        <div className="flex space-x-2">
                            <button
                                className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
                                onClick={() => onEdit(schedule)}
                            >
                                Edit
                            </button>
                            <button
                                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                                onClick={() => onDelete(schedule.id)}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

const ReportSchedules: React.FC<ScheduleProps> = ({userId, username}) => {
    const [schedules, setSchedules] = useState<Schedule[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingSchedule, setEditingSchedule] = useState<Partial<Schedule> | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            const loadedSchedules = await loadFromLocal("/mockData/schedules.json", Schedule.decode);
            setSchedules(loadedSchedules);
        };
        fetchData();
    }, []);

    const handleSaveSchedule = async (schedule: Partial<Schedule>) => {
        if (editingSchedule) {
            setSchedules((prev) =>
                prev.map((s) => (s.id === editingSchedule.id ? {...s, ...schedule} : s))
            );
        } else {
            const newId = schedules.length ? Math.max(...schedules.map((s) => s.id)) + 1 : 1;

            // Crea un nuovo oggetto Schedule
            const newSchedule: Schedule = new Schedule(
                newId,
                schedule.name || "Unnamed Schedule",
                schedule.recurrence || "Daily",
                "Active",
                schedule.email || "",
                schedule.startDate || new Date().toISOString().split("T")[0],
                schedule.kpis || [],
                schedule.machines || []
            );

            // Aggiungi " 00:00:00" alla data (formato richiesto dal server)
            newSchedule.startDate = newSchedule.startDate + " 00:00:00";

            try {
                // Prepara il payload per l'API
                const requestData = {
                    userId: userId,
                    params: {
                        id: newId.toString(),
                        status: newSchedule.status === "Active",
                        name: newSchedule.name,
                        recurrence: newSchedule.recurrence,
                        startDate: newSchedule.startDate, // Es. "2024-12-10 00:00:00"
                        email: newSchedule.email,
                        kpis: newSchedule.kpis.filter((kpi) => kpi && kpi.trim().length > 0),
                        machines: newSchedule.machines,
                    }
                };

                console.log("Saving schedule with requestData:", requestData);

                setSchedules((prev) => [...prev, newSchedule]);

                //Call the API to save the schedule
                await scheduleReport(requestData);

                console.log("Schedule saved successfully!");
            } catch (error) {
                console.error("Failed to save schedule:", error);
            }

            setIsModalOpen(false);
        }
    };


    const handleDeleteSchedule = (id: number) => {
        setSchedules((prev) => prev.filter((schedule) => schedule.id !== id));
    };

    return (
        <div className="SchedulesPage max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-xl space-y-6">
            <h1 className="text-3xl font-semibold text-gray-800">Manage Recurring Report Schedules</h1>

            {/* Create New Schedule Button */}
            <button
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition duration-200"
                onClick={() => {
                    setEditingSchedule(null); // Clear any existing schedule being edited
                    setIsModalOpen(true); // Open modal for creating a new schedule
                }}
            >
                Create New Schedule
            </button>

            {/* Schedules List */}
            <SchedulesList
                schedules={schedules}
                onEdit={(schedule) => {
                    setEditingSchedule(schedule); // Set the selected schedule for editing
                    setIsModalOpen(true); // Open the modal
                }}
                onDelete={handleDeleteSchedule} // Pass the delete handler
            />

            {/* Schedule Modal */}
            <ScheduleModal
                isOpen={isModalOpen}
                schedule={editingSchedule || {}} // Pass either the schedule to edit or an empty object for a new schedule
                onSave={(savedSchedule) => {
                    handleSaveSchedule(savedSchedule); // Save the new or edited schedule
                    setIsModalOpen(false); // Close the modal after saving
                }}
                onClose={() => setIsModalOpen(false)} // Close the modal
            />
        </div>
    );
};

export default ReportSchedules;