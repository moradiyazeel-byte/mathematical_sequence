import { motion } from "framer-motion";
const FormulaCard = ({ formula, patternName }) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
    style={{ background: "white", borderRadius: "20px", padding: "28px", border: "1px solid #e6faf7", boxShadow: "0 4px 20px rgba(13,148,136,0.08)", height: "100%" }}>
    <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
      <div style={{ width: "44px", height: "44px", background: "linear-gradient(135deg, #e6faf7, #ccfbf1)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid rgba(13,148,136,0.15)" }}>
        <span style={{ color: "#0d9488", fontSize: "20px", fontWeight: "900" }}>f</span>
      </div>
      <div>
        <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#0f2027", margin: 0 }}>Mathematical Formula</h3>
        <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>{patternName}</p>
      </div>
    </div>
    <div style={{ background: "linear-gradient(135deg, #e6faf7, #ccfbf1)", borderRadius: "14px", padding: "22px", textAlign: "center", border: "1px solid rgba(13,148,136,0.12)" }}>
      <p style={{ fontSize: "22px", fontWeight: "800", color: "#0d9488", fontFamily: "monospace", margin: 0 }}>{formula}</p>
    </div>
  </motion.div>
);
export default FormulaCard;