import { useState } from "react";
import { motion } from "framer-motion";

const InputSection = ({ onAnalyze, loading }) => {
  const [input, setInput] = useState("");
  const examples = ["1, 3, 5, 7, 9", "1, 1, 2, 3, 5, 8", "1, 4, 9, 16, 25", "2, 4, 8, 16, 32", "2, 3, 5, 7, 11", "1, 2, 6, 24, 120"];
  return (
    <section id="analyze" style={{ padding: "100px 40px", background: "white" }}>
      <div style={{ maxWidth: "720px", margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: "48px" }}>
          <h2 style={{ fontSize: "48px", fontWeight: "900", color: "#0f2027", marginBottom: "16px", letterSpacing: "-1.5px" }}>
            Analyze Your Sequence
          </h2>
          <p style={{ fontSize: "18px", color: "#64748b", lineHeight: 1.7 }}>
            Type any numbers separated by commas. Our AI will figure out the rest instantly.
          </p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}
          style={{ background: "white", borderRadius: "24px", padding: "40px", border: "1px solid rgba(13,148,136,0.15)", boxShadow: "0 8px 40px rgba(13,148,136,0.1)" }}>
          <label style={{ display: "block", fontSize: "13px", fontWeight: "700", color: "#0d9488", marginBottom: "12px", textTransform: "uppercase", letterSpacing: "1px" }}>
            Number Sequence
          </label>
          <input type="text" value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && onAnalyze(input)}
            placeholder="e.g.  1, 3, 5, 7, 9"
            style={{ width: "100%", background: "#f8fafc", border: "2px solid #e6faf7", borderRadius: "14px", padding: "18px 20px", fontSize: "20px", color: "#0f2027", outline: "none", marginBottom: "24px", fontFamily: "inherit", boxSizing: "border-box", transition: "all 0.3s" }}
            onFocus={e => { e.target.style.borderColor = "#0d9488"; e.target.style.boxShadow = "0 0 0 4px rgba(13,148,136,0.1)"; e.target.style.background = "white"; }}
            onBlur={e => { e.target.style.borderColor = "#e6faf7"; e.target.style.boxShadow = "none"; e.target.style.background = "#f8fafc"; }} />
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginBottom: "28px", alignItems: "center" }}>
            <span style={{ color: "#94a3b8", fontSize: "13px", fontWeight: "600" }}>Try:</span>
            {examples.map(seq => (
              <motion.button key={seq} onClick={() => setInput(seq)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                style={{ background: "#e6faf7", border: "1px solid rgba(13,148,136,0.2)", color: "#0d9488", fontSize: "12px", padding: "6px 14px", borderRadius: "8px", cursor: "pointer", fontFamily: "inherit", fontWeight: "600", transition: "all 0.2s" }}
                onMouseEnter={e => { e.currentTarget.style.background = "#ccfbf1"; e.currentTarget.style.borderColor = "#0d9488"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "#e6faf7"; e.currentTarget.style.borderColor = "rgba(13,148,136,0.2)"; }}>
                {seq}
              </motion.button>
            ))}
          </div>
          <motion.button onClick={() => onAnalyze(input)} disabled={loading || !input.trim()}
            whileHover={!loading && input.trim() ? { scale: 1.02, y: -1 } : {}} whileTap={!loading && input.trim() ? { scale: 0.98 } : {}}
            style={{ width: "100%", background: loading || !input.trim() ? "#e2e8f0" : "linear-gradient(135deg, #0d9488, #0891b2)", color: loading || !input.trim() ? "#94a3b8" : "white", border: "none", padding: "18px", borderRadius: "14px", fontSize: "18px", fontWeight: "800", cursor: loading || !input.trim() ? "not-allowed" : "pointer", fontFamily: "inherit", boxShadow: loading || !input.trim() ? "none" : "0 8px 30px rgba(13,148,136,0.35)", transition: "all 0.3s", letterSpacing: "-0.3px" }}>
            {loading ? "Analyzing..." : "Analyze Pattern →"}
          </motion.button>
        </motion.div>
      </div>
    </section>
  );
};
export default InputSection;