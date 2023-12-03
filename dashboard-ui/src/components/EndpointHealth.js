/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from 'react';
import '../App.css';

const HealthCheck = () => {
    const [healthStatus, setHealthStatus] = useState({});
    const [error, setError] = useState(null);

    const getHealth = () => {
        fetch('http://sbajustin.eastus.cloudapp.azure.com/health/health')
            .then(res => res.json())
            .then(
                (result) => {
                    console.log("Received stats");
                    setHealthStatus(result);
                    setError(null);
                },
                (error) => {
                    setError(error);
                }
            );
    };

    useEffect(() => {
        // Initial fetch on mount
        getHealth();

        // Set up interval to fetch health status every 20 seconds
        const interval = setInterval(() => getHealth(), 20000);

        // Cleanup the interval when the component unmounts
        return () => clearInterval(interval);
    }, []); // Empty dependency array to ensure it runs only once on mount

    return (
        <div>
            <h2>Health Check</h2>
            {error ? (
                <p>Error fetching data: {error.message}</p>
            ) : (
                <div>
                    <p>Audit: {healthStatus.audit}</p>
                    <p>Processing: {healthStatus.processing}</p>
                    <p>Receiver: {healthStatus.receiver}</p>
                    <p>Storage: {healthStatus.storage}</p>
                    <p>Last Updated: {healthStatus.last_update}</p>
                </div>
            )}
        </div>
    );
};

export default HealthCheck;
