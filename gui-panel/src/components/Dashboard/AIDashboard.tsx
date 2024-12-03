import {useLocation} from "react-router-dom";
import React from "react";

const AIDashboard: React.FC = () => {
    const location = useLocation();
    const metadata = location.state?.metadata;

    return (
        <div>
            <h1>Target Page</h1>
            {metadata && (
                <div>
                    <p>Metadata:</p>
                    <pre>{JSON.stringify(metadata, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default AIDashboard;