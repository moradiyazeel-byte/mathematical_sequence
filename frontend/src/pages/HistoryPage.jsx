import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { getHistory, deleteHistoryItem, clearHistory as clearHistoryApi } from '../services/api';
import { Search, X } from 'lucide-react';

const HistoryPage = () => {
  const navigate = useNavigate();
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('patternai_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    const fetchBackendHistory = async () => {
      try {
        const res = await getHistory();
        if (res.success && res.data?.records) {
          const records = res.data.records.map((r) => ({
            id: r.id,
            sequence: Array.isArray(r.input_sequence) ? r.input_sequence.join(', ') : String(r.input_sequence || ''),
            pattern: r.pattern_type ? r.pattern_type.charAt(0).toUpperCase() + r.pattern_type.slice(1) + ' Sequence' : 'Sequence',
            formula: r.predicted_next ? `Next: ${r.predicted_next}` : 'N/A',
            confidence: Math.round((r.confidence || 0) * 100),
            date: r.created_at ? new Date(r.created_at).toLocaleDateString() : new Date().toLocaleDateString(),
            time: r.created_at ? new Date(r.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
          }));
          if (records.length > 0) {
            setHistory(records);
            localStorage.setItem('patternai_history', JSON.stringify(records));
          }
        }
      } catch (err) {
        // Fallback to local state if backend fetch fails
      }
    };
    fetchBackendHistory();
  }, []);

  const patterns = ['All', ...new Set(history.map(h => h.pattern.replace(' Sequence', '')))];
  
  const filtered = history.filter(h => {
    return filter === 'All' || h.pattern.includes(filter);
  });

  const deleteOne = async (id) => {
    try {
      await deleteHistoryItem(id);
    } catch (e) {
      // Ignore API errors for guest
    }
    const updated = history.filter(h => h.id !== id);
    setHistory(updated);
    localStorage.setItem('patternai_history', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar historyCount={history.length} />

      {/* Header Area with Wave Background */}
      <div className="bg-hero-gradient pt-32 pb-32 md:pb-40 relative">
         <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3"></div>
         <div className="max-w-4xl mx-auto px-6 relative z-10 flex flex-col items-center text-center">
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-4 drop-shadow-md">
              Analysis History
            </h1>
            <p className="text-primary-50 text-lg max-w-lg mx-auto">
              Review your past sequence predictions and detected mathematical patterns.
            </p>
         </div>
         {/* Wave Divider */}
         <div className="absolute bottom-0 left-0 right-0 w-full overflow-hidden leading-none z-0">
           <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="block w-full h-16 md:h-28">
             <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V120H0V95.8C52.16,93.4,103.9,82.8,155,71.2,209.61,58.74,265.4,66.86,321.39,56.44Z" fill="#f8fafc"></path>
           </svg>
         </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-6 md:px-12 py-8 -mt-6 relative z-20">
        
        {/* Filter Pills */}
        {history.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
            {patterns.map(p => (
              <button 
                key={p} 
                onClick={() => setFilter(p)}
                className={`px-6 py-2 rounded-full font-bold text-sm transition-all border ${
                  filter === p 
                    ? 'bg-gradient-to-r from-primary-400 to-primary-500 text-white border-transparent shadow-md' 
                    : 'bg-white text-slate-600 border-slate-200 hover:border-primary-300'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {/* Empty State */}
        {history.length === 0 && (
          <div className="text-center py-20 bg-white rounded-3xl border border-slate-100 shadow-sm mt-8">
             <div className="w-16 h-16 mx-auto bg-primary-50 rounded-2xl flex items-center justify-center text-primary-500 mb-4">
                <Search size={32} />
             </div>
             <h2 className="text-2xl font-bold text-slate-800 mb-2">No History Yet</h2>
             <p className="text-slate-500 mb-6">Your analyzed sequences will appear here.</p>
             <Link to="/analyze" className="inline-block bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-full font-bold transition-all shadow-lg shadow-primary-500/30 hover:-translate-y-1">
              Analyze a Sequence
            </Link>
          </div>
        )}

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <AnimatePresence>
            {filtered.map((entry, i) => (
              <motion.div 
                key={entry.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.2 }}
                className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 hover:shadow-lg transition-all flex flex-col"
              >
                 {/* Top Badge */}
                 <div className="flex justify-start mb-4">
                    <span className="bg-primary-500 text-white text-xs font-bold px-4 py-1.5 rounded-full">
                       {entry.pattern}
                    </span>
                 </div>
                 
                 <p className="text-xs text-slate-500 font-medium mb-4">{entry.date}, {entry.time}</p>
                 
                 {/* Sequence Box */}
                 <div className="border border-slate-200 rounded-xl p-4 mb-4 font-mono text-slate-700 bg-slate-50/50 break-all text-sm h-16 overflow-hidden">
                    {entry.sequence}
                 </div>
                 
                 {/* Formula & Confidence */}
                 <div className="mb-6 flex-1">
                    <p className="text-xs font-bold text-slate-700 mb-1">Formula / Next Term</p>
                    <div className="bg-gradient-to-r from-primary-100 to-primary-50 rounded-lg p-3 border border-primary-200/50 mb-2 font-mono text-primary-700 font-bold text-sm">
                       {entry.formula}
                    </div>
                    
                    <div className="flex justify-between text-[10px] font-bold text-primary-700 mb-1 mt-3">
                       <span>{entry.confidence}% Confidence</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                       <div className="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full" style={{ width: `${entry.confidence}%` }}></div>
                    </div>
                 </div>

                 {/* Actions */}
                 <div className="flex items-center justify-between gap-3 pt-2">
                    <button 
                       onClick={() => navigate('/analyze', { state: { sequence: entry.sequence } })}
                       className="flex-1 border border-primary-200 text-primary-600 hover:bg-primary-50 font-bold text-sm py-2 rounded-lg transition-colors"
                    >
                       Re-analyze
                    </button>
                    <button 
                       onClick={() => deleteOne(entry.id)}
                       className="w-10 h-10 border border-red-100 text-red-500 hover:bg-red-50 rounded-lg flex items-center justify-center transition-colors"
                    >
                       <X size={18} />
                    </button>
                 </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

      </div>
      <Footer />
    </div>
  );
};

export default HistoryPage;