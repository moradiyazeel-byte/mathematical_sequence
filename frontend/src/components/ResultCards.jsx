import { motion } from "framer-motion";
import { useEffect } from "react";
import FormulaCard from "./FormulaCard";
import ConfidenceCard from "./ConfidenceCard";
import PredictionCard from "./PredictionCard";
import ExplanationCard from "./ExplanationCard";
import GraphSection from "./GraphSection";
import OEISCard from "./OEISCard";

const NoPatternFound = () => (
  <section style={{ padding: "60px 40px", background: "#f0fdfb" }}>
    <div style={{ maxWidth: "720px", margin: "0 auto" }}>
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        style={{ background: "white", borderRadius: "24px", padding: "48px", textAlign: "center", border: "1px solid #fecaca", boxShadow: "0 4px 20px rgba(239,68,68,0.08)" }}>
        <div style={{ width: "80px", height: "80px", background: "#fef2f2", borderRadius: "20px", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 24px", border: "1px solid #fecaca" }}>
          <span style={{ fontSize: "36px" }}>🔍</span>
        </div>
        <h2 style={{ fontSize: "28px", fontWeight: "800", color: "#0f2027", marginBottom: "12px" }}>No Pattern Detected</h2>
        <p style={{ fontSize: "16px", color: "#64748b", marginBottom: "32px", lineHeight: 1.7 }}>
          We ran 20+ algorithms on your sequence and found nothing. Either this is truly random, or you just broke our AI!
          <span style={{ color: "#0d9488", fontWeight: "700" }}> (We prefer to think it is the first one.)</span>
        </p>
        <div style={{ background: "#f8fafc", borderRadius: "16px", padding: "24px", marginBottom: "32px", textAlign: "left", border: "1px solid #e6faf7" }}>
          <h3 style={{ fontSize: "15px", fontWeight: "700", color: "#0f2027", marginBottom: "16px" }}>Try these known patterns:</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {[{ label: "Arithmetic", seq: "1, 3, 5, 7, 9" }, { label: "Fibonacci", seq: "1, 1, 2, 3, 5, 8" }, { label: "Squares", seq: "1, 4, 9, 16, 25" }, { label: "Factorial", seq: "1, 2, 6, 24, 120" }, { label: "Lucas", seq: "2, 1, 3, 4, 7, 11" }].map((item, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: "12px", padding: "10px 14px", background: "white", borderRadius: "10px", border: "1px solid #e6faf7" }}>
                <span style={{ fontSize: "12px", fontWeight: "700", color: "#0d9488", background: "#e6faf7", padding: "3px 10px", borderRadius: "100px" }}>{item.label}</span>
                <span style={{ fontSize: "13px", color: "#475569", fontFamily: "monospace", fontWeight: "600" }}>{item.seq}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ marginBottom: "32px" }}>
          <p style={{ fontSize: "13px", color: "#94a3b8", marginBottom: "12px" }}>We checked all of these:</p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center" }}>
            {["Arithmetic","Geometric","Fibonacci","Lucas","Prime","Square","Cube","Triangular","Factorial","Catalan","Pell","Pentagonal","Hexagonal","Harmonic","Exponential","Logarithmic","Armstrong","Perfect","Power","Polynomial"].map((p, i) => (
              <span key={i} style={{ fontSize: "11px", fontWeight: "600", color: "#0d9488", background: "#e6faf7", padding: "3px 10px", borderRadius: "100px", border: "1px solid rgba(13,148,136,0.15)" }}>{p}</span>
            ))}
          </div>
        </div>
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          style={{ background: "linear-gradient(135deg, #0d9488, #0891b2)", color: "white", border: "none", padding: "16px 40px", borderRadius: "14px", fontSize: "16px", fontWeight: "800", cursor: "pointer", fontFamily: "inherit", boxShadow: "0 8px 25px rgba(13,148,136,0.3)" }}>
          Try Another Sequence
        </motion.button>
      </motion.div>
    </div>
  </section>
);

const ResultCards = ({ result, onSave }) => {
  useEffect(() => { if (result && onSave && result.success) onSave(); }, [result]);
  if (!result) return null;
  if (!result.success || !result.predictions || result.predictions.length === 0) return <NoPatternFound />;
  const actualSequence = result.graph_data.filter(d => !d.predicted).map(d => d.value);
  return (
    <section style={{ padding: "80px 40px", background: "linear-gradient(180deg, #f0fdfb 0%, white 40%)" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} style={{ textAlign: "center", marginBottom: "56px" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: "12px", background: "white", border: "1px solid rgba(13,148,136,0.2)", borderRadius: "100px", padding: "12px 32px", boxShadow: "0 4px 20px rgba(13,148,136,0.1)" }}>
            <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ duration: 2, repeat: Infinity }}
              style={{ width: "10px", height: "10px", background: "linear-gradient(135deg, #0d9488, #0891b2)", borderRadius: "50%", boxShadow: "0 0 8px rgba(13,148,136,0.6)" }} />
            <span style={{ fontSize: "18px", fontWeight: "700", color: "#0f2027" }}>
              Detected: <span style={{ color: "#0d9488" }}>{result.pattern_name}</span>
            </span>
          </div>
        </motion.div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "24px" }}>
          <FormulaCard formula={result.formula} patternName={result.pattern_name} />
          <ConfidenceCard confidence={result.confidence} />
        </div>
        <div style={{ marginBottom: "24px" }}><GraphSection graphData={result.graph_data} sequence={actualSequence} /></div>
        <div style={{ marginBottom: "24px" }}><PredictionCard predictions={result.predictions} sequence={actualSequence} /></div>
        <div style={{ marginBottom: "24px" }}><ExplanationCard explanation={result.explanation} derivation={result.derivation} patternName={result.pattern_name} /></div>
        <div style={{ marginBottom: "24px" }}><OEISCard sequence={actualSequence} /></div>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          style={{ background: "white", borderRadius: "20px", padding: "32px", border: "1px solid #e6faf7", boxShadow: "0 4px 16px rgba(13,148,136,0.06)" }}>
          <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#0f2027", marginBottom: "20px" }}>All Pattern Scores</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" }}>
            {result.all_patterns.map((pattern, i) => (
              <motion.div key={i} initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5 + i * 0.03 }}
                style={{ borderRadius: "14px", padding: "16px", border: pattern.is_detected ? "1px solid rgba(13,148,136,0.25)" : "1px solid #f1f5f9", background: pattern.is_detected ? "linear-gradient(135deg, #e6faf7, #ccfbf1)" : "#f8fafc" }}>
                <p style={{ fontSize: "11px", fontWeight: "600", color: pattern.is_detected ? "#0d9488" : "#94a3b8", margin: "0 0 8px" }}>{pattern.pattern_name}</p>
                <p style={{ fontSize: "24px", fontWeight: "900", color: pattern.is_detected ? "#0d9488" : "#e2e8f0", margin: "0 0 6px" }}>{pattern.confidence.toFixed(0)}%</p>
                {pattern.is_detected && <span style={{ fontSize: "10px", fontWeight: "700", color: "#0d9488", background: "#ccfbf1", padding: "2px 8px", borderRadius: "100px", border: "1px solid rgba(13,148,136,0.2)" }}>Detected ✓</span>}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};
export default ResultCards;