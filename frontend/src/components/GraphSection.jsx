import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: "white", border: "1px solid rgba(13,148,136,0.2)", borderRadius: "12px", padding: "12px 16px", boxShadow: "0 8px 24px rgba(13,148,136,0.12)" }}>
        <p style={{ fontSize: "12px", color: "#94a3b8", margin: "0 0 4px", fontWeight: "600" }}>Position {label}</p>
        {payload.map((p, i) => p.value !== null && p.value !== undefined && (
          <p key={i} style={{ fontSize: "15px", fontWeight: "800", color: p.color, margin: 0 }}>
            {p.name}: {typeof p.value === "number" ? parseFloat(p.value.toFixed(2)) : p.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};
const GraphSection = ({ graphData, sequence }) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
    style={{ background: "white", borderRadius: "20px", padding: "28px", border: "1px solid #e6faf7", boxShadow: "0 4px 16px rgba(13,148,136,0.06)" }}>
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div style={{ width: "44px", height: "44px", background: "linear-gradient(135deg, #e0f2fe, #bae6fd)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid rgba(8,145,178,0.15)" }}>
          <span style={{ color: "#0891b2", fontSize: "18px", fontWeight: "900" }}>~</span>
        </div>
        <div>
          <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#0f2027", margin: 0 }}>Pattern Visualization</h3>
          <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>Actual values + AI predictions</p>
        </div>
      </div>
      <div style={{ display: "flex", gap: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "14px", height: "3px", background: "#0d9488", borderRadius: "2px" }} />
          <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "600" }}>Actual</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div style={{ width: "14px", height: "3px", background: "#0891b2", borderRadius: "2px" }} />
          <span style={{ fontSize: "12px", color: "#64748b", fontWeight: "600" }}>Predicted</span>
        </div>
      </div>
    </div>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={graphData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
        <XAxis dataKey="index" stroke="#e2e8f0" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} label={{ value: "Position (n)", position: "insideBottom", offset: -10, fill: "#94a3b8", fontSize: 12 }} />
        <YAxis stroke="#e2e8f0" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip content={<CustomTooltip />} />
        <ReferenceLine x={sequence.length + 0.5} stroke="#e2e8f0" strokeDasharray="4 4" label={{ value: "Predictions", position: "top", fill: "#0d9488", fontSize: 11, fontWeight: "700" }} />
        <Line type="monotone" dataKey="value" stroke="#0d9488" strokeWidth={2.5} dot={{ fill: "#0d9488", r: 5, strokeWidth: 2, stroke: "white" }} activeDot={{ r: 7 }} name="Actual" />
        <Line type="monotone" dataKey="predicted" stroke="#0891b2" strokeWidth={2.5} strokeDasharray="6 3" dot={{ fill: "#0891b2", r: 5, strokeWidth: 2, stroke: "white" }} name="Predicted" />
      </LineChart>
    </ResponsiveContainer>
  </motion.div>
);
export default GraphSection;