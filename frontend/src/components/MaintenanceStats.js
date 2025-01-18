import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const MaintenanceStats = ({ equipmentId }) => {
    const [maintenanceData, setMaintenanceData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [alertThreshold, setAlertThreshold] = useState(70); // Default threshold for risk score alerts

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
                    history: [
                        { date: '2024-01-01', riskScore: 30 },
                        { date: '2024-04-01', riskScore: 45 },
                        { date: '2024-07-01', riskScore: 60 },
                        { date: '2024-10-01', riskScore: 75 },
                        { date: '2025-01-01', riskScore: 80 },
                    ],
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

            {/* Maintenance History Chart */}
            <div className="chart-container">
                <h4>Maintenance Risk Score History</h4>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={maintenanceData.history}>
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="riskScore" stroke="#8884d8" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Alert Threshold Configuration */}
            <div className="alert-threshold">
                <h4>Set Risk Score Alert Threshold</h4>
                <input
                    type="number"
                    value={alertThreshold}
                    onChange={(e) => setAlertThreshold(Number(e.target.value))}
                    min="0"
                    max="100"
                />
                <button onClick={() => alert(`Alert threshold set to ${alertThreshold}.`)}>Save Threshold</button>
                {maintenanceData.riskScore > alertThreshold && (
                    <p className="alert-message">⚠️ Risk score exceeds the alert threshold!</p>
                )}
            </div>

            <button onClick={() => alert('Maintenance prediction updated.')}>Update Maintenance Prediction</button>
        </div>
    );
};

MaintenanceStats.propTypes = {
    equipmentId: PropTypes.string.isRequired,
};

export default MaintenanceStats;
