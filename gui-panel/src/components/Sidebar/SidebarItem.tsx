import React from 'react';
import {useNavigate} from 'react-router-dom';

export type SidebarItemProps = { text: string, path: string, icon: string, folder?: boolean };

const SidebarItem: React.FC<SidebarItemProps> = ({icon, text, path, folder}) => {
    const navigate = useNavigate();

    const handleClick = () => {
        if (!folder) navigate(path);
    };

    return (
        <div className={`flex-1 items-start space-x-3`}>
            <div
                onClick={handleClick}
                className="flex items-center p-1 rounded-lg cursor-pointer hover:bg-gray-100 transition"
            >
                <img src={icon} alt={text} className="w-5 h-5 mr-3"/>
                <span className="text-sm text-start text-gray-700">{text}</span>
            </div>
        </div>
    );
};

export default SidebarItem;
