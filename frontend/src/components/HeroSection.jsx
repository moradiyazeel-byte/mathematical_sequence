import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";

const TypeWriter = ({ texts }) => {
  const [displayed, setDisplayed] = useState("");
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);
  useEffect(() => {
    const current = texts[textIndex];
    const timeout = setTimeout(() => {
      if (!deleting) {
        setDisplayed(current.slice(0, charIndex + 1));
        if (charIndex + 1 === current.length) setTimeout(() => setDeleting(true), 1800);
        else setCharIndex(c => c + 1);
      } else {
        setDisplayed(current.slice(0, charIndex - 1));
        if (charIndex - 1 === 0) { setDeleting(false); setTextIndex(t => (t + 1) % texts.length); setCharIndex(0); }
        else setCharIndex(c => c - 1);
      }
    }, deleting ? 35 : 75);
    return () => clearTimeout(timeout);
  }, [charIndex, deleting, textIndex, texts]);
  return (
    <span style={{ color: "#0d9488" }}>
      {displayed}
      <motion.span animate={{ opacity: [1, 0] }} transition={{ duration: 0.5, repeat: Infinity }} style={{ color: "#0d9488" }}>|</motion.span>
    </span>
  );
};

// Auto-changing sequence demo data
const DEMO_SEQUENCES = [
  {
    label: "Arithmetic Progression",
    sequence: "1, 3, 5, 7, 9, 11, 13...",
    pattern: "Arithmetic",
    patternFull: "Progression",
    confidence: "100%",
    confidenceLabel: "Excellent Match",
    formula: "a(n) = 1 + (n-1) x 2",
    bars: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19],
    color: "#0d9488",
    bgColor: "#e6faf7",
  },
  {
    label: "Fibonacci Sequence",
    sequence: "1, 1, 2, 3, 5, 8, 13...",
    pattern: "Fibonacci",
    patternFull: "Sequence",
    confidence: "100%",
    confidenceLabel: "Excellent Match",
    formula: "a(n) = a(n-1) + a(n-2)",
    bars: [1, 1, 2, 3, 5, 8, 13, 21, 34, 55],
    color: "#0891b2",
    bgColor: "#e0f2fe",
  },
  {
    label: "Square Numbers",
    sequence: "1, 4, 9, 16, 25, 36...",
    pattern: "Square",
    patternFull: "Numbers",
    confidence: "100%",
    confidenceLabel: "Excellent Match",
    formula: "a(n) = n²",
    bars: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100],
    color: "#7c3aed",
    bgColor: "#ede9fe",
  },
  {
    label: "Geometric Progression",
    sequence: "2, 4, 8, 16, 32, 64...",
    pattern: "Geometric",
    patternFull: "Progression",
    confidence: "100%",
    confidenceLabel: "Excellent Match",
    formula: "a(n) = 2 x 2^(n-1)",
    bars: [2, 4, 8, 16, 32, 48, 64, 80, 96, 128],
    color: "#d97706",
    bgColor: "#fef3c7",
  },
  {
    label: "Prime Numbers",
    sequence: "2, 3, 5, 7, 11, 13, 17...",
    pattern: "Prime",
    patternFull: "Numbers",
    confidence: "100%",
    confidenceLabel: "Excellent Match",
    formula: "a(n) = nth prime number",
    bars: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
    color: "#dc2626",
    bgColor: "#fee2e2",
  },
];

const DemoCard = () => {
  const [current, setCurrent] = useState(0);
  const [prev, setPrev] = useState(null);
  const [direction, setDirection] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setPrev(current);
      setDirection(1);
      setCurrent(c => (c + 1) % DEMO_SEQUENCES.length);
    }, 3500);
    return () => clearInterval(interval);
  }, [current]);

  const demo = DEMO_SEQUENCES[current];
  const maxBar = Math.max(...demo.bars);

  return (
    <motion.div
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      style={{ background: "rgba(255,255,255,0.92)", borderRadius: "24px", padding: "28px", boxShadow: "0 24px 80px rgba(13,148,136,0.2), 0 4px 20px rgba(0,0,0,0.08)", backdropFilter: "blur(20px)", border: "1px solid rgba(255,255,255,0.95)", overflow: "hidden", position: "relative" }}>

      {/* Subtle background accent */}
      <motion.div
        key={current + "bg"}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{ position: "absolute", top: 0, right: 0, width: "200px", height: "200px", background: `radial-gradient(circle, ${demo.color}08, transparent)`, borderRadius: "50%", zIndex: 0 }} />

      {/* Browser Bar */}
      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "20px", paddingBottom: "16px", borderBottom: "1px solid #f1f5f9", position: "relative", zIndex: 1 }}>
        <div style={{ width: "11px", height: "11px", borderRadius: "50%", background: "#ff5f57" }} />
        <div style={{ width: "11px", height: "11px", borderRadius: "50%", background: "#febc2e" }} />
        <div style={{ width: "11px", height: "11px", borderRadius: "50%", background: "#28c840" }} />
        <div style={{ flex: 1, background: "#f8fafc", borderRadius: "6px", padding: "5px 12px", marginLeft: "10px" }}>
          <span style={{ fontSize: "11px", color: "#94a3b8" }}>patternai.app — Analysis</span>
        </div>
        {/* Sequence indicator dots */}
        <div style={{ display: "flex", gap: "4px", marginLeft: "8px" }}>
          {DEMO_SEQUENCES.map((_, i) => (
            <motion.div key={i}
              animate={{ width: i === current ? "16px" : "6px", background: i === current ? demo.color : "#e2e8f0" }}
              transition={{ duration: 0.3 }}
              style={{ height: "6px", borderRadius: "3px" }} />
          ))}
        </div>
      </div>      {/* Content with AnimatePresence for smooth transition */}
      <AnimatePresence mode="wait">
        <motion.div key={current} style={{ position: "relative", zIndex: 1 }}
          initial={{ opacity: 0, y: 20, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.98 }}
          transition={{ duration: 0.4, ease: "easeInOut" }}>

          {/* Sequence Input */}
          <div style={{ background: "#f8fafc", borderRadius: "10px", padding: "12px 16px", marginBottom: "14px", border: `2px solid ${demo.color}20` }}>
            <p style={{ fontSize: "10px", color: demo.color, margin: "0 0 3px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.8px" }}>Sequence Input</p>
            <p style={{ fontSize: "15px", fontFamily: "monospace", color: "#0f2027", margin: 0, fontWeight: "700" }}>{demo.sequence}</p>
          </div>

          {/* Pattern + Confidence */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "14px" }}>
            <div style={{ background: `linear-gradient(135deg, ${demo.bgColor}, white)`, borderRadius: "12px", padding: "14px", border: `1px solid ${demo.color}20` }}>
              <p style={{ fontSize: "10px", color: demo.color, fontWeight: "700", margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Pattern</p>
              <p style={{ fontSize: "16px", fontWeight: "800", color: "#0f2027", margin: 0 }}>{demo.pattern}</p>
              <p style={{ fontSize: "11px", color: demo.color, margin: "2px 0 0", fontWeight: "600" }}>{demo.patternFull}</p>
            </div>
            <div style={{ background: "linear-gradient(135deg, #f0fdf4, #dcfce7)", borderRadius: "12px", padding: "14px", border: "1px solid rgba(22,163,74,0.15)" }}>
              <p style={{ fontSize: "10px", color: "#16a34a", fontWeight: "700", margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Confidence</p>
              <p style={{ fontSize: "22px", fontWeight: "900", color: "#16a34a", margin: 0, lineHeight: 1 }}>{demo.confidence}</p>
              <p style={{ fontSize: "11px", color: "#16a34a", margin: "2px 0 0", fontWeight: "600" }}>{demo.confidenceLabel}</p>
            </div>
          </div>

          {/* Formula */}
          <div style={{ background: `linear-gradient(135deg, ${demo.color}, ${demo.color}cc)`, borderRadius: "12px", padding: "14px 18px", marginBottom: "14px" }}>
            <p style={{ fontSize: "10px", color: "rgba(255,255,255,0.7)", fontWeight: "700", margin: "0 0 4px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Formula</p>
            <p style={{ fontSize: "17px", fontFamily: "monospace", color: "white", margin: 0, fontWeight: "800" }}>{demo.formula}</p>
          </div>

          {/* Graph Bars */}
          <div>
            <p style={{ fontSize: "10px", color: "#94a3b8", fontWeight: "600", margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "0.5px" }}>Pattern Graph + Predictions</p>
            <div style={{ display: "flex", gap: "4px", alignItems: "flex-end", height: "56px" }}>
              {demo.bars.map((val, i) => (
                <motion.div key={i}
                  initial={{ height: 0 }}
                  animate={{ height: `${(val / maxBar) * 100}%` }}
                  transition={{ delay: i * 0.04, duration: 0.4, ease: "easeOut" }}
                  style={{ flex: 1, background: i < 6 ? `linear-gradient(180deg, ${demo.color}, ${demo.color}99)` : `linear-gradient(180deg, ${demo.bgColor}, white)`, borderRadius: "3px 3px 0 0", border: i >= 6 ? `1px dashed ${demo.color}50` : "none", boxSizing: "border-box" }} />
              ))}
            </div>
            <div style={{ display: "flex", gap: "4px", marginTop: "4px" }}>
              {demo.bars.map((_, i) => (
                <div key={i} style={{ flex: 1, textAlign: "center", fontSize: "8px", color: "#cbd5e1", fontWeight: "600" }}>{i + 1}</div>
              ))}
            </div>
          </div>

          {/* Pattern Label */}
          <div style={{ marginTop: "12px", display: "flex", justifyContent: "center" }}>
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.3 }}
              style={{ background: `${demo.color}15`, border: `1px solid ${demo.color}30`, borderRadius: "100px", padding: "4px 14px", display: "inline-flex", alignItems: "center", gap: "6px" }}>
              <div style={{ width: "6px", height: "6px", borderRadius: "50%", background: demo.color }} />
              <span style={{ fontSize: "11px", fontWeight: "700", color: demo.color }}>{demo.label}</span>
            </motion.div>
          </div>

        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
};

const features = [
  { icon: "\u03a3", title: "Pattern Detection", desc: "Detects 20+ mathematical patterns with 100% accuracy in milliseconds", color: "#0d9488" },
  { icon: "f(x)", title: "Formula Generation", desc: "Auto-generates the exact mathematical formula for your sequence", color: "#0891b2" },
  { icon: "\u2192", title: "Future Prediction", desc: "Predicts next 5+ values using the detected pattern algorithm", color: "#0d9488" },
  { icon: "\ud83d\udcca", title: "Visual Graphs", desc: "Beautiful interactive charts showing actual vs predicted values", color: "#0891b2" },
  { icon: "\u2726", title: "AI Explanation", desc: "Step-by-step human-readable explanation of how pattern was found", color: "#0d9488" },
  { icon: "%", title: "Confidence Score", desc: "Accuracy rating from 0-100% for every single detection", color: "#0891b2" },
];

const steps = [
  { n: "01", title: "Enter Sequence", desc: "Type any numbers separated by commas. Works with any numerical sequence!", color: "#0d9488" },
  { n: "02", title: "AI Analyzes", desc: "Our AI runs 20+ detection algorithms simultaneously in under 1 second.", color: "#0891b2" },
  { n: "03", title: "Get Results", desc: "See detected pattern, formula, graph, predictions and full explanation.", color: "#0d9488" },
];

const HeroSection = () => {
  const [demoModalOpen, setDemoModalOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setDemoModalOpen(false);
    };
    if (demoModalOpen) window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [demoModalOpen]);

  return (
    <>
      <AnimatePresence>
        {demoModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ position: 'fixed', inset: 0, zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(15, 32, 39, 0.8)', backdropFilter: 'blur(8px)', padding: '24px' }}
            onClick={() => setDemoModalOpen(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              style={{ position: 'relative', width: '100%', maxWidth: '700px' }}
              onClick={e => e.stopPropagation()}
            >
              <button 
                onClick={() => setDemoModalOpen(false)}
                style={{ position: 'absolute', top: '-40px', right: 0, color: 'white', background: 'transparent', border: 'none', fontSize: '15px', fontWeight: '600', cursor: 'pointer', padding: '8px' }}
              >
                Close (ESC)
              </button>
              <DemoCard />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* HERO */}
      <section style={{ minHeight: "100vh", paddingTop: "70px", position: "relative", overflow: "hidden", background: "linear-gradient(160deg, #e6faf7 0%, #b2f0e8 35%, #5eead4 65%, #14b8a6 100%)" }}>

        {/* Organic Blobs */}
        <div style={{ position: "absolute", inset: 0, zIndex: 0, overflow: "hidden" }}>
          <div className="blob1" style={{ position: "absolute", width: "650px", height: "650px", borderRadius: "60% 40% 70% 30% / 50% 60% 40% 50%", background: "rgba(255,255,255,0.35)", top: "-200px", right: "-150px", filter: "blur(2px)" }} />
          <div className="blob2" style={{ position: "absolute", width: "450px", height: "450px", borderRadius: "40% 60% 30% 70% / 60% 40% 70% 30%", background: "rgba(255,255,255,0.25)", bottom: "-100px", left: "-100px", filter: "blur(1px)" }} />
          <div className="blob3" style={{ position: "absolute", width: "300px", height: "300px", borderRadius: "50% 50% 30% 70% / 40% 60% 40% 60%", background: "rgba(255,255,255,0.2)", top: "30%", left: "30%", filter: "blur(1px)" }} />
          <div style={{ position: "absolute", width: "120px", height: "120px", borderRadius: "50%", background: "rgba(255,255,255,0.4)", top: "15%", right: "25%", filter: "blur(8px)" }} />
          <div style={{ position: "absolute", width: "80px", height: "80px", borderRadius: "50%", background: "rgba(255,255,255,0.35)", bottom: "20%", right: "15%", filter: "blur(6px)" }} />
        </div>

        {/* Content */}
        <div style={{ maxWidth: "1280px", margin: "0 auto", padding: "80px 40px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "60px", alignItems: "center", position: "relative", zIndex: 1, minHeight: "calc(100vh - 70px)" }}>

          {/* Left */}
          <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
              style={{ display: "inline-flex", alignItems: "center", gap: "8px", background: "rgba(255,255,255,0.7)", border: "1px solid rgba(13,148,136,0.25)", borderRadius: "100px", padding: "7px 18px", marginBottom: "28px", backdropFilter: "blur(10px)" }}>
              <motion.div animate={{ scale: [1, 1.5, 1] }} transition={{ duration: 2, repeat: Infinity }}
                style={{ width: "7px", height: "7px", background: "#0d9488", borderRadius: "50%" }} />
              <span style={{ color: "#0d9488", fontSize: "14px", fontWeight: "700" }}>AI-Powered Pattern Discovery</span>
            </motion.div>

            <motion.h1 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
              style={{ fontSize: "58px", fontWeight: "900", color: "#0f2027", lineHeight: 1.1, marginBottom: "24px", letterSpacing: "-2px" }}>
              Discover Patterns
              <br />
              <TypeWriter texts={["with Clarity!", "with Precision.", "with Confidence!", "Instantly."]} />
              <br />
              <span style={{ fontSize: "48px" }}>and Control</span>
            </motion.h1>

            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
              style={{ fontSize: "18px", color: "rgba(15,32,39,0.65)", lineHeight: 1.8, marginBottom: "40px", maxWidth: "480px" }}>
              A powerful, intuitive platform for mathematical pattern analysis. Enter any sequence and get instant AI-powered insights.
            </motion.p>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }}
              style={{ display: "flex", gap: "16px", marginBottom: "48px" }}>
              <motion.div whileHover={{ scale: 1.04, y: -2 }} whileTap={{ scale: 0.97 }}>
                <Link to="/analyze"
                  style={{ background: "linear-gradient(135deg, #0d9488, #0891b2)", color: "white", padding: "16px 36px", borderRadius: "12px", fontSize: "16px", fontWeight: "800", textDecoration: "none", boxShadow: "0 6px 25px rgba(13,148,136,0.4)", display: "inline-block" }}>
                  Get Started Free
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.04, y: -2 }} whileTap={{ scale: 0.97 }}>
                <button onClick={() => setDemoModalOpen(true)}
                  style={{ background: "rgba(255,255,255,0.75)", color: "#0f2027", padding: "16px 36px", borderRadius: "12px", fontSize: "16px", fontWeight: "700", border: "1.5px solid rgba(13,148,136,0.2)", display: "inline-block", backdropFilter: "blur(10px)", cursor: "pointer", outline: "none" }}>
                  See a Demo
                </button>
              </motion.div>
            </motion.div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
              style={{ display: "flex", gap: "40px" }}>
              {[{ n: "20+", l: "Pattern Types" }, { n: "100%", l: "Accuracy" }, { n: "<1s", l: "Analysis Time" }].map((s, i) => (
                <div key={i}>
                  <div style={{ fontSize: "30px", fontWeight: "900", color: "#0d9488", letterSpacing: "-1px" }}>{s.n}</div>
                  <div style={{ fontSize: "13px", color: "rgba(15,32,39,0.5)", fontWeight: "600", marginTop: "2px" }}>{s.l}</div>
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right — Auto-changing Demo Card */}
          <motion.div initial={{ opacity: 0, x: 60, y: 20 }} animate={{ opacity: 1, x: 0, y: 0 }} transition={{ duration: 0.8, delay: 0.3 }}>
            <DemoCard />
          </motion.div>

        </div>

        {/* Wave */}
        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, zIndex: 1 }}>
          <svg viewBox="0 0 1440 80" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ display: "block" }}>
            <path d="M0 80L60 74.7C120 69.3 240 58.7 360 53.3C480 48 600 48 720 53.3C840 58.7 960 69.3 1080 69.3C1200 69.3 1320 58.7 1380 53.3L1440 48V80H1380C1320 80 1200 80 1080 80C960 80 840 80 720 80C600 80 480 80 360 80C240 80 120 80 60 80H0Z" fill="white"/>
          </svg>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" style={{ padding: "100px 40px", background: "white" }}>
        <div style={{ maxWidth: "1280px", margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: "72px" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", background: "#e6faf7", border: "1px solid rgba(13,148,136,0.2)", borderRadius: "100px", padding: "6px 18px", marginBottom: "18px" }}>
              <span style={{ color: "#0d9488", fontSize: "13px", fontWeight: "700" }}>Powerful Features</span>
            </div>
            <h2 style={{ fontSize: "48px", fontWeight: "900", color: "#0f2027", marginBottom: "16px", letterSpacing: "-1.5px" }}>
              Everything You Need to
              <br />
              <span style={{ color: "#0d9488" }}>Understand Any Sequence</span>
            </h2>
            <p style={{ fontSize: "18px", color: "#64748b", maxWidth: "540px", margin: "0 auto", lineHeight: 1.7 }}>
              All the tools to analyze, understand and predict mathematical sequences completely free
            </p>
          </motion.div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "24px" }}>
            {features.map((f, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.08 }}
                whileHover={{ y: -8, boxShadow: "0 20px 50px rgba(13,148,136,0.12)" }}
                style={{ background: "white", borderRadius: "20px", padding: "32px", border: "1px solid #e6faf7", boxShadow: "0 2px 12px rgba(13,148,136,0.06)", transition: "all 0.3s", cursor: "default" }}>
                <div style={{ width: "52px", height: "52px", background: i % 2 === 0 ? "linear-gradient(135deg, #e6faf7, #ccfbf1)" : "linear-gradient(135deg, #e0f2fe, #bae6fd)", borderRadius: "14px", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "20px", border: "1px solid rgba(13,148,136,0.12)" }}>
                  <span style={{ color: f.color, fontSize: "22px", fontWeight: "900" }}>{f.icon}</span>
                </div>
                <h3 style={{ fontSize: "18px", fontWeight: "700", color: "#0f2027", marginBottom: "10px" }}>{f.title}</h3>
                <p style={{ fontSize: "14px", color: "#64748b", lineHeight: 1.7, margin: 0 }}>{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="howitworks" style={{ padding: "100px 40px", position: "relative", overflow: "hidden", background: "linear-gradient(160deg, #e6faf7 0%, #b2f0e8 40%, #5eead4 80%, #14b8a6 100%)" }}>
        <div style={{ position: "absolute", inset: 0, zIndex: 0, overflow: "hidden" }}>
          <div className="blob1" style={{ position: "absolute", width: "500px", height: "500px", borderRadius: "60% 40% 70% 30% / 50% 60% 40% 50%", background: "rgba(255,255,255,0.3)", top: "-150px", right: "-100px" }} />
          <div className="blob2" style={{ position: "absolute", width: "350px", height: "350px", borderRadius: "40% 60% 30% 70% / 60% 40% 70% 30%", background: "rgba(255,255,255,0.2)", bottom: "-80px", left: "-80px" }} />
        </div>
        <div style={{ maxWidth: "1280px", margin: "0 auto", position: "relative", zIndex: 1 }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: "72px" }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", background: "rgba(255,255,255,0.7)", border: "1px solid rgba(13,148,136,0.2)", borderRadius: "100px", padding: "6px 18px", marginBottom: "18px", backdropFilter: "blur(10px)" }}>
              <span style={{ color: "#0d9488", fontSize: "13px", fontWeight: "700" }}>Simple Process</span>
            </div>
            <h2 style={{ fontSize: "48px", fontWeight: "900", color: "#0f2027", marginBottom: "16px", letterSpacing: "-1.5px" }}>
              3 Steps to Discover
              <br />
              <span style={{ color: "#0d9488" }}>Any Hidden Pattern</span>
            </h2>
            <p style={{ fontSize: "18px", color: "rgba(15,32,39,0.6)", maxWidth: "450px", margin: "0 auto", lineHeight: 1.7 }}>
              Seriously. Just type numbers and let the AI magic happen in seconds.
            </p>
          </motion.div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "32px", marginBottom: "64px" }}>
            {steps.map((step, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15 }}
                style={{ textAlign: "center", position: "relative" }}>
                {i < 2 && <div style={{ position: "absolute", top: "36px", left: "62%", width: "76%", height: "2px", background: "linear-gradient(90deg, rgba(13,148,136,0.4), transparent)", zIndex: 0 }} />}
                <div style={{ position: "relative", zIndex: 1 }}>
                  <motion.div whileHover={{ scale: 1.1, boxShadow: "0 16px 40px rgba(13,148,136,0.35)" }}
                    style={{ width: "72px", height: "72px", background: "linear-gradient(135deg, #0d9488, #14b8a6)", borderRadius: "20px", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 28px", boxShadow: "0 8px 24px rgba(13,148,136,0.3)", transition: "all 0.3s" }}>
                    <span style={{ color: "white", fontSize: "22px", fontWeight: "900" }}>{step.n}</span>
                  </motion.div>
                  <h3 style={{ fontSize: "22px", fontWeight: "800", color: "#0f2027", marginBottom: "12px" }}>{step.title}</h3>
                  <p style={{ fontSize: "15px", color: "rgba(15,32,39,0.55)", lineHeight: 1.7, maxWidth: "280px", margin: "0 auto" }}>{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center" }}>
            <motion.div whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.97 }}>
              <Link to="/analyze"
                style={{ background: "linear-gradient(135deg, #0d9488, #0891b2)", color: "white", padding: "18px 52px", borderRadius: "14px", fontSize: "17px", fontWeight: "800", textDecoration: "none", boxShadow: "0 8px 30px rgba(13,148,136,0.4)", display: "inline-block" }}>
                Start Analyzing — It is Free!
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: "100px 40px", position: "relative", overflow: "hidden", background: "linear-gradient(135deg, #0d9488 0%, #0891b2 100%)" }}>
        <div style={{ position: "absolute", inset: 0, zIndex: 0 }}>
          <div className="blob1" style={{ position: "absolute", width: "500px", height: "500px", borderRadius: "60% 40% 70% 30% / 50% 60% 40% 50%", background: "rgba(255,255,255,0.1)", top: "-200px", right: "-100px" }} />
          <div className="blob2" style={{ position: "absolute", width: "400px", height: "400px", borderRadius: "40% 60% 30% 70% / 60% 40% 70% 30%", background: "rgba(255,255,255,0.08)", bottom: "-150px", left: "-100px" }} />
        </div>
        <div style={{ maxWidth: "800px", margin: "0 auto", textAlign: "center", position: "relative", zIndex: 1 }}>
          <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            style={{ fontSize: "52px", fontWeight: "900", color: "white", marginBottom: "20px", letterSpacing: "-1.5px" }}>
            Ready to Discover Hidden Patterns?
          </motion.h2>
          <motion.p initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}
            style={{ fontSize: "18px", color: "rgba(255,255,255,0.8)", marginBottom: "40px", lineHeight: 1.7 }}>
            Join thousands of students, researchers and engineers who use PatternAI to unlock mathematical insights instantly.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }}
            style={{ display: "flex", justifyContent: "center", gap: "16px" }}>
            <motion.div whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.97 }}>
              <Link to="/analyze"
                style={{ background: "white", color: "#0d9488", padding: "16px 40px", borderRadius: "12px", fontSize: "17px", fontWeight: "800", textDecoration: "none", boxShadow: "0 8px 30px rgba(0,0,0,0.15)", display: "inline-block" }}>
                Get Started Free
              </Link>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.97 }}>
              <Link to="/signup"
                style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "16px 40px", borderRadius: "12px", fontSize: "17px", fontWeight: "700", textDecoration: "none", border: "1.5px solid rgba(255,255,255,0.3)", display: "inline-block" }}>
                Sign Up Free
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </>
  );
};
export default HeroSection;