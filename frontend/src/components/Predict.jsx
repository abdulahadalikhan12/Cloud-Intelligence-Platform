import React, { useState } from 'react';
import api from '../api';

export default function Predict() {
    const [mode, setMode] = useState('risk'); // 'risk' or 'pollution'
    const [formData, setFormData] = useState({
        temperature: 20,
        humidity: 50,
        rain: 0,
        pressure: 1012,
        wind_speed: 10,
        month: 6,
        hour: 12
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: parseFloat(e.target.value) });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResult(null);
        try {
            const endpoint = mode === 'risk' ? '/predict/air-quality' : '/predict/pollution';
            const res = await api.post(endpoint, formData);
            setResult(res.data);
        } catch (err) {
            console.error(err);
            alert("Error fetching prediction");
        }
        setLoading(false);
    };

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', justifyContent: 'center' }}>
                <button className={`btn-primary ${mode === 'risk' ? '' : 'opacity-50'}`} style={{ opacity: mode === 'risk' ? 1 : 0.5 }} onClick={() => setMode('risk')}>
                    Air Quality Risk
                </button>
                <button className={`btn-primary ${mode === 'pollution' ? '' : 'opacity-50'}`} style={{ opacity: mode === 'pollution' ? 1 : 0.5 }} onClick={() => setMode('pollution')}>
                    Pollution (PM2.5) Level
                </button>
            </div>

            <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '2rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>

                {Object.keys(formData).map((key) => (
                    <div key={key}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', textTransform: 'capitalize', color: 'var(--text-secondary)' }}>
                            {key.replace('_', ' ')}
                        </label>
                        <input
                            type="number"
                            name={key}
                            value={formData[key]}
                            onChange={handleChange}
                            step="any"
                        />
                    </div>
                ))}

                <div style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                    <button type="submit" className="btn-primary" style={{ width: '100%' }} disabled={loading}>
                        {loading ? 'Predicting...' : 'Run Prediction'}
                    </button>
                </div>
            </form>

            {result && (
                <div className="glass-panel animate-fade-in" style={{ marginTop: '2rem', padding: '1.5rem', textAlign: 'center', borderColor: '#3b82f6', borderWidth: '2px' }}>
                    <h3 style={{ marginTop: 0 }}>Prediction Result</h3>
                    {mode === 'risk' ? (
                        <div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: result.aqi_category === 'Good' ? '#34d399' : '#ef4444' }}>
                                {result.aqi_category}
                            </div>
                            <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                        </div>
                    ) : (
                        <div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#60a5fa' }}>
                                {result.predicted_pm25.toFixed(2)} µg/m³
                            </div>
                            <p>Estimated PM2.5 Concentration</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
