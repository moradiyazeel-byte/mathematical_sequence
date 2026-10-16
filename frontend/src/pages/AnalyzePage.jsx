import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import ExplanationCard from "../components/ExplanationCard";
import OEISCard from "../components/OEISCard";
import useAnalyze from "../hooks/useAnalyze";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Sparkles, Edit2, CheckCircle2, AlertTriangle } from "lucide-react";

const AnalyzePage = () => {
  const { result, loading, error, analyze, reset } = useAnalyze();
  const [history, setHistory] = useState(() => JSON.parse(localStorage.getItem("patternai_history") || "[]"));
  const [input, setInput] = useState("");

  const templates = [
    { label: "Fibonacci", seq: "1, 1, 2, 3, 5, 8" },
    { label: "Geometric", seq: "2, 4, 8, 16, 32" },
    { label: "Arithmetic", seq: "2, 5, 8, 11, 14, 17" },
    { label: "Quadratic", seq: "1, 4, 9, 16, 25" },
    { label: "Triangular", seq: "1, 3, 6, 10, 15" },
    { label: "Prime", seq: "2, 3, 5, 7, 11" }
  ];

  const saveHistory = (res) => {
    if (!res || !input || !res.success) return;
    const entry = { id: res.id || Date.now(), sequence: input.trim(), pattern: res.pattern_name, formula: res.formula, confidence: res.confidence, time: new Date().toLocaleTimeString(), date: new Date().toLocaleDateString() };
    const updated = [entry, ...history.filter(h => h.sequence !== entry.sequence).slice(0, 19)];
    setHistory(updated);
    localStorage.setItem("patternai_history", JSON.stringify(updated));
  };

  const handleAnalyze = async (seq) => {
    setInput(seq);
    await analyze(seq);
    if(result) saveHistory(result);
  };

  const actualSequence = result && result.success ? result.graph_data.filter(d => !d.predicted).map(d => d.value) : [];
  const isFound = result?.is_pattern_found && result?.predictions?.length > 0;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar historyCount={history.length} />

      {/* Hero Header Area */}
      <div className="bg-hero-gradient pt-32 pb-48 relative z-0">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3"></div>
        {/* Wave Divider */}
        <div className="absolute bottom-0 left-0 right-0 w-full overflow-hidden leading-none z-0">
           <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="block w-full h-16 md:h-28">
             <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V120H0V95.8C52.16,93.4,103.9,82.8,155,71.2,209.61,58.74,265.4,66.86,321.39,56.44Z" fill="#f8fafc"></path>
           </svg>
        </div>
      </div>

      <div className="flex-1 max-w-7xl mx-auto w-full px-6 md:px-12 -mt-64 relative z-10 mb-20">
        
        {/* Input Box */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white/90 backdrop-blur-md rounded-2xl shadow-xl p-6 md:p-12 mb-8 border border-white/50 max-w-5xl mx-auto">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze(input)}
            placeholder="e.g. 2, 5, 10, 17, 26, 37..."
            className="w-full text-2xl md:text-3xl font-mono text-slate-800 text-center outline-none bg-transparent border-2 border-primary-200 rounded-xl py-6 px-4 focus:border-primary-500 focus:ring-4 focus:ring-primary-100 transition-all placeholder-slate-300"
          />
          
          <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
            {templates.map((t, i) => (
              <button 
                key={i} 
                onClick={() => setInput(t.seq)}
                className="px-4 py-1.5 rounded-full border border-primary-200 text-primary-600 text-sm font-semibold hover:bg-primary-50 transition-colors bg-white shadow-sm"
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="mt-6 text-center">
             <button 
                onClick={() => handleAnalyze(input)} 
                disabled={loading || !input.trim()}
                className="bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-all"
             >
                {loading ? "Analyzing..." : "Analyze"}
             </button>
          </div>
        </motion.div>

        {error && (
           <div className="bg-red-50 border border-red-200 text-red-600 p-4 rounded-xl text-center font-semibold mb-8 shadow-sm">
              {error}
           </div>
        )}

        {/* Results Area */}
        <AnimatePresence>
          {result && result.success && !loading ? (
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-6">
              
              {/* Detected or No Pattern Badge */}
              <div className="flex justify-center mb-4">
                 {isFound ? (
                   <div className="bg-gradient-to-r from-primary-400 to-primary-600 text-white font-extrabold text-xl px-8 py-3 rounded-2xl shadow-lg border border-primary-300/50">
                      Detected: {result.pattern_name.replace(' Sequence', '')}
                   </div>
                 ) : (
                   <div className="bg-amber-500 text-white font-extrabold text-xl px-8 py-3 rounded-2xl shadow-lg border border-amber-400 flex items-center gap-3">
                      <AlertTriangle size={24} /> No Standard Pattern Detected
                   </div>
                 )}
              </div>

              {/* Grid Top Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Formula Card */}
                <div className={`p-6 md:p-8 rounded-3xl shadow-md text-white relative overflow-hidden flex flex-col justify-between ${isFound ? 'bg-gradient-to-br from-primary-500 to-primary-600' : 'bg-slate-700'}`}>
                   <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full blur-2xl translate-x-1/2 -translate-y-1/2"></div>
                   <div>
                     <h3 className="font-bold text-slate-100 mb-4 text-sm tracking-wide uppercase">Formula Status</h3>
                     <p className="text-sm font-medium text-slate-200 mb-2">{isFound ? 'Formula:' : 'Status:'}</p>
                     <p className="font-mono text-2xl md:text-3xl font-bold mb-4">{result.formula}</p>
                   </div>
                   <div className="flex items-center gap-2 text-slate-200 text-xs font-semibold pt-4 border-t border-white/20 mt-8">
                      <Edit2 size={14} /> Tested against 20+ mathematical families
                   </div>
                </div>

                {/* Confidence Card */}
                <div className="bg-white p-6 md:p-8 rounded-3xl shadow-sm border border-slate-100 flex flex-col justify-between items-center text-center">
                   <h3 className="font-bold text-slate-800 mb-4 text-sm tracking-wide uppercase w-full text-left">Confidence Level</h3>
                   
                   {/* Radial Progress */}
                   <div className="relative w-32 h-32 flex items-center justify-center">
                     <ResponsiveContainer width="100%" height="100%">
                       <PieChart>
                         <Pie
                           data={[{ value: result.confidence }, { value: Math.max(100 - result.confidence, 1) }]}
                           cx="50%"
                           cy="50%"
                           innerRadius={45}
                           outerRadius={60}
                           startAngle={90}
                           endAngle={-270}
                           dataKey="value"
                           stroke="none"
                         >
                           <Cell fill={isFound ? "#0d9488" : "#94a3b8"} />
                           <Cell fill="#f1f5f9" />
                         </Pie>
                       </PieChart>
                     </ResponsiveContainer>
                     <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className={`text-3xl font-extrabold ${isFound ? 'text-primary-600' : 'text-slate-500'}`}>{result.confidence.toFixed(0)}%</span>
                     </div>
                   </div>
                   <p className="text-slate-600 text-xs font-bold mt-2">{isFound ? "Pattern Matched" : "No Law Found"}</p>

                   <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold pt-4 border-t border-slate-100 mt-6 w-full justify-start">
                      {isFound ? (
                        <><CheckCircle2 size={14} className="text-emerald-500" /> Pattern Verified</>
                      ) : (
                        <><AlertTriangle size={14} className="text-amber-500" /> Irregular sequence terms</>
                      )}
                   </div>
                </div>

              </div>

              {/* Chart Full Width */}
              <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
                <h3 className="font-bold text-slate-800 mb-6 text-sm tracking-wide uppercase text-center">{isFound ? "Actual vs Predicted Values" : "Observed Sequence Values"}</h3>
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={result.graph_data} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="index" tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                    <YAxis tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                    <RechartsTooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                    <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6'}} name="Observed Terms" connectNulls />
                    {isFound && (
                      <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={3} strokeDasharray="5 5" dot={{r: 4, fill: '#f59e0b'}} name="Predicted" connectNulls />
                    )}
                  </LineChart>
                </ResponsiveContainer>
                <div className="flex justify-center items-center gap-6 mt-4">
                  <div className="flex items-center gap-2"><div className="w-3 h-1 bg-blue-500 rounded"></div><span className="text-xs text-slate-500 font-bold">Observed Terms</span></div>
                  {isFound && (
                    <div className="flex items-center gap-2"><div className="w-3 h-1 border-t-2 border-dashed border-amber-500"></div><span className="text-xs text-slate-500 font-bold">Predicted Next Terms</span></div>
                  )}
                </div>
              </div>

              {/* Next 5 Values Card (ONLY shown when pattern is verified) */}
              {isFound && (
                <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
                  <div className="bg-gradient-to-r from-primary-400 to-primary-600 px-6 py-4">
                    <h3 className="font-bold text-white text-sm tracking-wide uppercase text-center">Next 5 Extrapolated Values</h3>
                  </div>
                  <div className="p-8 flex items-center justify-center flex-1 text-center">
                    <p className="text-3xl md:text-4xl font-extrabold text-slate-800 leading-tight font-mono">
                      {result.predictions.slice(0, 5).join(", ")}
                    </p>
                  </div>
                </div>
              )}

              {/* Deep Mathematical Derivation & Proof Component */}
              <ExplanationCard
                explanation={result.explanation}
                derivation={result.derivation}
                patternName={result.pattern_name}
              />

              {/* OEIS Database Lookup Component */}
              <OEISCard sequence={actualSequence} />

            </motion.div>
          ) : !loading && !error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center text-center mt-12 mb-8 opacity-60">
              <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center mb-6 shadow-inner">
                <Sparkles size={32} className="text-slate-400" />
              </div>
              <h3 className="text-xl font-bold text-slate-400 mb-2">Ready to Discover Patterns</h3>
              <p className="text-slate-400 max-w-sm">Enter a mathematical sequence above to instantly reveal its hidden formula, graphical representation, and next predicted values.</p>
            </motion.div>
          )}
        </AnimatePresence>

      </div>
      <Footer />
    </div>
  );
};

export default AnalyzePage;