import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-white pt-16 pb-8 text-slate-600 text-sm border-t border-slate-100">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-10 border-b border-slate-100 pb-12 mb-8">
          
          {/* Brand */}
          <div className="md:col-span-2">
            <Link to="/" className="flex items-center gap-2 mb-6 text-decoration-none">
              <div className="w-7 h-7 rounded bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center shadow-sm">
                <span className="text-white font-bold text-sm leading-none">P</span>
              </div>
              <span className="font-extrabold text-xl tracking-tight text-slate-900">
                Pattern<span className="text-primary-600">AI</span>
              </span>
            </Link>
            <p className="max-w-xs leading-relaxed mb-6 text-slate-500">
              Empowering data scientists and enthusiasts with advanced pattern recognition and predictive mathematical models.
            </p>
          </div>

          {/* Links */}
          <div>
            <h4 className="text-slate-900 font-bold mb-4 text-base">Company</h4>
            <ul className="flex flex-col gap-3">
              <li><a href="#" className="hover:text-primary-600 transition-colors">Home</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Product</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Marketplace</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-slate-900 font-bold mb-4 text-base">Product</h4>
            <ul className="flex flex-col gap-3">
              <li><a href="#" className="hover:text-primary-600 transition-colors">About</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Resources</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Pricing</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-slate-900 font-bold mb-4 text-base">Support</h4>
            <ul className="flex flex-col gap-3">
              <li><a href="#" className="hover:text-primary-600 transition-colors">Legal</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-primary-600 transition-colors">Contact</a></li>
            </ul>
          </div>

          {/* Newsletter */}
          <div className="md:col-span-5 lg:col-span-5 pt-8 border-t border-slate-100 mt-4 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="w-full md:w-auto">
              <h4 className="text-slate-900 font-bold mb-2 text-base">Newsletter</h4>
              <p className="mb-4 md:mb-0 text-slate-500">Subscribe for the latest updates and AI features.</p>
            </div>
            <div className="flex w-full md:w-80 bg-slate-50 rounded-xl p-1 border border-slate-200 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition-all">
              <input 
                type="email" 
                placeholder="Type email address" 
                className="bg-transparent border-none outline-none text-slate-700 px-4 py-2 w-full text-sm placeholder-slate-400"
              />
              <button className="bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-lg transition-colors flex items-center justify-center shadow-sm">
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
          
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-500">
          <p>Copyright © {new Date().getFullYear()} PatternAI. All rights reserved.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-primary-600 transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-primary-600 transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;