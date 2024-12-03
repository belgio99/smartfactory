import React from 'react';
import SidebarItem, { SidebarItemProps } from './SidebarItem';
import SidebarFolder from './SidebarFolder';

interface SidebarSectionProps {
    title: string;
    items: SidebarItemProps[]; // Support items and folders
}

const SidebarSection: React.FC<SidebarSectionProps> = ({ title, items }) => (
    <div className="w-full mb-6">
        <h3 className="text-sm space-y-1 font-bold uppercase text-gray-500 mb-2">{title}</h3>
        <div className="flex flex-col gap-2">
            {items.map((item) =>
                item.folder ? (
                    <SidebarFolder
                        key={item.path}
                        icon={item.icon}
                        text={item.text}
                        path={item.path}
                        children={item.children || []}
                    />
                ) : (
                    <SidebarItem
                        key={item.path}
                        icon={item.icon}
                        text={item.text}
                        path={item.path}
                        folder={item.folder}
                    />
                )
            )}
        </div>
    </div>
);

export default SidebarSection;
