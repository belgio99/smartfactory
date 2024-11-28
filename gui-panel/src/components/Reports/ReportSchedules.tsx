import React, { useState } from "react";

type Schedule = {
    id: number;
    name: string;
    recurrence: string; // Daily, Weekly, Monthly
    status: "Active" | "Inactive";
    email: string;
    startDate: string;
};

const ReportSchedules: React.FC = () => {
    // Simulated schedule data
    const initialSchedules: Schedule[] = [
        {
            id: 1,
            name: "Quarterly Sales Report",
            recurrence: "Monthly",
            status: "Active",
            email: "sales@company.com",
            startDate: "2024-12-01",
        },
        {
            id: 2,
            name: "Annual Marketing Report",
            recurrence: "Yearly",
            status: "Inactive",
            email: "marketing@company.com",
            startDate: "2024-01-01",
        },
    ];

    const [schedules, setSchedules] = useState<Schedule[]>(initialSchedules);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentSchedule, setCurrentSchedule] = useState<Schedule | null>(null);

    const [newSchedule, setNewSchedule] = useState({
        name: "",
        recurrence: "Daily",
        startDate: "",
        email: "",
    });

    const openModal = (schedule: Schedule | null) => {
        setCurrentSchedule(schedule);
        setNewSchedule(schedule ? { ...schedule } : { name: "", recurrence: "Daily", startDate: "", email: "" });
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setNewSchedule((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleRecurrenceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setNewSchedule((prev) => ({
            ...prev,
            recurrence: e.target.value,
        }));
    };

    const handleSaveSchedule = () => {
        if (currentSchedule) {
            // Edit existing schedule
            setSchedules((prev) =>
                prev.map((schedule) =>
                    schedule.id === currentSchedule.id ? { ...schedule, ...newSchedule } : schedule
                )
            );
        } else {
            // Create new schedule
            const newId = schedules.length ? Math.max(...schedules.map((s) => s.id)) + 1 : 1;
            const newScheduleWithId = { id: newId, ...newSchedule, status: "Active" as "Active" };
            setSchedules((prev) => [...prev, newScheduleWithId]);
        }
        closeModal();
    };

    const handleDeleteSchedule = (id: number) => {
        setSchedules((prev) => prev.filter((schedule) => schedule.id !== id));
    };

    return (
        <div className="SchedulesPage max-w-4xl mx-auto p-6 bg-gray-100 rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Manage Recurring Report Schedules</h1>

            <button
                className="px-4 py-2 bg-blue-500 text-white rounded-lg mb-4 hover:bg-blue-600"
                onClick={() => openModal(null)}
            >
                Create New Schedule
            </button>

            {/* Schedules List */}
            <div className="space-y-4">
                {schedules.map((schedule) => (
                    <div key={schedule.id} className="bg-white border border-gray-200 rounded-lg shadow-sm">
                        <div className="flex items-center justify-between p-4">
                            <div>
                                <h3 className="text-lg font-medium">{schedule.name}</h3>
                                <p className="text-sm text-gray-500">Recurrence: {schedule.recurrence}</p>
                                <p className="text-sm text-gray-500">Email: {schedule.email}</p>
                                <p className="text-sm text-gray-500">Start Date: {schedule.startDate}</p>
                            </div>
                            <div className="flex space-x-2">
                                <button
                                    className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
                                    onClick={() => openModal(schedule)}
                                >
                                    Edit
                                </button>
                                <button
                                    className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                                    onClick={() => handleDeleteSchedule(schedule.id)}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Modal for Create/Edit Schedule */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-gray-500 bg-opacity-50 flex items-center justify-center">
                    <div className="bg-white p-6 rounded-lg shadow-lg max-w-sm w-full">
                        <h2 className="text-xl font-semibold mb-4">{currentSchedule ? "Edit" : "Create"} Schedule</h2>

                        <label className="block mb-2 text-sm">Schedule Name</label>
                        <input
                            type="text"
                            name="name"
                            value={newSchedule.name}
                            onChange={handleInputChange}
                            className="w-full p-2 mb-4 border border-gray-300 rounded"
                            placeholder="Enter schedule name"
                        />

                        <label className="block mb-2 text-sm">Recurrence</label>
                        <select
                            name="recurrence"
                            value={newSchedule.recurrence}
                            onChange={handleRecurrenceChange}
                            className="w-full p-2 mb-4 border border-gray-300 rounded"
                        >
                            <option value="Daily">Daily</option>
                            <option value="Weekly">Weekly</option>
                            <option value="Monthly">Monthly</option>
                            <option value="Yearly">Yearly</option>
                        </select>

                        <label className="block mb-2 text-sm">Start Date</label>
                        <input
                            type="date"
                            name="startDate"
                            value={newSchedule.startDate}
                            onChange={handleInputChange}
                            className="w-full p-2 mb-4 border border-gray-300 rounded"
                        />

                        <label className="block mb-2 text-sm">Email</label>
                        <input
                            type="email"
                            name="email"
                            value={newSchedule.email}
                            onChange={handleInputChange}
                            className="w-full p-2 mb-4 border border-gray-300 rounded"
                            placeholder="Enter email"
                        />

                        <div className="flex space-x-4">
                            <button
                                className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                                onClick={closeModal}
                            >
                                Cancel
                            </button>
                            <button
                                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                                onClick={handleSaveSchedule}
                            >
                                Save
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ReportSchedules;
