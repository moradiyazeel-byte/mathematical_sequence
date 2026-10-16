import { motion } from 'framer-motion';
import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { FileText, BarChart2, Search, Sparkles } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';

const DashboardPage = () => {
  const history = useMemo(() => {
    const saved = localStorage.getItem('patternai_history');
    return saved ? JSON.parse(saved) : [];
  }, []);

  const totalAnalyses = history.length;
  const avgConfidence = totalAnalyses > 0
    ? (history.reduce((sum, h) => sum + h.confidence, 0) / totalAnalyses).toFixed(0)
    : 0;

  const patternCounts = history.reduce((acc, h) => {
    acc[h.pattern] = (acc[h.pattern] || 0) + 1;
    return acc;
  }, {});

  const pieData = Object.entries(patternCounts).map(([name, value]) => ({ name, value }));
  const mostDetected = Object.entries(patternCounts).sort((a, b) => b[1] - a[1])[0];

  const COLORS = ['#2dd4bf', '#0ea5e9', '#6366f1', '#a78bfa', '#f472b6'];

  const trendData = history.slice().reverse().map((h, i) => ({
    index: i,
    confidence: h.confidence,
    name: h.pattern,
  }));

  const highConfidence = history.filter(h => h.confidence >= 90).length;
  const uniquePatterns = new Set(history.map(h => h.pattern)).size;

  const stats = [
    { label: 'Total Analyses', value: totalAnalyses.toLocaleString(), icon: <FileText size={20} />, bg: 'bg-primary-50', color: 'text-primary-600' },
    { label: 'Avg Confidence', value: `${avgConfidence}%`, icon: <BarChart2 size={20} />, bg: 'bg-green-50', color: 'text-green-600' },
    { label: 'Unique Patterns', value: uniquePatterns, icon: <Search size={20} />, bg: 'bg-indigo-50', color: 'text-indigo-600' },
    { label: 'High Accuracy', value: highConfidence, icon: <Sparkles size={20} />, bg: 'bg-amber-50', color: 'text-amber-600' },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar historyCount={history.length} />

      <div className="max-w-7xl mx-auto px-6 md:px-12 pt-32 pb-20">
        
        <h1 className="text-3xl font-bold text-slate-800 mb-8">User Dashboard</h1>

        {totalAnalyses === 0 ? (
           <div className="bg-white rounded-2xl p-12 text-center border border-slate-100 shadow-sm">
             <h2 className="text-xl font-bold text-slate-700 mb-4">No Data Yet</h2>
             <p className="text-slate-500 mb-6">Analyze some sequences to populate your dashboard.</p>
             <Link to="/analyze" className="inline-block bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-all hover:-translate-y-0.5">
            Start Analyzing Data
          </Link>
           </div>
        ) : (
          <>
            {/* 4 Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, i) => (
                <div key={i} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-between">
                  <div className={`w-10 h-10 rounded-xl ${stat.bg} ${stat.color} flex items-center justify-center mb-4`}>
                    {stat.icon}
                  </div>
                  <div>
                    <h3 className="text-3xl font-extrabold text-slate-800 mb-1">{stat.value}</h3>
                    <p className="text-slate-500 text-sm font-medium">{stat.label}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Banner */}
            <div className="bg-hero-gradient rounded-2xl p-8 mb-8 flex items-center gap-6 shadow-md relative overflow-hidden">
               <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3"></div>
               <div className="text-5xl relative z-10 drop-shadow-md">🏆</div>
               <div className="relative z-10">
                 <h2 className="text-2xl font-bold text-white mb-2">Best Pattern of the Week: {mostDetected ? mostDetected[0] : 'None'} (98.5% Confidence)</h2>
                 <p className="text-primary-50 text-sm">Sample Sequence: 2, 4, 8, 16, 55, 89, 144, 226, ...</p>
               </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              
              {/* Confidence Trend */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Confidence Trend</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorConf" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#0d9488" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#0d9488" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="index" tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                    <YAxis tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} domain={[0, 100]} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                    <Area type="monotone" dataKey="confidence" stroke="#0d9488" strokeWidth={3} fillOpacity={1} fill="url(#colorConf)" name="Confidence %" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Pattern Distribution */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center">
                <h3 className="text-lg font-bold text-slate-800 mb-2 w-full text-left">Pattern Distribution</h3>
                <div className="flex-1 w-full flex flex-col items-center justify-center">
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                    </PieChart>
                  </ResponsiveContainer>
                  
                  {/* Custom Legend */}
                  <div className="flex flex-wrap justify-center gap-4 mt-4">
                    {pieData.map((entry, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }}></div>
                        <span className="text-xs text-slate-600 font-medium">{entry.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
              <h3 className="text-lg font-bold text-slate-800 mb-6">Recent Activity</h3>
              <div className="flex flex-col gap-3">
                {history.slice(0, 5).map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                    <div>
                      <h4 className="font-bold text-slate-700 text-sm mb-1">{item.pattern} Analysis</h4>
                      <p className="text-xs text-slate-500">Sequence: {item.sequence.substring(0, 20)}... <span className="text-slate-400 mx-1">|</span> Confidence: {item.confidence}%</p>
                    </div>
                    <div className="w-32 h-2.5 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full" style={{ width: `${item.confidence}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

          </>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default DashboardPage;