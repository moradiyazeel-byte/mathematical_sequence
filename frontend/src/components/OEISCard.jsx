import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getOeisInfo } from "../services/api";

const OEISCard = ({ sequence }) => {
  const [oeisData, setOeisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    if (!sequence || sequence.length < 3) {
      setLoading(false);
      return;
    }

    const fetchOeis = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await getOeisInfo(sequence);
        if (active) {
          setOeisData(res.data);
          setLoading(false);
        }
      } catch (err) {
        if (active) {
          setError(err.message || "Failed to load OEIS data.");
          setLoading(false);
        }
      }
    };

    fetchOeis();

    return () => {
      active = false;
    };
  }, [sequence]);

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: "white",
          borderRadius: "20px",
          padding: "28px",
          border: "1px solid #e6faf7",
          boxShadow: "0 4px 16px rgba(13,148,136,0.06)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "20px" }}>
          <div style={{ width: "44px", height: "44px", background: "#f1f5f9", borderRadius: "12px" }} />
          <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
            <div style={{ width: "180px", height: "16px", background: "#e2e8f0", borderRadius: "4px" }} />
            <div style={{ width: "120px", height: "12px", background: "#f1f5f9", borderRadius: "4px" }} />
          </div>
        </div>
        <motion.div
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          style={{ display: "flex", flexDirection: "column", gap: "10px" }}
        >
          <div style={{ width: "100%", height: "40px", background: "#f1f5f9", borderRadius: "8px" }} />
          <div style={{ width: "90%", height: "20px", background: "#f1f5f9", borderRadius: "8px" }} />
          <div style={{ width: "80%", height: "20px", background: "#f1f5f9", borderRadius: "8px" }} />
        </motion.div>
      </motion.div>
    );
  }

  // If there's an error or no sequence found in OEIS, fail silently (render nothing)
  // to avoid cluttering the prediction results screen.
  if (error || !oeisData || !oeisData.found) {
    return null;
  }

  const { oeis_id, name, comments, formulas } = oeisData.data;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      style={{
        background: "white",
        borderRadius: "20px",
        padding: "28px",
        border: "1px solid #e6faf7",
        boxShadow: "0 4px 16px rgba(13,148,136,0.06)",
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{ width: "44px", height: "44px", background: "linear-gradient(135deg, #e0f2fe, #bae6fd)", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid rgba(8,145,178,0.15)" }}>
            <span style={{ color: "#0891b2", fontSize: "20px", fontWeight: "900" }}>📚</span>
          </div>
          <div>
            <h3 style={{ fontSize: "16px", fontWeight: "700", color: "#0f2027", margin: 0 }}>Historical & Mathematical Insights</h3>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>Verified records from the OEIS Encyclopedia</p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span style={{ fontSize: "12px", color: "#94a3b8", fontWeight: "600" }}>Catalog ID:</span>
          <span style={{ fontSize: "12px", color: "#0d9488", background: "#e6faf7", border: "1px solid rgba(13,148,136,0.25)", padding: "3px 10px", borderRadius: "100px", fontWeight: "700", fontFamily: "monospace" }}>
            {oeis_id}
          </span>
        </div>
      </div>

      {/* Content */}
      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        {/* Name / Description */}
        <div style={{ background: "linear-gradient(135deg, #f8fafc, #f1f5f9)", borderRadius: "14px", padding: "18px", border: "1px solid #e2e8f0" }}>
          <span style={{ fontSize: "11px", fontWeight: "800", color: "#0d9488", textTransform: "uppercase", display: "block", marginBottom: "6px", letterSpacing: "0.5px" }}>Official Description</span>
          <p style={{ fontSize: "15px", color: "#1e293b", margin: 0, fontWeight: "700", lineHeight: 1.6 }}>
            {name}
          </p>
        </div>

        {/* Formulas */}
        {formulas && formulas.length > 0 && (
          <div>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", display: "block", marginBottom: "8px" }}>Mathematical Formulas</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
              {formulas.map((form, idx) => (
                <div key={idx} style={{ background: "#f8fafc", borderRadius: "10px", padding: "12px 16px", border: "1px solid #f1f5f9", fontFamily: "monospace", fontSize: "13px", color: "#0891b2", wordBreak: "break-all", lineHeight: 1.4 }}>
                  {form}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Comments/Facts */}
        {comments && comments.length > 0 && (
          <div>
            <span style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", display: "block", marginBottom: "8px" }}>Historical Facts & Gaps</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {comments.map((comm, idx) => (
                <div key={idx} style={{ display: "flex", gap: "12px", alignItems: "flex-start", background: "#f8fafc", borderRadius: "10px", padding: "12px 14px", border: "1px solid #f1f5f9" }}>
                  <div style={{ width: "6px", height: "6px", background: "#0d9488", borderRadius: "50%", marginTop: "7px", flexShrink: 0 }} />
                  <p style={{ fontSize: "13px", color: "#475569", margin: 0, lineHeight: 1.5, fontWeight: "500" }}>
                    {comm}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Subtle Footer Reference */}
        <div style={{ display: "flex", justifyContent: "flex-end", borderTop: "1px dashed #f1f5f9", paddingTop: "12px" }}>
          <a
            href={`https://oeis.org/${oeis_id}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: "11px", color: "#94a3b8", textDecoration: "none", fontWeight: "600", display: "inline-flex", alignItems: "center", gap: "4px" }}
            className="hover:text-teal-600 transition-colors"
          >
            Source: On-Line Encyclopedia of Integer Sequences ↗
          </a>
        </div>
      </div>
    </motion.div>
  );
};

export default OEISCard;
