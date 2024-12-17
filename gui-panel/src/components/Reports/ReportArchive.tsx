import React, {useEffect, useState} from "react";
import {useNavigate} from "react-router-dom"; // React Router
import {downloadReport, getReports, instantReport} from "../../api/ApiService";
import ReportModal from "./InstantModal";

type Report = {
    id: string;
    name: string;
    type: string;
};

interface ReportArchiveProps {
    // Props
    userId: string;
    username: string;
    token: string;
    role: string;
    site: string;
}

/**
 * This method downloads and create a new tab for the report
 * @param reportId string - reportID of the report to download
 */
export const handleView = async (reportId: string) => {
    try {
        const blob = await downloadReport(reportId);
        const fileURL = URL.createObjectURL(blob);

        // Apri il file in una nuova scheda
        window.open(fileURL, "_blank");
        console.log(`Report ID ${reportId} aperto in una nuova scheda.`);
    } catch (error) {
        console.error("Errore durante l'apertura del report:", error);
        alert("Errore durante l'apertura del report");
    }
};

/**
 * This method downloads the report
 * @param reportId string - reportID of the report to download
 * @param title string - title of the report to download
 */
export const handleDownload = async (reportId: string, title: string) => {
    try {
        const blob = await downloadReport(reportId); // Usa la tua API già implementata
        const fileName = `${title}.pdf`;
        const fileURL = URL.createObjectURL(blob);

        // Salva il file
        const anchor = document.createElement("a");
        anchor.href = fileURL;
        anchor.download = fileName;
        anchor.click();
        URL.revokeObjectURL(fileURL);

        console.log(`Report "${title}" downloaded successfully`);
    } catch (error) {
        console.error("Error during the download: ", error);
        alert("An error occurred during the download. Please try again later.");
    }
};


const ReportArchive: React.FC<ReportArchiveProps> = ({userId, username, token, role, site}) => {
    const navigate = useNavigate(); // React Router hook for navigation
    var getReportList; // Variable to get the list of reports

    // Take from API the list of reports
    // While waiting for the API response, show loading spinner
    const [reports, setReports] = useState<Report[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const handleInstant = async (partialReportData: Partial<{
        machines: string[];
        name: string;
        email: string;
        period: string;
        kpis: string[]
    }>) => {
        setIsLoading(true); // Show loading screen
        setIsModalOpen(false);

        try {
            // TODO: Implement API request to generate instant report
            console.log("Requesting report with data:", partialReportData);
            // Simulate a delay for loading screen demo purposes

            const reportData = {
                id: new Date().getTime(),
                name: partialReportData.name || "Unnamed Report",
                email: partialReportData.email || "",
                recurrence: partialReportData.period || "Daily",
                kpis: partialReportData.kpis || [],
                machines: partialReportData.machines || [],
                status: true,
                startDate: new Date().toISOString().split("T")[0],
            };

            try {
                const reportId = await instantReport(userId, reportData);
                console.log("Report generated successfully with ID:", reportId);
                await handleView(reportId); // Open the generated report in a new tab
            } catch (error) {
                console.error("Failed to request report:", error);
            }
        } catch (error) {
            console.error("Failed to request report:", error);
            // Handle error appropriately (e.g., show error message)
        } finally {
            setIsLoading(false); // Hide loading screen
        }
    };

    const handleClose = () => {
        setIsModalOpen(false); // Close modal without saving
    };

    useEffect(() => {
        getReports(userId).then((reports) => {
            setReports(reports);
        }).catch((error: any) => {
            console.error("Failed to get reports:", error);
        }).finally(
            () => setIsLoading(false)
        );
    }, [userId]);

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
            report.name.toLowerCase().includes(filter.toLowerCase())
        )
        .sort((a, b) => {
            if (sortOrder === "asc") {
                return a.name.localeCompare(b.name);
            } else {
                return b.name.localeCompare(a.name);
            }
        });

    console.log("Reports:", filteredReports);
    return (
        <div className="ReportArchive max-w-6xl mx-auto p-6 bg-gray-25 rounded-lg shadow-lg">
            <h1 className="text-2xl font-bold mb-4 text-gray-800">Report Manager</h1>

            <div className="flex items-center space-x-4 mb-6 text-gray-700">
                In this section you can view, download, and generate reports. To see, create and edit the recurrent
                report schedules click on "Manage Schedules".
            </div>

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
                <div className="flex items-center mx-auto space-x-4 justify-end">
                    <div className="flex space-x-4 items-center">
                        <button
                            className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600 shadow text-sm"
                            onClick={handleManageSchedules}
                        >
                            Manage Schedules
                        </button>
                    </div>
                    <div>
                        {/* Button to Open Modal */}
                        <button
                            onClick={() => setIsModalOpen(true)}
                            className="px-3 py-1 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                        >
                            Generate Report Now
                        </button>

                        {/* Modal */}
                        <ReportModal
                            isOpen={isModalOpen}
                            reportData={{}} // Provide initial report data (if any)
                            onSave={handleInstant}
                            onClose={handleClose}
                        />

                        {/* Loading Screen */}
                        {isLoading && (
                            <div
                                className="fixed inset-0 bg-gray-500 bg-opacity-50 flex items-center justify-center z-50">
                                <div className="bg-white p-6 rounded-lg shadow-lg">
                                    <p className="text-lg font-semibold">Requesting Report...</p>
                                    <div className="mt-4">
                                        <div
                                            className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full border-blue-500 border-t-transparent"></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                </div>
            </div>

            {/* Report List */}
            <div className="space-y-4 flex-col">
                {filteredReports.map((report) => (
                    <div
                        key={report.id}
                        className="bg-white border flex border-gray-200 rounded-lg shadow-sm"
                    >

                        <div className="p-4 border-t border-gray-200">
                            <p className="text-gray-600 mb-4 font-normal text-start ">{report.name}</p>
                            <div className="flex space-x-4">
                                <button
                                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                                    onClick={() => handleView(report.id)}>
                                    View
                                </button>
                                <button
                                    className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                                    onClick={() => handleDownload(report.id, report.name)}>
                                    Download
                                </button>
                            </div>
                        </div>

                    </div>
                ))}
            </div>

        </div>
    );
};

export default ReportArchive;
