import { motion } from "framer-motion";
const PredictionCard = ({ predictions, sequence }) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
    style={{ background: "white", borderRadius: "20px", padding: "28px", border: "1px solid #e6faf7", boxShadow: "0 4px 16px rgba(13,148,136,0.06)" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "24px" }}>
      <div style={{ width: "44px", height: "44px", background: "linear-gradient(135deg, #e6faf7, #ccfbf1)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid rgba(13,148,136,0.15)" }}>
        <span style={{ color: "#0d9488", fontSize: "20px", fontWeight: "900" }}>→</span>
      </div>
      <div>
        <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#0f2027", margin: 0 }}>Next Value Predictions</h3>
        <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>AI predicted next 5 values</p>
      </div>
    </div>
    <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
      {sequence.slice(-3).map((val, i) => (
        <div key={i} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: "12px", padding: "12px 16px", textAlign: "center" }}>
          <p style={{ fontSize: "16px", fontWeight: "700", color: "#94a3b8", margin: 0, fontFamily: "monospace" }}>{val}</p>
          <p style={{ fontSize: "11px", color: "#cbd5e1", margin: 0 }}>n-{2 - i}</p>
        </div>
      ))}
      <div style={{ color: "#cbd5e1", fontSize: "24px" }}>···</div>
      {predictions.map((val, i) => (
        <motion.div key={i} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 + i * 0.1 }}
          style={{ background: "linear-gradient(135deg, #e6faf7, #ccfbf1)", border: "2px solid rgba(13,148,136,0.25)", borderRadius: "12px", padding: "12px 16px", textAlign: "center", boxShadow: "0 4px 12px rgba(13,148,136,0.12)" }}>
          <p style={{ fontSize: "16px", fontWeight: "800", color: "#0d9488", margin: 0, fontFamily: "monospace" }}>{typeof val === "number" ? parseFloat(val.toFixed(2)) : val}</p>
          <p style={{ fontSize: "11px", color: "#14b8a6", margin: 0, fontWeight: "700" }}>+{i + 1}</p>
        </motion.div>
      ))}
    </div>
  </motion.div>
);
export default PredictionCard;