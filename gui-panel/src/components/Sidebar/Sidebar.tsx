import React, {useEffect, useState} from 'react';
import SidebarSection from './SidebarSection';
import {DashboardFolder} from "../../api/DataStructures";
import {SidebarItemProps} from "./SidebarItem";

export const pointIcon: string = 'https://cdn.builder.io/api/v1/image/assets/TEMP/e4f31bc08d7f9cce9aa4820b2adc97643d3b0c001526273b80178ee6bf890b69?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130';
export const folderIcon: string = "/icons/folder.svg";
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
        /*{
            icon: 'https://cdn.builder.io/api/v1/image/assets/TEMP/0d48c9f5dfc5a5a35e09f99f937cac2777cbffd55ad9387fca9e140c2b0bc70f?placeholderIfAbsent=true&apiKey=346cd8710f5247b5a829262d8409a130',
            text: 'Production Lines',
            path: '/production-lines'
        },
         */
        {icon: '/icons/kpi.svg', text: 'KPIs', path: '/kpis'},
        {icon: '/icons/forecast.svg', text: 'Forecasting', path: '/forecasts'},
    ];

    const formatDashboards = (folders: DashboardFolder[]): SidebarItemProps[] => {
        const formatted: SidebarItemProps[] = [];

        formatted.push({icon: "/icons/pie.svg", text: 'Overview', path: '/dashboards/overview'});
        folders.forEach((folder) => {
            const currentPath = `/dashboards/${folder.id}`;

            // Add the folder item with its children
            formatted.push({
                text: folder.name,
                path: currentPath,
                icon: folderIcon,
                folder: true,
                children: folder.children.map((child) => {
                    if (child instanceof DashboardFolder) {
                        // Process nested folders
                        return {
                            text: child.name,
                            path: `${currentPath}/${child.id}`,
                            icon: folderIcon,
                            folder: true,
                            children: formatDashboards([child]), // Recursive children formatting
                        };
                    } else {
                        // Add pointer (endpoint) items
                        return {
                            text: child.name,
                            path: `${currentPath}/${child.id}`,
                            icon: pointIcon,
                            folder: false,
                        };
                    }
                }),
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
