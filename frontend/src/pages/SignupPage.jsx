import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../services/api';

const SignupPage = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const username = email.split('@')[0].replace(/[^a-zA-Z0-9_]/g, '') || 'user' + Math.floor(Math.random() * 1000);
      const res = await registerUser(username, email, password, name);
      if (res.success) {
        navigate('/login');
      } else {
        setError(res.error || 'Registration failed');
      }
    } catch (err) {
      setError(err.message || 'Error registering user. Please try again.');
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

  const numbers = [
    { s: '1,1,2,3,5', x: '8%', y: '12%', d: 0 },
    { s: 'a(n)=n²', x: '72%', y: '18%', d: 0.5 },
    { s: '2,4,8,16', x: '12%', y: '65%', d: 1 },
    { s: 'f(x)=x³', x: '68%', y: '60%', d: 1.5 },
    { s: '∑n=n(n+1)/2', x: '25%', y: '82%', d: 0.8 },
    { s: 'GP: r=2', x: '60%', y: '78%', d: 1.2 },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', overflow: 'hidden' }}>

      {/* Left — Form */}
      <div style={{ width: '780px', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '70px', background: '#ffffff' }}>
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

            <h1 style={{ fontSize: '38px', fontWeight: '900', color: '#0f172a', marginBottom: '10px', letterSpacing: '-1px' }}>Create account</h1>
            <p style={{ color: '#64748b', fontSize: '17px', marginBottom: '40px' }}>Start discovering patterns for free today</p>

            {error && (
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px', padding: '14px 18px', marginBottom: '24px', color: '#dc2626', fontSize: '14px', fontWeight: '600' }}>
                {error}
              </div>
            )}

            <form onSubmit={handleSignup} autoComplete="off">

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '10px' }}>Full Name</label>
                <input type="text" name={`name_${Math.random()}`} autoComplete="new-password" value={name} onChange={e => setName(e.target.value)}
                  placeholder="John Doe" required style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = '#0d9488'; e.target.style.boxShadow = '0 0 0 4px rgba(13,148,136,0.1)'; e.target.style.background = '#fff'; }}
                  onBlur={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f8fafc'; }} />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '10px' }}>Email address</label>
                <input type="email" name={`email_${Math.random()}`} autoComplete="new-password" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com" required style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = '#0d9488'; e.target.style.boxShadow = '0 0 0 4px rgba(13,148,136,0.1)'; e.target.style.background = '#fff'; }}
                  onBlur={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f8fafc'; }} />
              </div>

              <div style={{ marginBottom: '32px' }}>
                <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '10px' }}>Password</label>
                <input type="password" name={`pwd_${Math.random()}`} autoComplete="new-password" value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="Min 8 characters" required style={inputStyle}
                  onFocus={e => { e.target.style.borderColor = '#0d9488'; e.target.style.boxShadow = '0 0 0 4px rgba(13,148,136,0.1)'; e.target.style.background = '#fff'; }}
                  onBlur={e => { e.target.style.borderColor = '#e2e8f0'; e.target.style.boxShadow = 'none'; e.target.style.background = '#f8fafc'; }} />
              </div>

              <button type="submit" disabled={loading}
                style={{ width: '100%', background: 'linear-gradient(135deg, #0d9488, #0891b2)', color: 'white', border: 'none', padding: '18px', borderRadius: '14px', fontSize: '18px', fontWeight: '700', cursor: 'pointer', fontFamily: 'inherit', boxShadow: '0 8px 25px rgba(13,148,136,0.3)', marginBottom: '16px', letterSpacing: '0.3px' }}>
                {loading ? 'Creating account...' : 'Create Free Account'}
              </button>

              <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: '13px', marginBottom: '28px' }}>
                By signing up, you agree to our Terms of Service
              </p>

            </form>

            <p style={{ textAlign: 'center', color: '#64748b', fontSize: '16px' }}>
              Already have an account?{' '}
              <Link to="/login" style={{ color: '#0d9488', fontWeight: '700', textDecoration: 'none' }}>Sign in</Link>
            </p>

          </motion.div>
        </div>
      </div>

      {/* Right — 3D Dark Panel */}
      <div style={{ flex: 1, background: 'linear-gradient(160deg, #e6faf7 0%, #b2f0e8 35%, #5eead4 65%, #14b8a6 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative', overflow: 'hidden' }}>

        {/* Grid */}
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(13,148,136,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(13,148,136,0.1) 1px, transparent 1px)', backgroundSize: '50px 50px', transform: 'perspective(500px) rotateX(30deg)', transformOrigin: 'top' }}></div>

        {/* Glow Orbs */}
        <div style={{ position: 'absolute', width: '350px', height: '350px', background: 'radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%)', borderRadius: '50%', top: '10%', right: '10%', filter: 'blur(50px)' }}></div>
        <div style={{ position: 'absolute', width: '250px', height: '250px', background: 'radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%)', borderRadius: '50%', bottom: '15%', left: '15%', filter: 'blur(40px)' }}></div>

        {/* Floating Numbers */}
        {numbers.map((item, i) => (
          <motion.div key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.2, 0.6, 0.2], y: [0, -15, 0] }}
            transition={{ duration: 3 + i * 0.4, delay: item.d, repeat: Infinity }}
            style={{ position: 'absolute', left: item.x, top: item.y, fontSize: '14px', fontWeight: '700', color: 'rgba(0,0,0,0.4)', userSelect: 'none', fontFamily: 'monospace' }}>
            {item.s}
          </motion.div>
        ))}

        {/* 3D Rotating Ring */}
        <motion.div
          animate={{ rotateZ: 360 }}
          transition={{ duration: 10, repeat: Infinity, ease: 'linear' }}
          style={{ width: '220px', height: '220px', border: '3px solid rgba(255,255,255,0.5)', borderRadius: '50%', position: 'relative', marginBottom: '16px', boxShadow: '0 0 40px rgba(255,255,255,0.3), inset 0 0 40px rgba(255,255,255,0.1)' }}>

          {/* Orbiting Ball */}
          <motion.div
            animate={{ rotateZ: -360 }}
            transition={{ duration: 6, repeat: Infinity, ease: 'linear' }}
            style={{ position: 'absolute', top: '-3px', left: '50%', width: '60px', height: '60px', background: 'linear-gradient(135deg, #0d9488, #0891b2)', borderRadius: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(13,148,136,0.8)' }}>
            <span style={{ color: 'white', fontWeight: '900', fontSize: '20px' }}>∑</span>
          </motion.div>

          {/* Inner Ring */}
          <motion.div
            animate={{ rotateZ: -360 }}
            transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
            style={{ position: 'absolute', top: '20px', left: '20px', right: '20px', bottom: '20px', border: '2px solid rgba(255,255,255,0.3)', borderRadius: '50%' }}>
          </motion.div>

          {/* Center */}
          <div style={{ position: 'absolute', inset: '40px', background: 'linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.2))', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(255,255,255,0.3)', backdropFilter: 'blur(10px)' }}>
            <span style={{ color: '#0f172a', fontSize: '24px', fontWeight: '900' }}>π</span>
          </div>
        </motion.div>

        {/* Text */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          style={{ textAlign: 'center', padding: '0 48px', position: 'relative', zIndex: 10, marginTop: '32px' }}>
          <h2 style={{ color: '#0f172a', fontSize: '28px', fontWeight: '800', marginBottom: '12px' }}>Join PatternAI Today</h2>
          <p style={{ color: '#1e293b', fontSize: '15px', lineHeight: '1.7' }}>Unlock the power of mathematical pattern discovery</p>
        </motion.div>

        {/* Features */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}
          style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '32px', position: 'relative', zIndex: 10 }}>
          {['20+ Mathematical Pattern Types', '100% Detection Accuracy', 'Instant Formula Generation', 'Future Value Prediction'].map((f, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 + i * 0.1 }}
              style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ width: '24px', height: '24px', background: 'rgba(13,148,136,0.3)', border: '1px solid rgba(13,148,136,0.6)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <span style={{ color: '#0d9488', fontSize: '13px', fontWeight: '700' }}>✓</span>
              </div>
              <span style={{ color: 'rgba(15,32,39,0.75)', fontSize: '15px', fontWeight: '500' }}>{f}</span>
            </motion.div>
          ))}
        </motion.div>

      </div>
    </div>
  );
};

export default SignupPage;