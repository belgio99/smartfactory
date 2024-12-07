import React, { useState, useEffect } from "react";
import {useNavigate} from "react-router-dom"; // React Router
import {getReports} from "../../api/ApiService";

type Report = {
    id: string;
    title: string;
    description: string;
};

interface ReportArchiveProps {
    // Props
    userId: string;
    username: string;
    token: string;
    role: string;
    site: string;
}


const ReportArchive: React.FC<ReportArchiveProps> = ({userId, username, token, role, site}) => {
    const navigate = useNavigate(); // React Router hook for navigation
    var getReportList; // Variable to get the list of reports

    // Take from API the list of reports
    // While waiting for the API response, show loading spinner
    const [loading, setLoading] = useState(true);
    const [reports, setReports] = useState<Report[]>([]);

    useEffect(() => {
        getReports(userId).then((reports) => {
            setReports(reports);
            setLoading(false);
        });
    }, [userId]);

    // If no reports are available, show mock data
    if(reports.length === 0) {
        const getReportList = (): Report[] => [
            { id: "1", title: "Quarterly Report Q1", description: "Summary and details of Q1 performance." },
            { id: "2", title: "Quarterly Report Q2", description: "Summary and details of Q2 performance." },
            { id: "3", title: "Annual Report 2023", description: "Comprehensive analysis of the year 2023." },
            { id: "4", title: "Quarterly Report Q3", description: "Summary and details of Q3 performance." },
            { id: "5", title: "Annual Report 2022", description: "Comprehensive analysis of the year 2022." },
        ];
        setReports(getReportList());
    }

    const [expanded, setExpanded] = useState<number | null>(null);
    const [filter, setFilter] = useState<string>(""); // For filtering reports by title
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc"); // For sorting reports

    const toggleAccordion = (id: number) => {
        setExpanded((prev) => (prev === id ? null : id));
    };

    const handleManageSchedules = (): void => {
        // Navigate to the recurring schedules page
        navigate("/reports/schedules");
    };

    // Filtering and sorting the reports
    const filteredReports = reports
        .filter((report) =>
            report.title.toLowerCase().includes(filter.toLowerCase())
        )
        .sort((a, b) => {
            if (sortOrder === "asc") {
                return a.title.localeCompare(b.title);
            } else {
                return b.title.localeCompare(a.title);
            }
        });

    return (
        <div className="ReportArchive max-w-6xl mx-auto p-6 bg-gray-50 rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Report Archive</h1>

            {/* Filter and Sort Controls */}
            <div className="mb-6 flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
                <div className="flex items-center space-x-4 flex-1">
                    <label htmlFor="filter" className="block text-gray-700 font-medium">
                        Search Reports
                    </label>
                    <input
                        type="text"
                        id="filter"
                        placeholder="Search by title..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="w-1/2 p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                </div>

                <div className="flex items-center space-x-4">
                    <button
                        className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 shadow text-sm"
                        onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
                    >
                        Sort by Title ({sortOrder === "asc" ? "Asc" : "Desc"})
                    </button>
                </div>
                {/* Schedule Buttons */}
                <div className="mb-6 flex space-x-4 justify-center">
                    <button
                        className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 shadow text-sm"
                        onClick={handleManageSchedules}
                    >
                        Manage Recurring Schedules
                    </button>
                </div>
            </div>

            {/* Report List */}
            <div className="space-y-4">
                {filteredReports.map((report) => (
                    <div
                        key={report.id}
                        className="bg-white border border-gray-200 rounded-lg shadow-sm"
                    >
                        <div
                            className="flex items-center justify-between p-4 cursor-pointer"
                            onClick={() => toggleAccordion(Number(report.id))}
                        >
                            <span className="font-medium text-gray-700">{report.title}</span>
                            <span className="text-gray-500">{expanded === Number(report.id) ? "▲" : "▼"}</span>
                        </div>
                        {expanded === Number(report.id) && (
                            <div className="p-4 border-t border-gray-200">
                                <p className="text-gray-600 mb-4 font-normal text-start ">{report.description}</p>
                                <div className="flex space-x-4">
                                    <button className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm">
                                        View
                                    </button>
                                    <button className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm">
                                        Download
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ReportArchive;
