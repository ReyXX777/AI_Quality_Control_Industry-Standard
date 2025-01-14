import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const MaintenanceStats = ({ equipmentId }) => {
    const [maintenanceData, setMaintenanceData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Simulate API call to fetch maintenance data (replace with actual API call)
        const fetchMaintenanceData = async () => {
            try {
                // Simulated API response
                const response = {
                    nextMaintenanceDate: '2025-03-15',
                    riskScore: 80,
                    downtime: '15 hours',
                    lastMaintenanceDate: '2024-12-01',
                };
                setMaintenanceData(response);
                setLoading(false);
            } catch (err) {
                setError('Failed to fetch maintenance data');
                setLoading(false);
            }
        };

        fetchMaintenanceData();
    }, [equipmentId]);

    if (loading) {
        return <div>Loading maintenance data...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="maintenance-stats">
            <h3>Maintenance Statistics for Equipment ID: {equipmentId}</h3>
            <ul>
                <li><strong>Next Maintenance Date:</strong> {maintenanceData.nextMaintenanceDate}</li>
                <li><strong>Risk Score:</strong> {maintenanceData.riskScore}</li>
                <li><strong>Downtime:</strong> {maintenanceData.downtime}</li>
                <li><strong>Last Maintenance Date:</strong> {maintenanceData.lastMaintenanceDate}</li>
            </ul>
            <button onClick={() => alert('Maintenance prediction updated.')}>Update Maintenance Prediction</button>
        </div>
    );
};

MaintenanceStats.propTypes = {
    equipmentId: PropTypes.string.isRequired,
};

export default MaintenanceStats;
