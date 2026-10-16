import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const cleanMathText = (text) => {
  if (!text || typeof text !== "string") return text;
  return text
    .replace(/\$\$(.*?)\$\$/g, "$1")
    .replace(/\$(.*?)\$/g, "$1")
    .replace(/\\mathbf\{([^}]+)\}/g, "$1")
    .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, "($1 / $2)")
    .replace(/\\cdot/g, "·")
    .replace(/\\times/g, "×")
    .replace(/\\implies/g, "➔")
    .replace(/\\Delta_?(\d?)/g, "Δ$1")
    .replace(/\\sqrt\{([^}]+)\}/g, "√$1");
};

const ExplanationCard = ({ explanation, derivation, patternName }) => {
  const [activeTab, setActiveTab] = useState("derivation");

  // Fallback steps if derivation object is not present
  const hasDerivation = derivation && derivation.steps && derivation.steps.length > 0;
  const rawSteps = hasDerivation
    ? derivation.steps
    : (explanation || []).map((stepText, idx) => ({
        step_number: idx + 1,
        title: `Step ${idx + 1}`,
        explanation: stepText,
      }));

  const steps = rawSteps.map((s) => ({
    ...s,
    title: cleanMathText(s.title),
    explanation: cleanMathText(s.explanation),
  }));

  const proofText = cleanMathText(
    derivation?.proof || (explanation && explanation.length > 1 ? explanation[1] : null)
  );
  const aliases = (derivation?.alternative_names || []).map((a) => ({
    name: cleanMathText(a.name),
    description: cleanMathText(a.description),
  }));
  const historical = cleanMathText(derivation?.historical_context || "");
  const combinatorial = cleanMathText(derivation?.combinatorial_meaning || "");
  const primaryName = cleanMathText(derivation?.primary_name || patternName || "Mathematical Sequence");

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      style={{
        background: "white",
        borderRadius: "24px",
        padding: "32px",
        border: "1px solid #e6faf7",
        boxShadow: "0 8px 30px rgba(13,148,136,0.06)",
      }}
    >
      {/* Header Section */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "16px",
          marginBottom: "24px",
          paddingBottom: "20px",
          borderBottom: "1px solid #f1f5f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              background: "linear-gradient(135deg, #0d9488, #0891b2)",
              borderRadius: "14px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 4px 14px rgba(13,148,136,0.25)",
              color: "white",
              fontSize: "22px",
            }}
          >
            ✦
          </div>
          <div>
            <h3 style={{ fontSize: "19px", fontWeight: "800", color: "#0f2027", margin: 0 }}>
              Deep Mathematical Derivation & Proof
            </h3>
            <p style={{ fontSize: "13px", color: "#64748b", margin: "3px 0 0" }}>
              Exact step-by-step breakdown for <span style={{ color: "#0d9488", fontWeight: "700" }}>{primaryName}</span>
            </p>
          </div>
        </div>

        {/* Tab Navigation Pill */}
        <div
          style={{
            display: "flex",
            background: "#f1f5f9",
            borderRadius: "12px",
            padding: "4px",
            gap: "4px",
          }}
        >
          <button
            onClick={() => setActiveTab("derivation")}
            style={{
              background: activeTab === "derivation" ? "white" : "transparent",
              color: activeTab === "derivation" ? "#0d9488" : "#64748b",
              border: "none",
              borderRadius: "9px",
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: activeTab === "derivation" ? "700" : "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: activeTab === "derivation" ? "0 2px 8px rgba(0,0,0,0.06)" : "none",
            }}
          >
            🧮 Step-by-Step Solution
          </button>

          <button
            onClick={() => setActiveTab("proof")}
            style={{
              background: activeTab === "proof" ? "white" : "transparent",
              color: activeTab === "proof" ? "#0d9488" : "#64748b",
              border: "none",
              borderRadius: "9px",
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: activeTab === "proof" ? "700" : "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: activeTab === "proof" ? "0 2px 8px rgba(0,0,0,0.06)" : "none",
            }}
          >
            📜 Formal Proof
          </button>

          <button
            onClick={() => setActiveTab("aliases")}
            style={{
              background: activeTab === "aliases" ? "white" : "transparent",
              color: activeTab === "aliases" ? "#0d9488" : "#64748b",
              border: "none",
              borderRadius: "9px",
              padding: "8px 16px",
              fontSize: "13px",
              fontWeight: activeTab === "aliases" ? "700" : "600",
              cursor: "pointer",
              transition: "all 0.2s ease",
              boxShadow: activeTab === "aliases" ? "0 2px 8px rgba(0,0,0,0.06)" : "none",
            }}
          >
            🏷️ Alternative Names ({aliases.length > 0 ? aliases.length : "Identities"})
          </button>
        </div>
      </div>

      {/* Tab Content Panels */}
      <AnimatePresence mode="wait">
        {/* TAB 1: STEP-BY-STEP DERIVATION */}
        {activeTab === "derivation" && (
          <motion.div
            key="derivation"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            style={{ display: "flex", flexDirection: "column", gap: "14px" }}
          >
            {steps.map((step, i) => (
              <div
                key={i}
                style={{
                  background: "#f8fafc",
                  borderRadius: "16px",
                  padding: "18px 22px",
                  border: "1px solid #f1f5f9",
                  borderLeft: "4px solid #0d9488",
                  transition: "transform 0.2s ease, box-shadow 0.2s ease",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
                  <span
                    style={{
                      background: "linear-gradient(135deg, #0d9488, #0891b2)",
                      color: "white",
                      fontSize: "11px",
                      fontWeight: "800",
                      padding: "3px 9px",
                      borderRadius: "6px",
                    }}
                  >
                    STEP {step.step_number || i + 1}
                  </span>
                  <h4 style={{ fontSize: "14px", fontWeight: "700", color: "#0f2027", margin: 0 }}>
                    {step.title || `Calculation Phase ${i + 1}`}
                  </h4>
                </div>
                <div
                  style={{
                    fontSize: "14px",
                    color: "#334155",
                    lineHeight: 1.7,
                    whiteSpace: "pre-line",
                    fontFamily: "inherit",
                  }}
                >
                  {step.explanation}
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* TAB 2: FORMAL MATHEMATICAL PROOF */}
        {activeTab === "proof" && (
          <motion.div
            key="proof"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            style={{ display: "flex", flexDirection: "column", gap: "16px" }}
          >
            <div
              style={{
                background: "linear-gradient(135deg, #f0fdf4, #e6faf7)",
                borderRadius: "16px",
                padding: "24px",
                border: "1px solid rgba(13,148,136,0.2)",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "14px" }}>
                <span style={{ fontSize: "20px" }}>🛡️</span>
                <h4 style={{ fontSize: "16px", fontWeight: "800", color: "#065f46", margin: 0 }}>
                  Classification Proof & Theoretical Invariance
                </h4>
              </div>
              <div
                style={{
                  fontSize: "14px",
                  color: "#1e293b",
                  lineHeight: 1.8,
                  whiteSpace: "pre-line",
                }}
              >
                {proofText || "The sequence strictly obeys the characteristic mathematical relations of this family."}
              </div>
            </div>

            {combinatorial && (
              <div
                style={{
                  background: "#f8fafc",
                  borderRadius: "14px",
                  padding: "18px 20px",
                  border: "1px solid #e2e8f0",
                }}
              >
                <h5 style={{ fontSize: "13px", fontWeight: "700", color: "#0f2027", margin: "0 0 6px" }}>
                  💡 Combinatorial Meaning & Nature:
                </h5>
                <p style={{ fontSize: "13px", color: "#475569", margin: 0, lineHeight: 1.6 }}>
                  {combinatorial}
                </p>
              </div>
            )}
          </motion.div>
        )}

        {/* TAB 3: ALTERNATIVE NAMES & IDENTITIES */}
        {activeTab === "aliases" && (
          <motion.div
            key="aliases"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            style={{ display: "flex", flexDirection: "column", gap: "18px" }}
          >
            {aliases.length > 0 ? (
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "12px" }}>
                {aliases.map((alias, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: "#f8fafc",
                      borderRadius: "14px",
                      padding: "16px 20px",
                      border: "1px solid #f1f5f9",
                      display: "flex",
                      flexDirection: "column",
                      gap: "4px",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                      <span
                        style={{
                          background: "#ccfbf1",
                          color: "#0f766e",
                          fontSize: "11px",
                          fontWeight: "800",
                          padding: "2px 8px",
                          borderRadius: "6px",
                        }}
                      >
                        Alias #{idx + 1}
                      </span>
                      <h4 style={{ fontSize: "15px", fontWeight: "700", color: "#0f2027", margin: 0 }}>
                        {alias.name}
                      </h4>
                    </div>
                    <p style={{ fontSize: "13px", color: "#475569", margin: "4px 0 0", lineHeight: 1.6 }}>
                      {alias.description}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: "14px", color: "#64748b", margin: 0 }}>
                This sequence is primarily recognized under standard canonical nomenclature.
              </p>
            )}

            {historical && (
              <div
                style={{
                  background: "linear-gradient(135deg, #fffbeb, #fef3c7)",
                  borderRadius: "14px",
                  padding: "18px 20px",
                  border: "1px solid rgba(245,158,11,0.25)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                  <span style={{ fontSize: "16px" }}>🏛️</span>
                  <h5 style={{ fontSize: "13px", fontWeight: "800", color: "#92400e", margin: 0 }}>
                    Historical Origin & Discovery
                  </h5>
                </div>
                <p style={{ fontSize: "13px", color: "#78350f", margin: 0, lineHeight: 1.6 }}>
                  {historical}
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ExplanationCard;