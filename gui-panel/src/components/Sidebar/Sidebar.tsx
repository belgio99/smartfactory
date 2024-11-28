import React, {useEffect, useState} from 'react';
import SidebarSection from './SidebarSection';
import {DashboardFolder} from "../../api/DataStructures";
import {SidebarItemProps} from "./SidebarItem";

export const pointIcon = 'https://cdn.builder.io/api/v1/image/assets/TEMP/e4f31bc08d7f9cce9aa4820b2adc97643d3b0c001526273b80178ee6bf890b69?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130';
export const folderIcon = 'https://cdn.builder.io/api/v1/image/assets/TEMP/eaf772e37067af09780cab33ecbf00699526f2539b536d7e2dac43b2122526b2?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130';
export const pieIcon = 'https://cdn.builder.io/api/v1/image/assets/TEMP/0949995bd2a21ce720d84c11dc64463261305492e6cd6409f1dd6840a7747be9?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130';
const DashboardSidebar: React.FC = () => {

    const sectionsItems = [
        {
            icon: '/icons/user.svg',
            text: 'User Settings',
            path: '/user-settings'
        },
        {
            icon: '/icons/log.svg',
            text: 'Reports',
            path: '/reports'
        },
        {
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/a71c21e7b5dfbcb7b600377b94bb0ba6e150f444fca7a9c978d6d84a0e3b8cea?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130',
            text: 'Data View',
            path: '/data-view'
        },
        {
            icon: '/icons/log.svg',
            text: 'Log',
            path: '/log'
        },
        {
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/0d48c9f5dfc5a5a35e09f99f937cac2777cbffd55ad9387fca9e140c2b0bc70f?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130',
            text: 'Production Lines',
            path: '/production-lines'
        },
        {icon: '/icons/kpi.svg', text: 'KPIs', path: '/kpis'},
        {icon: '/icons/forecast.svg', text: 'Forecasting', path: '/forecasts'},
    ];

    const formatDashboards = (folders: DashboardFolder[]): SidebarItemProps[] => {
        const formatted: SidebarItemProps[] = [];

        formatted.push({icon: pieIcon, text: 'Overview', path: '/dashboards/overview'})
        folders.forEach((folder) => {
            const currentPath = `/dashboards/${folder.id}`;

            // Format the folder itself
            formatted.push({
                text: folder.name,
                path: currentPath,  // Path will be the folder ID
                icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/eaf772e37067af09780cab33ecbf00699526f2539b536d7e2dac43b2122526b2?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130',
                folder: true
            });

            // Recursively format children
            folder.children.forEach((child) => {
                if (child instanceof DashboardFolder) {
                    // Recursively process child folders
                    formatted.push(...formatDashboards([child]));
                } else { // Add pointers (endpoints) directly
                    formatted.push({
                        text: child.name,
                        path: `${currentPath}/${child.id}`,  // Append pointer ID to the path
                        icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/e4f31bc08d7f9cce9aa4820b2adc97643d3b0c001526273b80178ee6bf890b69?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130',  // Use pointIcon for individual dashboards
                    });
                }
            });
        });

        return formatted;
    };


    useEffect(() => {
        const fetchDashboards = async () => {
            try {
                // Fetch the JSON data
                const response = await fetch('/mockData/dashboards.json'); // Adjust path as needed
                const data = await response.json();

                // Decode the JSON into DashboardFolder instances
                const folderData: DashboardFolder[] = data.map((folderJson: any) => DashboardFolder.decode(folderJson));

                // Format the data for the sidebar
                const formattedDashboards = formatDashboards(folderData);

                setDashboards(formattedDashboards);
            } catch (error) {
                console.error('Failed to fetch dashboards:', error);
            }
        };

        fetchDashboards();
    }, []);

    const [dashboardsItems, setDashboards] = useState<
        SidebarItemProps[]
    >([]);

    return (
        <aside className="bg-white border-r border-gray-200 flex flex-col items-center w-fit h-screen p-3">
            {/* Company Logo */}
            <div className="flex justify-center items-center mb-4">
                <img
                    src={require('./icons/logo.svg').default}
                    alt="Company Logo"
                    className="w-36 h-auto"
                />
            </div>

            {/* Sidebar Sections */}
            {/* <SidebarSection title="Favorites" items={favoritesItems}/> */}
            <SidebarSection title="Sections" items={sectionsItems}/>
            <SidebarSection title="Dashboards" items={dashboardsItems}/>
        </aside>
    );
};

export default DashboardSidebar;
