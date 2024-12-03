import React, { useState } from 'react';
import SidebarItem, { SidebarItemProps } from './SidebarItem';

interface SidebarFolderProps {
    icon?: string; // Optional folder icon
    text: string;
    path: string;
    children: SidebarItemProps[];
}

const SidebarFolder: React.FC<SidebarFolderProps> = ({ icon, text, path, children }) => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleOpen = () => setIsOpen(!isOpen);

    return (
        <div className="flex flex-col">
            <button
                className="flex items-center space-x-2 text-gray-700 font-medium"
                onClick={toggleOpen}
            >
                {icon && <img src={icon} alt={`${text} icon`} className="w-4 h-4" />}
                <span>{text}</span>
                <span>{isOpen ? '-' : '+'}</span>
            </button>
            {isOpen && (
                <div className="pl-4">
                    {children.map((child) => (
                        <SidebarItem
                            key={child.path}
                            icon={child.icon}
                            text={child.text}
                            path={child.path}
                            folder={child.folder}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};

export default SidebarFolder;
