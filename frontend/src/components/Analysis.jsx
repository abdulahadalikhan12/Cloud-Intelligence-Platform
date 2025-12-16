import React, { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../api';

export default function Analysis() {
    const [clusters, setClusters] = useState({ 'Low Pollution': [], 'Industrial': [], 'Extreme': [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnalysisData();
    }, []);

    const fetchAnalysisData = async () => {
        try {
            const res = await api.get('/predict/analysis');
            // Process data into groups
            const grouped = { 'Low Pollution': [], 'Industrial': [], 'Extreme': [] };
            // Map cluster IDs to names as used in backend logic (0, 1, 2)
            // Name mapping: 0: Low/Moderate, 1: High/Industrial, 2: Extreme
            res.data.forEach(item => {
                if (item.cluster === 0) grouped['Low Pollution'].push(item);
                else if (item.cluster === 1) grouped['Industrial'].push(item);
                else if (item.cluster === 2) grouped['Extreme'].push(item);
            });
            setClusters(grouped);
        } catch (err) {
            console.error(err);
        }
        setLoading(false);
    };

    return (
        <div style={{ paddingBottom: '2rem' }}>
            <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                <h2 style={{ marginBottom: '0.5rem' }}>Clustering Analysis (Real-Time)</h2>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Segmentation: <span style={{ color: '#34d399' }}>Low Pollution</span> vs <span style={{ color: '#f472b6' }}>Industrial</span> vs <span style={{ color: '#60a5fa' }}>Extreme</span>
                </p>
            </div>

            <div style={{ height: '500px', width: '100%', background: 'rgba(0,0,0,0.2)', borderRadius: '16px', padding: '1rem' }}>
                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#94a3b8' }}>Loading Analysis Data...</div>
                ) : (
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis type="number" dataKey="x" name="Temperature" unit="°C" stroke="#94a3b8" />
                            <YAxis type="number" dataKey="y" name="PM 2.5" unit="µg" stroke="#94a3b8" />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)' }} />
                            <Legend wrapperStyle={{ color: '#fff' }} />

                            <Scatter name="Low Pollution" data={clusters['Low Pollution']} fill="#34d399" />
                            <Scatter name="Industrial" data={clusters['Industrial']} fill="#f472b6" />
                            <Scatter name="Extreme" data={clusters['Extreme']} fill="#60a5fa" />
                        </ScatterChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
}
