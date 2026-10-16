import { motion } from "framer-motion";
const steps = ["Validating your sequence...", "Running 20+ pattern detectors...", "Calculating mathematical relationships...", "Generating formula...", "Predicting future values..."];
const LoadingSpinner = () => (
  <div style={{ padding: "80px 40px", display: "flex", flexDirection: "column", alignItems: "center", background: "linear-gradient(135deg, #e6faf7, #b2f0e8)" }}>
    <div style={{ position: "relative", width: "80px", height: "80px", marginBottom: "32px" }}>
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: "linear" }}
        style={{ position: "absolute", inset: 0, border: "3px solid rgba(13,148,136,0.15)", borderTopColor: "#0d9488", borderRadius: "50%" }} />
      <motion.div animate={{ rotate: -360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        style={{ position: "absolute", inset: "10px", border: "2px solid rgba(8,145,178,0.12)", borderTopColor: "#0891b2", borderRadius: "50%" }} />
      <div style={{ position: "absolute", inset: "20px", background: "linear-gradient(135deg, #0d9488, #0891b2)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(13,148,136,0.4)" }}>
        <span style={{ color: "white", fontSize: "13px", fontWeight: "900" }}>P</span>
      </div>
    </div>
    <h3 style={{ fontSize: "24px", fontWeight: "800", color: "#0f2027", marginBottom: "8px" }}>Analyzing Pattern...</h3>
    <p style={{ fontSize: "15px", color: "#64748b", marginBottom: "40px" }}>Give us a second. We are doing math. Lots of it.</p>
    <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%", maxWidth: "380px" }}>
      {steps.map((step, i) => (
        <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.4 }}
          style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 16px", background: "rgba(255,255,255,0.7)", borderRadius: "12px", border: "1px solid rgba(13,148,136,0.12)", backdropFilter: "blur(10px)" }}>
          <motion.div animate={{ scale: [1, 1.6, 1] }} transition={{ duration: 1.5, delay: i * 0.4, repeat: Infinity }}
            style={{ width: "8px", height: "8px", background: "linear-gradient(135deg, #0d9488, #0891b2)", borderRadius: "50%", flexShrink: 0, boxShadow: "0 0 8px rgba(13,148,136,0.5)" }} />
          <span style={{ fontSize: "13px", color: "#475569", fontWeight: "500" }}>{step}</span>
        </motion.div>
      ))}
    </div>
  </div>
);
export default LoadingSpinner;