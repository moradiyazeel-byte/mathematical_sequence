import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';

const LoginPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await loginUser(email, password);
      if (res.success && res.data?.token) {
        localStorage.setItem('patternai_token', res.data.token);
        localStorage.setItem('patternai_user', JSON.stringify(res.data.user || {}));
        navigate('/dashboard');
      } else {
        setError(res.error || 'Login failed');
      }
    } catch (err) {
      setError(err.message || 'Invalid credentials or server error');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%', background: '#f8fafc', border: '2px solid #e2e8f0',
    borderRadius: '12px', padding: '16px 18px', fontSize: '17px',
    color: '#0f172a', outline: 'none', fontFamily: 'inherit',
    boxSizing: 'border-box', transition: 'all 0.2s'
  };

  const symbols = [
    { s: '∑', x: '10%', y: '10%', d: 0 },
    { s: 'π', x: '80%', y: '15%', d: 0.5 },
    { s: '∞', x: '15%', y: '60%', d: 1 },
    { s: '√', x: '75%', y: '55%', d: 1.5 },
    { s: '∫', x: '20%', y: '80%', d: 0.8 },
    { s: 'Δ', x: '70%', y: '75%', d: 1.2 },
    { s: 'θ', x: '45%', y: '20%', d: 0.3 },
    { s: 'λ', x: '50%', y: '70%', d: 1.8 },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', overflow: 'hidden' }}>

      {/* Left — 3D Dark Panel */}
      <div style={{ flex: 1, background: 'linear-gradient(160deg, #e6faf7 0%, #b2f0e8 35%, #5eead4 65%, #14b8a6 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>

        {/* Grid */}
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(20,184,166,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(20,184,166,0.1) 1px, transparent 1px)', backgroundSize: '50px 50px', transform: 'perspective(500px) rotateX(30deg)', transformOrigin: 'top' }}></div>

        {/* Glow Orbs */}
        <div style={{ position: 'absolute', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%)', borderRadius: '50%', top: '20%', left: '20%', filter: 'blur(40px)' }}></div>
        <div style={{ position: 'absolute', width: '200px', height: '200px', background: 'radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%)', borderRadius: '50%', bottom: '20%', right: '20%', filter: 'blur(30px)' }}></div>

        {/* Floating Symbols */}
        {symbols.map((item, i) => (
          <motion.div key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.2, 0.7, 0.2], y: [0, -20, 0] }}
            transition={{ duration: 3 + i * 0.5, delay: item.d, repeat: Infinity }}
            style={{ position: 'absolute', left: item.x, top: item.y, fontSize: '28px', fontWeight: '800', color: 'rgba(0,0,0,0.2)', userSelect: 'none', textShadow: '0 0 20px rgba(255,255,255,0.8)' }}>
            {item.s}
          </motion.div>
        ))}

        {/* 3D Rotating Cube */}
        <motion.div
          animate={{ rotateY: 360, rotateX: 15 }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          style={{ width: '180px', height: '180px', position: 'relative', transformStyle: 'preserve-3d', marginBottom: '48px' }}>
          {[
            { transform: 'translateZ(90px)', bg: 'rgba(13,148,136,0.3)', border: '2px solid rgba(13,148,136,0.6)', content: '∑' },
            { transform: 'translateZ(-90px) rotateY(180deg)', bg: 'rgba(20,184,166,0.3)', border: '2px solid rgba(20,184,166,0.6)', content: '√' },
            { transform: 'rotateY(90deg) translateZ(90px)', bg: 'rgba(45,212,191,0.3)', border: '2px solid rgba(45,212,191,0.6)', content: 'π' },
            { transform: 'rotateY(-90deg) translateZ(90px)', bg: 'rgba(13,148,136,0.3)', border: '2px solid rgba(13,148,136,0.6)', content: '∞' },
            { transform: 'rotateX(90deg) translateZ(90px)', bg: 'rgba(20,184,166,0.2)', border: '2px solid rgba(20,184,166,0.4)', content: 'f(x)' },
            { transform: 'rotateX(-90deg) translateZ(90px)', bg: 'rgba(13,148,136,0.2)', border: '2px solid rgba(13,148,136,0.4)', content: 'n²' },
          ].map((face, i) => (
            <div key={i} style={{ position: 'absolute', width: '180px', height: '180px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px', fontWeight: '900', color: 'white', background: face.bg, border: face.border, borderRadius: '12px', backdropFilter: 'blur(10px)', transform: face.transform }}>
              {face.content}
            </div>
          ))}
        </motion.div>

        {/* Text */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          style={{ textAlign: 'center', padding: '0 48px', position: 'relative', zIndex: 10 }}>
          <h2 style={{ color: '#0f172a', fontSize: '28px', fontWeight: '800', marginBottom: '12px' }}>Discover Math Patterns</h2>
          <p style={{ color: '#1e293b', fontSize: '15px', lineHeight: '1.7' }}>Detect hidden mathematical relationships in any sequence</p>
        </motion.div>

        {/* Stats */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}
          style={{ display: 'flex', gap: '32px', marginTop: '40px', position: 'relative', zIndex: 10 }}>
          {[{ n: '20+', l: 'Patterns' }, { n: '100%', l: 'Accuracy' }, { n: '<1s', l: 'Speed' }].map((s, i) => (
            <div key={i} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: '800', color: '#0d9488' }}>{s.n}</div>
              <div style={{ fontSize: '12px', color: '#1e293b', marginTop: '2px', fontWeight: '600' }}>{s.l}</div>
            </div>
          ))}
        </motion.div>

      </div>

      {/* Right — Form */}
      <div style={{ width: '780px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px', background: '#ffffff' }}>
        <div style={{ width: '100%', maxWidth: '460px' }}>

          {/* Logo */}
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: '48px' }}>
            <Link to="/" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #0d9488, #0891b2)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ color: 'white', fontWeight: '800', fontSize: '18px' }}>P</span>
              </div>
              <span style={{ fontWeight: '800', fontSize: '22px', color: '#0f172a' }}>
                Pattern<span style={{ background: 'linear-gradient(135deg, #0d9488, #0891b2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI</span>
              </span>
            </Link>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>

            <h1 style={{ fontSize: '38px', fontWeight: '900', color: '#0f172a', marginBottom: '10px', letterSpacing: '-1px' }}>Welcome back</h1>
            <p style={{ color: '#64748b', fontSize: '17px', marginBottom: '40px' }}>Sign in to your PatternAI account</p>

            {error && (
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px', padding: '14px 18px', marginBottom: '24px', color: '#dc2626', fontSize: '14px', fontWeight: '600' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleLogin} autoComplete="off">

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '10px' }}>Email address</label>
                <input type="email" name={`email_${Math.random()}`} autoComplete="new-password" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com" required style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = '#0d9488'; e.target.style.boxShadow = '0 0 0 4px rgba(20,184,166,0.1)'; e.target.style.background = '#fff'; }}
                  onBlur={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f8fafc'; }} />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '10px' }}>Password</label>
                <input type="password" name={`pwd_${Math.random()}`} autoComplete="new-password" value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password" required style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = '#0d9488'; e.target.style.boxShadow = '0 0 0 4px rgba(20,184,166,0.1)'; e.target.style.background = '#fff'; }}
                  onBlur={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f8fafc'; }} />
              </div>

              <div style={{ textAlign: 'right', marginBottom: '32px' }}>
                <a href="#" style={{ color: '#0d9488', fontSize: '15px', fontWeight: '600', textDecoration: 'none' }}>Forgot password?</a>
              </div>

              <button type="submit" disabled={loading}
                style={{ width: '100%', background: 'linear-gradient(135deg, #0d9488, #0891b2)', color: 'white', border: 'none', padding: '18px', borderRadius: '14px', fontSize: '18px', fontWeight: '700', cursor: 'pointer', fontFamily: 'inherit', boxShadow: '0 8px 25px rgba(20,184,166,0.3)', marginBottom: '28px', letterSpacing: '0.3px' }}>
                {loading ? 'Signing in...' : 'Sign In'}
              </button>

            </form>



            <p style={{ textAlign: 'center', color: '#64748b', fontSize: '16px' }}>
              Don't have an account?{' '}
              <Link to="/signup" style={{ color: '#0d9488', fontWeight: '700', textDecoration: 'none' }}>Sign up free</Link>
            </p>

          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;