import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { User, Mail, Calendar, Key, Save, CheckCircle2, AlertCircle } from "lucide-react";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

const ProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState("");
  
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: ""
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("patternai_token");
      if (!token) {
        window.location.href = "/login";
        return;
      }
      const res = await fetch("/api/user/profile", {
        headers: { "Authorization": `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) {
        setProfile(data.data);
        setFormData({
          full_name: data.data.full_name || "",
          email: data.data.email || "",
          password: ""
        });
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError("Failed to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccessMsg("");
    
    try {
      const token = localStorage.getItem("patternai_token");
      const payload = { full_name: formData.full_name, email: formData.email };
      if (formData.password) {
        payload.password = formData.password;
      }
      
      const res = await fetch("/api/user/profile", {
        method: "PUT",
        headers: { 
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      if (data.success) {
        setProfile(data.data);
        setSuccessMsg("Profile updated successfully!");
        setFormData(prev => ({ ...prev, password: "" }));
        
        // update name in local storage if present
        const user = JSON.parse(localStorage.getItem("patternai_user") || "{}");
        localStorage.setItem("patternai_user", JSON.stringify({ ...user, username: data.data.username, full_name: data.data.full_name }));
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError("Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar historyCount={JSON.parse(localStorage.getItem("patternai_history") || "[]").length} />

      {/* Header Area with Wave Background */}
      <div className="bg-hero-gradient pt-32 pb-40 relative">
         <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full blur-3xl translate-x-1/3 -translate-y-1/3"></div>
         <div className="max-w-4xl mx-auto px-6 relative z-10 flex flex-col items-center text-center">
           <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="mb-4">
             <div className="w-24 h-24 bg-white rounded-full mx-auto flex items-center justify-center shadow-2xl shadow-primary-500/20 text-primary-500 relative">
               <div className="absolute inset-0 rounded-full border-4 border-white opacity-20 scale-110"></div>
               <User size={44} strokeWidth={2.5} />
             </div>
           </motion.div>
           <motion.h1 initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="text-4xl md:text-5xl font-extrabold text-white mb-3 drop-shadow-md">
             {profile?.full_name || profile?.username || "Your Profile"}
           </motion.h1>
           <motion.p initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="text-primary-50 text-lg max-w-lg mx-auto">
             Manage your account settings, personal details, and security preferences.
           </motion.p>
         </div>
         
         {/* Wave Divider */}
         <div className="absolute bottom-0 left-0 right-0 w-full overflow-hidden leading-none z-0">
           <svg viewBox="0 0 1200 120" preserveAspectRatio="none" className="block w-full h-16 md:h-28">
             <path d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V120H0V95.8C52.16,93.4,103.9,82.8,155,71.2,209.61,58.74,265.4,66.86,321.39,56.44Z" fill="#f8fafc"></path>
           </svg>
         </div>
      </div>

      <div className="flex-1 max-w-4xl mx-auto w-full px-6 md:px-12 pb-20 -mt-16 relative z-20">

        {loading ? (
          <div className="text-center text-slate-500 py-20 bg-white rounded-3xl shadow-sm border border-slate-100">Loading profile data...</div>
        ) : profile ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-white rounded-3xl p-8 md:p-12 shadow-xl shadow-slate-200/40 border border-slate-100">
            
            {error && (
              <div className="mb-8 p-4 bg-red-50 text-red-600 rounded-xl border border-red-200 flex items-center gap-2 text-sm font-semibold">
                <AlertCircle size={18} /> {error}
              </div>
            )}
            
            {successMsg && (
              <div className="mb-8 p-4 bg-green-50 text-green-700 rounded-xl border border-green-200 flex items-center gap-2 text-sm font-semibold">
                <CheckCircle2 size={18} /> {successMsg}
              </div>
            )}
            
            <form onSubmit={handleSave} className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Username</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                      <User size={16} />
                    </div>
                    <input 
                      type="text" 
                      value={profile.username} 
                      disabled 
                      className="w-full bg-slate-50/70 border border-slate-200 rounded-xl py-3 pl-11 pr-4 text-slate-500 font-medium cursor-not-allowed" 
                    />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Username cannot be changed.</p>
                </div>
                
                <div>
                  <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Full Name</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                      <User size={16} />
                    </div>
                    <input 
                      type="text" 
                      value={formData.full_name} 
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                      className="w-full bg-white border border-slate-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-50 rounded-xl py-3 pl-11 pr-4 text-slate-700 font-medium transition-all outline-none" 
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                    <Mail size={16} />
                  </div>
                  <input 
                    type="email" 
                    value={formData.email} 
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full bg-white border border-slate-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-50 rounded-xl py-3 pl-11 pr-4 text-slate-700 font-medium transition-all outline-none" 
                  />
                </div>
              </div>

              <div className="pt-6 border-t border-slate-100">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Security</h3>
                <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Change Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                    <Key size={16} />
                  </div>
                  <input 
                    type="password" 
                    placeholder="Leave blank to keep current password"
                    value={formData.password} 
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="w-full bg-white border border-slate-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-50 rounded-xl py-3 pl-11 pr-4 text-slate-700 font-medium transition-all outline-none" 
                  />
                </div>
              </div>

              <div className="pt-8 flex justify-end">
                <button 
                  type="submit"
                  disabled={saving}
                  className="bg-primary-600 hover:bg-primary-700 disabled:bg-primary-300 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-all flex items-center gap-2"
                >
                  <Save size={18} /> {saving ? "Saving Changes..." : "Save Changes"}
                </button>
              </div>

            </form>
          </motion.div>
        ) : null}

        {profile && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mt-8 flex justify-center gap-6 text-sm text-slate-500">
            <div className="flex items-center gap-2"><Calendar size={14} /> Joined {new Date(profile.created_at).toLocaleDateString()}</div>
            {profile.last_login_at && (
              <div className="flex items-center gap-2"><CheckCircle2 size={14} /> Last Login: {new Date(profile.last_login_at).toLocaleDateString()}</div>
            )}
          </motion.div>
        )}

      </div>
      
      <Footer />
    </div>
  );
};

export default ProfilePage;
