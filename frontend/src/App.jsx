import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';
import Predict from './components/Predict';
import Analysis from './components/Analysis';
import { LayoutDashboard, BarChart3, BrainCircuit, Network } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'predict', label: 'AI Predictions', icon: BrainCircuit },
    { id: 'analysis', label: 'Cluster Analysis', icon: Network },
  ];

  return (
    <div className="layout-container">
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, #60a5fa, #a78bfa)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Climate Intelligence Platform
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>Real-Time Environmental Monitoring & AI Forecasting</p>
      </header>

      <nav className="tab-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <tab.icon size={18} />
            {tab.label}
          </button>
        ))}
      </nav>

      <main className="glass-panel" style={{ padding: '2rem', minHeight: '600px' }}>
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'analytics' && <Analytics />}
        {activeTab === 'predict' && <Predict />}
        {activeTab === 'analysis' && <Analysis />}
      </main>
    </div>
  );
}

export default App;
