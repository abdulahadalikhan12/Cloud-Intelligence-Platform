import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api';

const CITIES = ["London", "New York", "Tokyo", "Delhi", "Beijing", "Paris", "Berlin", "Sydney"];

export default function Analytics() {
    const [city, setCity] = useState("London");
    const [data, setData] = useState([]);

    useEffect(() => {
        fetchForecast(city);
    }, [city]);

    const fetchForecast = async (cityName) => {
        try {
            const res = await api.post(`/forecast/weather?city=${cityName}`); // Note: Backend router expects query param for POST? Let me check backend. 
            // Router: @misc_router.post("/forecast/weather") def forecast_proxy(city: str) -> Query param.
            setData(res.data.forecast);
        } catch (err) {
            console.error(err);
        }
    };

    const CITY_INSIGHTS = {
        "London": "Temperate maritime climate. Frequent cloud cover and light precipitation. Primary pollution source: Road traffic (NO2).",
        "New York": "Humid subtropical climate. Significant seasonal temperature variation. Pollution risks: Ozone in summer, PM2.5 from urban density.",
        "Tokyo": "Humid subtropical. Wet summers, dry winters. High urban density leads to heat island effect and localized particulate accumulation.",
        "Delhi": "Semi-arid climate. Extreme temperatures. Critical air quality issues in winter due to inversion layers and agricultural burning (PM2.5/PM10).",
        "Beijing": "Humid continental. Hot, humid summers; cold, dry winters. Historically high PM2.5, though significantly improved recent years. Dust storms in spring.",
        "Paris": "Oceanic climate. Mild temperatures. key pollutants: Nitrogen dioxide from diesel vehicles and particulate matter.",
        "Berlin": "Temperate seasonal climate. Moderate rainfall. Air quality generally good but winter smog episodes occur due to wood burning and traffic.",
        "Sydney": "Humid subtropical. Sunny with mild winters. Occasional bushfire smoke events impact air quality (PM2.5) severely in summer."
    };

    return (
        <div style={{ height: '100%', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h2>Temperature Forecast & Insights</h2>
                <select value={city} onChange={(e) => setCity(e.target.value)} style={{ width: '200px' }}>
                    {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
            </div>

            <div style={{ height: '350px', width: '100%', marginBottom: '2rem' }}>
                <ResponsiveContainer>
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                        <XAxis dataKey="date" stroke="#94a3b8" />
                        <YAxis stroke="#94a3b8" unit="°C" />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)' }}
                        />
                        <Line type="monotone" dataKey="temperature" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 6 }} name="Avg Temp" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 3-Day Outlook Wrapper */}
            <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--glass-border)', paddingBottom: '0.5rem' }}>3-Day Outlook</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                {data.map((day, idx) => (
                    <div key={idx} className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.1rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#60a5fa' }}>{day.date}</div>
                        <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{day.temperature.toFixed(1)}°</div>
                        <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '5px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                            <span>💨 Wind: {day.wind_speed.toFixed(1)} km/h</span>
                            <span>🌧 Rain: {day.rain.toFixed(1)} mm</span>
                            <span>☔ Chance: {day.precipitation_probability}%</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* City Insights */}
            <div className="glass-panel" style={{ padding: '2rem', borderLeft: '4px solid #3b82f6' }}>
                <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
                    🌍 {city} Environmental Profile
                </h3>
                <p style={{ lineHeight: '1.6', fontSize: '1.1rem', color: '#e2e8f0' }}>
                    {CITY_INSIGHTS[city] || "Detailed environmental data not available for this location."}
                </p>
            </div>
        </div>
    );
}
