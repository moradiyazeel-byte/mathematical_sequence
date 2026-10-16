import { motion } from "framer-motion";
const ConfidenceCard = ({ confidence }) => {
  const color = confidence >= 90 ? "#0d9488" : confidence >= 70 ? "#0891b2" : "#f59e0b";
  const label = confidence >= 90 ? "Excellent Match!" : confidence >= 70 ? "Good Match" : "Partial Match";
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}
      style={{ background: "white", borderRadius: "20px", padding: "28px", border: `1px solid ${color}20`, boxShadow: `0 4px 20px ${color}10`, height: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
        <div style={{ width: "44px", height: "44px", background: color + "12", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: `1px solid ${color}18` }}>
          <span style={{ color, fontSize: "20px", fontWeight: "900" }}>%</span>
        </div>
        <div>
          <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#0f2027", margin: 0 }}>Confidence Score</h3>
          <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>Pattern match accuracy</p>
        </div>
      </div>
      <div style={{ textAlign: "center", marginBottom: "16px" }}>
        <motion.span initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3, type: "spring" }}
          style={{ fontSize: "56px", fontWeight: "900", color, lineHeight: 1, display: "block" }}>
          {confidence.toFixed(1)}%
        </motion.span>
        <span style={{ fontSize: "14px", fontWeight: "700", color }}>{label}</span>
      </div>
      <div style={{ background: "#f1f5f9", borderRadius: "100px", height: "8px", overflow: "hidden" }}>
        <motion.div initial={{ width: 0 }} animate={{ width: `${confidence}%` }} transition={{ duration: 1.2, delay: 0.4, ease: "easeOut" }}
          style={{ height: "100%", background: `linear-gradient(90deg, ${color}, ${color}99)`, borderRadius: "100px" }} />
      </div>
    </motion.div>
  );
};
export default ConfidenceCard;