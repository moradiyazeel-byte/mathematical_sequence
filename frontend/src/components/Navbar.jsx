import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { User, ChevronDown, Menu, X } from "lucide-react";

const Navbar = ({ historyCount }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const isActive = (path) => location.pathname === path;

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled || mobileMenuOpen
          ? "bg-white/90 backdrop-blur-lg shadow-sm py-3"
          : "bg-transparent py-4 md:py-5"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-decoration-none z-50" onClick={() => setMobileMenuOpen(false)}>
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-lg leading-none">P</span>
          </div>
          <span
            className={`font-extrabold text-xl tracking-tight ${
              scrolled || mobileMenuOpen ? "text-slate-800" : "text-slate-900"
            }`}
          >
            Pattern<span className="text-primary-600">AI</span>
          </span>
        </Link>

        {/* Center Links - Desktop */}
        <div className="hidden md:flex items-center gap-8">
          <Link
            to="/"
            className={`font-semibold text-sm transition-colors ${
              isActive("/") ? "text-primary-700" : "text-slate-600 hover:text-primary-600"
            }`}
          >
            Home
          </Link>
          <Link
            to="/analyze"
            className={`font-semibold text-sm transition-colors ${
              isActive("/analyze") ? "text-primary-700" : "text-slate-600 hover:text-primary-600"
            }`}
          >
            Analyze
          </Link>
          <Link
            to="/history"
            className={`font-semibold text-sm transition-colors flex items-center gap-1.5 ${
              isActive("/history") ? "text-primary-700" : "text-slate-600 hover:text-primary-600"
            }`}
          >
            History
            {historyCount > 0 && (
              <span className="bg-primary-100 text-primary-700 text-[10px] px-1.5 py-0.5 rounded-full font-bold">
                {historyCount}
              </span>
            )}
          </Link>
          <Link
            to="/dashboard"
            className={`font-semibold text-sm transition-colors ${
              isActive("/dashboard") ? "text-primary-700" : "text-slate-600 hover:text-primary-600"
            }`}
          >
            Dashboard
          </Link>
        </div>

        {/* Right Auth / Profile - Desktop */}
        <div className="hidden md:flex items-center gap-4">
          {localStorage.getItem("patternai_token") ? (
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  localStorage.removeItem("patternai_token");
                  localStorage.removeItem("patternai_user");
                  localStorage.removeItem("patternai_history");
                  window.location.href = "/";
                }}
                className="text-sm font-semibold text-slate-600 hover:text-red-500 transition-colors"
              >
                Logout
              </button>
              <Link to="/profile" className="w-9 h-9 rounded-full bg-slate-100 flex items-center justify-center text-slate-400 border border-slate-200 hover:bg-primary-50 hover:text-primary-600 transition-colors cursor-pointer" title="Your Profile">
                <User size={18} />
              </Link>
            </div>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm font-bold text-slate-700 hover:text-primary-700 bg-white/50 backdrop-blur px-5 py-2 rounded-full transition-all"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="text-sm font-bold text-white bg-primary-500 hover:bg-primary-600 shadow-[0_4px_14px_0_rgba(20,184,166,0.39)] px-5 py-2 rounded-full transition-all hover:-translate-y-0.5"
              >
                Get Started
              </Link>
            </>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className="md:hidden z-50 p-2 -mr-2 text-slate-600"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu Dropdown */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden bg-white border-t border-slate-100 overflow-hidden"
          >
            <div className="flex flex-col px-6 py-6 gap-6">
              <Link to="/" className="font-semibold text-slate-700 hover:text-primary-600" onClick={() => setMobileMenuOpen(false)}>Home</Link>
              <Link to="/analyze" className="font-semibold text-slate-700 hover:text-primary-600" onClick={() => setMobileMenuOpen(false)}>Analyze</Link>
              <Link to="/history" className="font-semibold text-slate-700 hover:text-primary-600 flex justify-between" onClick={() => setMobileMenuOpen(false)}>
                History
                {historyCount > 0 && <span className="bg-primary-100 text-primary-700 text-xs px-2 py-0.5 rounded-full font-bold">{historyCount}</span>}
              </Link>
              <Link to="/dashboard" className="font-semibold text-slate-700 hover:text-primary-600" onClick={() => setMobileMenuOpen(false)}>Dashboard</Link>
              
              <Link to="/profile" className="font-semibold text-slate-700 hover:text-primary-600" onClick={() => setMobileMenuOpen(false)}>Profile</Link>
              
              <div className="h-px bg-slate-100 my-2"></div>
              
              {localStorage.getItem("patternai_token") ? (
                <button
                  onClick={() => {
                    localStorage.removeItem("patternai_token");
                    localStorage.removeItem("patternai_user");
                    localStorage.removeItem("patternai_history");
                    window.location.href = "/";
                  }}
                  className="font-semibold text-red-500 text-left"
                >
                  Logout
                </button>
              ) : (
                <div className="flex flex-col gap-4">
                  <Link to="/login" className="font-bold text-center text-slate-700 bg-slate-100 py-3 rounded-xl" onClick={() => setMobileMenuOpen(false)}>
                    Sign In
                  </Link>
                  <Link to="/signup" className="font-bold text-center text-white bg-primary-500 py-3 rounded-xl shadow-lg shadow-primary-500/30" onClick={() => setMobileMenuOpen(false)}>
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default Navbar;