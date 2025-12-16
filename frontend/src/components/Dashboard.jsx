import React, { useState, useEffect } from 'react';
import api from '../api';
import { CloudRain, Wind, Droplets, ThermometerSun, MapPin } from 'lucide-react';

const CITIES = [
    "London", "New York", "Tokyo", "Delhi", "Beijing", "Paris", "Berlin", "Sydney"
];

export default function Dashboard() {
    const [selectedCity, setSelectedCity] = useState("London");
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchWeather(selectedCity);
    }, [selectedCity]);

    const fetchWeather = async (city) => {
        setLoading(true);
        try {
            const res = await api.get(`/weather/current?city=${city}`);
            setWeather(res.data);
        } catch (err) {
            console.error(err);
        }
        setLoading(false);
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(250px, 1fr) 3fr', gap: '2rem', height: '100%', minHeight: '500px' }}>

            {/* City List Sidebar */}
            <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '600px', overflowY: 'auto' }}>
                <h3 style={{ marginTop: 0, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <MapPin size={20} color="#60a5fa" /> Cities
                </h3>
                {CITIES.map(city => (
                    <button
                        key={city}
                        onClick={() => setSelectedCity(city)}
                        style={{
                            background: selectedCity === city ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                            border: selectedCity === city ? '1px solid #3b82f6' : '1px solid transparent',
                            color: 'white',
                            padding: '10px 15px',
                            borderRadius: '12px',
                            textAlign: 'left',
                            cursor: 'pointer',
                            fontWeight: selectedCity === city ? 'bold' : 'normal',
                            transition: 'all 0.2s'
                        }}
                    >
                        {city}
                    </button>
                ))}
            </div>

            {/* Main Weather View */}
            <div className="glass-panel" style={{ padding: '3rem', display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>

                {/* Decorative Background Blob */}
                <div style={{
                    position: 'absolute', top: -50, right: -50, width: '200px', height: '200px',
                    background: 'radial-gradient(circle, rgba(96,165,250,0.2) 0%, rgba(0,0,0,0) 70%)',
                    borderRadius: '50%', pointerEvents: 'none'
                }} />

                <h2 style={{ fontSize: '3rem', margin: '0 0 2rem 0', fontWeight: '800', letterSpacing: '-1px' }}>
                    {selectedCity}
                </h2>

                {loading ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '1.2rem', color: '#94a3b8' }}>
                        <div className="animate-spin" style={{ width: '20px', height: '20px', border: '2px solid #94a3b8', borderTopColor: 'transparent', borderRadius: '50%' }}></div>
                        Fetching live satellite data...
                    </div>
                ) : weather ? (
                    <div className="animate-fade-in" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '2rem' }}>

                        <div className="stat-card" style={{ background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '16px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#fbbf24', marginBottom: '0.5rem' }}>
                                <ThermometerSun size={24} /> <span style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '1px' }}>Temp</span>
                            </div>
                            <div style={{ fontSize: '3rem', fontWeight: 'bold' }}>{weather.temperature.toFixed(1)}°</div>
                        </div>

                        <div className="stat-card" style={{ background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '16px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#60a5fa', marginBottom: '0.5rem' }}>
                                <Droplets size={24} /> <span style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '1px' }}>Humidity</span>
                            </div>
                            <div style={{ fontSize: '3rem', fontWeight: 'bold' }}>{weather.humidity}%</div>
                        </div>

                        <div className="stat-card" style={{ background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '16px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#34d399', marginBottom: '0.5rem' }}>
                                <Wind size={24} /> <span style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '1px' }}>Wind</span>
                            </div>
                            <div style={{ fontSize: '3rem', fontWeight: 'bold' }}>{weather.wind_speed.toFixed(2)} <span style={{ fontSize: '1rem', color: '#94a3b8' }}>km/h</span></div>
                        </div>

                        <div className="stat-card" style={{ background: 'rgba(255,255,255,0.03)', padding: '1.5rem', borderRadius: '16px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#f472b6', marginBottom: '0.5rem' }}>
                                <CloudRain size={24} /> <span style={{ textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '1px' }}>Status</span>
                            </div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', lineHeight: '3.5rem' }}>{weather.condition}</div>
                        </div>
                    </div>
                ) : (
                    <p>No data available.</p>
                )}
            </div>
        </div>
    );
}
